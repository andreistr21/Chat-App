import pytest
from django.contrib.auth.models import User
from chat.models import ChatRoom

from chat.services import create_message
from chat.tests.services import multiple_users_generator


@pytest.mark.django_db
def test_create_message(user: User, room: ChatRoom):
    multiple_users = multiple_users_generator()
    users = []
    for _ in range(3):
        next_user = next(multiple_users)
        room.members.add(next_user)
        users.append(next_user)

    message = create_message(user, room, "test message content")

    assert len(user.author.all()) == 1
    assert message.author == user
    assert message.room == room
    assert message.content == "test message content"
    assert list(message.unread_by.all()) == users


@pytest.mark.django_db
def test_create_message_with_same_user_and_room(user: User, room: ChatRoom):
    create_message(user, room, "test message content")
    create_message(user, room, "test message content")

    assert len(user.author.all()) == 2
