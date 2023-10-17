from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from pytest_mock import MockerFixture

from chat.models import ChatRoom, Message


@pytest.mark.django_db
# Despite ability to create message with empty or white characters string,
# this should be forbidden for user through user GUI.
@pytest.mark.parametrize(
    "content", ("", " ", "test message content", "How are you?")
)
def test_message_creation(
    mocker: MockerFixture, user: User, room: ChatRoom, content: str
):
    mocker.patch.object(
        timezone,
        "now",
        return_value=timezone.make_aware(datetime(2023, 9, 28, 14, 16)),
    )

    message = Message.objects.create(author=user, room=room, content=content)
    message.unread_by.add(user)

    assert message.author == user
    assert message.room == room
    assert message.content == content
    assert message.timestamp == timezone.now()
    assert list(message.unread_by.all()) == [user]


@pytest.mark.django_db
def test_create_message_missing_author(room: ChatRoom):
    with pytest.raises(Exception):
        Message.objects.create(room=room, content="Test message")


@pytest.mark.django_db
def test_create_message_missing_room(user: User):
    with pytest.raises(Exception):
        Message.objects.create(author=user, content="Test message")


@pytest.mark.django_db
def test_message_str(user: User, room: ChatRoom):
    message = Message.objects.create(
        author=user, room=room, content="Test message"
    )

    message_str = str(message)

    assert message_str == "test-user: Test message"
