from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from pytest_mock import MockerFixture
from django.contrib.auth.models import User

from chat.models import ChatRoom, Message
from chat.serializers import messages_to_json
from conftest import TEST_PASSWORD, TEST_USERNAME

TEST_MESSAGE_CONTENT = "test message content"


def _create_user(username_postfix: str | int) -> User:
    return get_user_model().objects.create(
        username=f"{TEST_USERNAME}-{username_postfix}", password=TEST_PASSWORD
    )


def _create_room(user: User) -> ChatRoom:
    return ChatRoom.objects.create(
        admin=user,
    )


def _create_message(user: User, room: ChatRoom) -> Message:
    return Message.objects.create(
        author=user, room=room, content=TEST_MESSAGE_CONTENT
    )


def _create_messages(num_messages: int) -> list[Message]:
    messages = []
    for i in range(num_messages):
        user = _create_user(i)
        room = _create_room(user)
        message = _create_message(user, room)
        messages.append(message)

    return messages


def _message_to_json(message: Message) -> dict[str, str]:
    return {
        "author": message.author.username,
        "content": message.content,
        "timestamp": str(message.timestamp),
    }


def _messages_to_json(messages: list[Message]) -> list[dict[str, str]]:
    return [_message_to_json(message) for message in messages]


@pytest.mark.django_db
@pytest.mark.parametrize("num_messages", (0, 1, 2, 5, 10, 30, 100))
def test_return_values(mocker: MockerFixture, num_messages: int):
    mocker.patch.object(
        timezone,
        "now",
        return_value=timezone.make_aware(datetime(2023, 9, 27, 13, 55)),
    )
    messages = _create_messages(num_messages)
    expected_messages_json = _messages_to_json(messages)

    messages_json = messages_to_json(messages)

    assert messages_json == expected_messages_json
