from typing import Any, List, Optional, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import QuerySet

from chat.models import ChatRoom, Message
from chat.redis import get_redis_connection
from chat.utils import construct_name_of_redis_list_for_channel_name


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


def get_last_message(chat_room: ChatRoom) -> Message:
    """
    Returns last message of the chat.
    """
    return chat_room.message.order_by("-timestamp")[0]  # type: ignore


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
