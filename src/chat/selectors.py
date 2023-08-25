from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import QuerySet

from chat.models import ChatRoom, Message


def last_20_messages(room_id: str) -> List[Message]:
    return Message.objects.filter(room=room_id).order_by("-timestamp")[:20][::-1]  # type: ignore


def get_author(username: str) -> User:
    return get_user_model().objects.get(username=username)  # type: ignore


def get_room(room_id: str) -> ChatRoom:
    return ChatRoom.objects.get(id=room_id)
