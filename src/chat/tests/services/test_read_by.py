from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import make_aware
from pytest_mock import MockerFixture

from chat.models import ChatRoom, Message
from chat.services import read_by


@pytest.mark.django_db
def test_with_same_author(mocker: MockerFixture, user: User):
    parse_datetime_mocked = mocker.patch("chat.services.parse_datetime")
    message = {
        "author": user.username,
        "content": "test message content",
        "timestamp": str(make_aware(datetime(2023, 10, 17, 1, 1, 1, 1))),
    }

    read_by(message, user)

    parse_datetime_mocked.assert_not_called()


@pytest.mark.django_db
def test_invalid_date(mocker: MockerFixture, user: User):
    mocker.patch(
        "chat.services.parse_datetime",
        return_value=None,
    )
    message_filter_mocked = mocker.patch.object(Message.objects, "filter")
    message = {
        "author": user.username + "f",
        "content": "test message content",
        "timestamp": str(make_aware(datetime(2023, 10, 17))),
    }

    read_by(message, user)

    message_filter_mocked.assert_not_called()


@pytest.mark.django_db
def test_marked_read(mocker: MockerFixture, user: User, room: ChatRoom):
    date = make_aware(datetime(2023, 10, 17))
    message = {
        "author": user.username + "f",
        "content": "test message content",
        "timestamp": str(date),
    }
    mocker.patch.object(timezone, "now", return_value=date)
    message_obj = Message.objects.create(
        author=user, room=room, timestamp=date, content="test message content"
    )
    message_obj.unread_by.add(user)

    read_by(message, user)

    assert not message_obj.unread_by.all().exists()
