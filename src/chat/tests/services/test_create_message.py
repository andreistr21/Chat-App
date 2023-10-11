import pytest
from django.contrib.auth.models import User
from chat.models import ChatRoom

from chat.services import create_message


@pytest.mark.django_db
def test_create_message(user: User, room: ChatRoom):
    create_message(user, room, "test message content")

    assert len(user.author.all()) == 1


@pytest.mark.django_db
def test_create_message_with_same_user_and_room(user: User, room: ChatRoom):
    create_message(user, room, "test message content")
    create_message(user, room, "test message content")

    assert len(user.author.all()) == 2
