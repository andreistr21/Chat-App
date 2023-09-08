from typing import List, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url

from chat.models import ChatRoom
from chat.redis import get_redis_connection
from chat.selectors import get_3_members, get_last_message, get_room
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

    return sorted(chats_and_msgs, key=lambda el: el[2].timestamp, reverse=True)  # type: ignore


def get_room_or_redirect(room_id: str) -> ChatRoom | HttpResponseRedirect:
    if room_obj := get_room(room_id):
        return room_obj
    return redirect(resolve_url(settings.CHATS_URL), permanent=False)


def save_channel_name(user_id: str, channel_name: str) -> None:
    """
    Appends redis list from the head with channel name.
    """
    redis_connection = get_redis_connection()
    redis_connection.lpush(
        construct_name_of_redis_list_for_channel_name(user_id), channel_name
    )


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
