from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import QuerySet

from chat.models import ChatRoom, Message


def last_20_messages(room_id: str) -> List[Message]:
    return Message.objects.filter(room=room_id).order_by("-timestamp")[:20][::-1]  # type: ignore


def get_author(username: str) -> User:
    return get_user_model().objects.get(username=username)  # type: ignore


def get_room(room_id: str) -> ChatRoom | None:
    return ChatRoom.objects.filter(id=room_id).first()


def get_user_chats(user: User) -> QuerySet[ChatRoom]:
    return user.chat_rooms.all()  # type: ignore


def get_3_members(room_obj: ChatRoom) -> str:
    return ", ".join(room_obj.members.values_list("username", flat=True)[:3])


def get_last_message(chat_room: ChatRoom) -> str:
    return chat_room.message.order_by("-timestamp").values_list( # type: ignore
        "content", flat=True
    )[0]
