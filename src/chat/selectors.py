from typing import Any, List
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.db.transaction import atomic

from chat.models import ChatRoom, Message
from chat.redis import get_redis_connection
from chat.utils import construct_name_of_redis_list_for_channel_name


def get_last_20_messages(
    room_id_str: str, username: str
) -> List[Message] | None:
    """
    Returns last 20 messages in room and removes them from unread table.
    """
    room_id_UUID = UUID(room_id_str)
    with atomic():
        messages = list(
            Message.objects.filter(room=room_id_UUID).order_by("-timestamp")[
                :20
            ][::-1]
        )

        user = get_user(username)
        if user is not None:
            for message in messages:
                message.unread_by.remove(user)

    return None if user is None else messages


def get_user(username: str) -> User | None:
    """
    Returns User object or None if don't exists.
    """
    return get_user_model().objects.filter(username=username).first()


def get_room(room_id: str) -> ChatRoom | None:
    """
    Returns room object or None if don't exists.
    """
    return ChatRoom.objects.filter(id=room_id).first()


def get_user_chats(user: User) -> QuerySet[ChatRoom]:
    """
    Returns all chats in which the user is a member.
    """
    return user.chat_rooms.all()


def get_3_members(room_obj: ChatRoom) -> str:
    """
    Returns first 3 or less, if don't exists, members of room as a string or empty string.
    """
    return ", ".join(room_obj.members.values_list("username", flat=True)[:3])


def get_last_message(chat_room: ChatRoom) -> Message | None:
    """
    Returns last message of the chat or empty string.
    """
    return chat_room.message.order_by("-timestamp").first()


def get_users_channels(
    chat_members: list[User] | QuerySet[User],
) -> list[list[Any | bytes]]:
    """
    Retrieves all channels names for user in one transaction and returns them.
    """
    redis_connection = get_redis_connection()
    with redis_connection.pipeline() as redis_pipeline:
        for user_obj in chat_members:
            redis_pipeline.lrange(
                construct_name_of_redis_list_for_channel_name(user_obj.pk),
                0,
                -1,
            )

        return redis_pipeline.execute()


def get_chat_members(room_obj: ChatRoom) -> QuerySet[User]:
    """
    Returns all chat members.
    """
    return room_obj.members.all()


def is_chat_member(user_id: int, room_id: str) -> bool:
    """
    Returns True if user is a member of chat room, False otherwise.
    """
    if room := get_room(room_id):
        return room.members.filter(id=user_id).exists()
    return False
