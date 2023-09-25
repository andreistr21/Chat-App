from typing import List, Tuple

from django.conf import settings
from django.db.models import QuerySet
from datetime import datetime
from django.utils.timezone import make_aware

from chat.models import ChatRoom
from chat.redis import get_redis_connection
from chat.selectors import get_3_members, get_last_message
from chat.utils import construct_name_of_redis_list_for_channel_name


def chats_list(
    chat_rooms: QuerySet[ChatRoom],
) -> List[Tuple[str, str, str]]:
    """
    Retrieves chat rooms id, name, last message object, mappers it together,
    sorts by last message and returns.
    """
    chats_and_msgs = []
    for chat_room in chat_rooms:
        room_id = chat_room.id
        room_name = chat_room.room_name or get_3_members(chat_room)
        room_last_msg = get_last_message(chat_room)

        chats_and_msgs.append((room_id, room_name, room_last_msg))

    # TODO: Substitute 2000-01-01 with chat date creation
    return sorted(chats_and_msgs, key=lambda el: (el[2].timestamp if el[2] is not None else make_aware(datetime(2000, 1, 1, 0, 0, 0))), reverse=True)  # type: ignore


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
