from typing import List, Tuple
from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.utils.dateparse import parse_datetime

from chat.models import ChatRoom, Message
from chat.redis import get_redis_connection
from chat.selectors import get_3_members, get_last_message
from chat.utils import construct_name_of_redis_list_for_channel_name


def chats_list(
    chat_rooms: QuerySet[ChatRoom],
) -> List[Tuple[UUID, str, Message | None]]:
    """
    Retrieves chat rooms id, name, last message object, mappers it together,
    sorts by last message or chat creation and returns.
    """
    chats_and_msgs = []
    for chat_room in chat_rooms:
        room_id = chat_room.id
        room_name = chat_room.room_name or get_3_members(chat_room)
        room_last_msg = get_last_message(chat_room)

        chats_and_msgs.append((room_id, room_name, room_last_msg))

    return sorted(
        chats_and_msgs,
        key=lambda el: (
            el[2].timestamp
            if el[2] is not None
            else chat_rooms[chats_and_msgs.index(el)].created
        ),
        reverse=True,
    )


def save_channel_name(user_id: str, channel_name: str) -> None:
    """
    Appends redis list from the head with channel name and updates TTL.
    """
    redis_connection = get_redis_connection()
    redis_key_name = construct_name_of_redis_list_for_channel_name(user_id)
    with redis_connection.pipeline() as redis_pipeline:
        redis_pipeline.lpush(
            redis_key_name,
            channel_name,
        )
        redis_pipeline.expire(
            redis_key_name, settings.USERS_CHANNELS_NAMES_TTL
        )

        redis_pipeline.execute()


def remove_channel_name(user_id: str, channel_name: str) -> None:
    """
    Removes specified element from redis list.
    """
    redis_connection = get_redis_connection()
    redis_connection.lrem(
        construct_name_of_redis_list_for_channel_name(user_id),
        -1,
        channel_name,
    )


def create_message(
    author_obj: User, room_obj: ChatRoom, msg_content: str
) -> Message:
    """
    Creates message, adds all members, with author as exception, to unread_by
    table, and returns message.
    """
    with atomic():
        message = Message.objects.create(
            author=author_obj, content=msg_content, room=room_obj
        )
        unread_by_users = room_obj.members.exclude(id=author_obj.id)
        message.unread_by.add(*unread_by_users)

    return message


# TODO: Add tests
def read_by(message: dict, user: User) -> None:
    """
    Marks message as read by user.
    """
    # If this user is author, it is already marked as read by him.
    if message["author"] == user.username:
        return None

    date = parse_datetime(message["timestamp"])
    if not date:
        return None
    message_obj = Message.objects.filter(
        timestamp=date,
        content=message["content"],
    ).first()

    if message_obj:
        message_obj.unread_by.remove(user)
