import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom


@pytest.mark.django_db
@pytest.mark.parametrize("chat_name", ("", "room1", "room 2", "Test-Room-3"))
def test_create_chat_room(user: User, chat_name: str):
    chat_room = ChatRoom.objects.create(admin=user, room_name=chat_name)

    assert chat_room.admin == user
    assert chat_room.room_name == chat_name


@pytest.mark.django_db
def test_create_chat_room_without_name(user: User):
    chat_room = ChatRoom.objects.create(admin=user)

    assert chat_room.admin == user
    assert chat_room.room_name is None


@pytest.mark.django_db
# Despite the ability to set room name as white characters string, this should
# be forbidden for the user through GUI.
@pytest.mark.parametrize("chat_name", (" ", "room1", "room 2", "Test-Room-3"))
def test_chat_room_str(user: User, chat_name: str):
    chat_room = ChatRoom.objects.create(admin=user, room_name=chat_name)

    chat_room_str = str(chat_room)

    assert chat_room_str == chat_room.room_name


@pytest.mark.django_db
@pytest.mark.parametrize("chat_name", ("", None))
def test_chat_room_str_empty_name(user: User, chat_name: str | None):
    chat_room = ChatRoom.objects.create(admin=user, room_name=chat_name)

    chat_room_str = str(chat_room)

    assert chat_room_str == str(chat_room.id)
