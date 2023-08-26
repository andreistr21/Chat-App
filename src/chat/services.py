from typing import List, Tuple
from django.db.models import QuerySet

from chat.models import ChatRoom
from chat.selectors import get_3_members, get_last_message


def chats_list(
    chat_rooms: QuerySet[ChatRoom],
) -> List[Tuple[str, str, str]]:
    """Retrieves chat rooms id, name and last message, and mappers it together"""
    chats_and_msgs = []
    for chat_room in chat_rooms:
        room_id = chat_room.id
        room_name = chat_room.room_name or get_3_members(chat_room)
        room_last_msg = get_last_message(chat_room)

        chats_and_msgs.append((room_id, room_name, room_last_msg))

    return chats_and_msgs
