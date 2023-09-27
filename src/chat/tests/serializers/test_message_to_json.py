import datetime

import pytest
from django.utils import timezone
from pytest_mock import MockerFixture

from chat.models import ChatRoom, Message
from chat.serializers import message_to_json
from conftest import TEST_USERNAME

TEST_MESSAGE_CONTENT = "test message content"


def _message(room: ChatRoom) -> Message:
    return Message.objects.create(
        author=room.admin, room=room, content=TEST_MESSAGE_CONTENT
    )


@pytest.mark.django_db
def test_return_values(room: ChatRoom, mocker: MockerFixture):
    mocker.patch.object(
        timezone,
        "now",
        return_value=timezone.make_aware(
            datetime.datetime(2023, 9, 27, 13, 55)
        ),
    )
    message = _message(room)

    expected_json = {
        "author": TEST_USERNAME,
        "content": TEST_MESSAGE_CONTENT,
        "timestamp": str(timezone.now()),
    }

    json = message_to_json(message)

    assert json == expected_json
