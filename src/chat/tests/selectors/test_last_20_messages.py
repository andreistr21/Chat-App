from time import sleep
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User
from pytest_mock import MockerFixture

from chat.models import ChatRoom, Message
from chat.selectors import get_last_20_messages


@pytest.fixture
def get_user_mock(mocker: MockerFixture, user: User):
    return mocker.patch("chat.selectors.get_user", return_value=user)


def _create_room(user_obj: User) -> ChatRoom:
    chat_room = ChatRoom.objects.create(admin=user_obj)
    chat_room.members.add(user_obj)
    return chat_room


def _get_chat_room(user: User, num_messages: int, unread=False):
    """
    Creates user and room objects, and appends room with specified number of
    messages.
    """
    room_obj = _create_room(user)
    for i in range(num_messages):
        msg = Message.objects.create(
            author=user, room=room_obj, content=str(i)
        )
        if unread:
            msg.unread_by.add(user)
        # Necessary for difference in timestamps
        sleep(0.0001)

    return room_obj


@pytest.mark.parametrize(
    ["num_messages", "expected_num_messages"],
    [
        (0, 0),
        (1, 1),
        (5, 5),
        (19, 19),
        (20, 20),
        (21, 20),
        (30, 20),
        (50, 20),
    ],
)
@pytest.mark.django_db
def test_num_returned_items(
    get_user_mock: Mock,
    num_messages: int,
    expected_num_messages: int,
    user: User,
) -> None:
    """
    Tests if number of returned items muches expected number.
    """
    room_obj = _get_chat_room(user, num_messages)
    messages = get_last_20_messages(str(room_obj.id), user.username)

    assert len(messages) == expected_num_messages  # type: ignore


@pytest.mark.parametrize(
    "num_messages",
    [0, 1, 5, 19, 20, 21, 30, 50],
)
@pytest.mark.django_db
def test_order_returned_items(
    get_user_mock: Mock, num_messages: int, user: User
) -> None:
    room_obj = _get_chat_room(user, num_messages)
    messages = get_last_20_messages(str(room_obj.id), user.username)

    expected_messages = list(
        room_obj.message.order_by("-timestamp")[:20][::-1]
    )

    assert messages == expected_messages


@pytest.mark.django_db
def test_msgs_mark_as_read(get_user_mock: Mock, user: User) -> None:
    room_obj = _get_chat_room(user, 20, True)

    _ = get_last_20_messages(str(room_obj.id), user.username)

    expected_messages: list[Message] = list(
        room_obj.message.order_by("-timestamp")[:20][::-1]
    )

    unread = []
    for msg in expected_messages:
        unread.append(msg.unread_by.all().exists())

    assert True not in unread


@pytest.mark.django_db
def test_none_returned(get_user_mock: Mock, user: User) -> None:
    """
    Tests if no user found. M2M relations will still exists.
    """
    get_user_mock.return_value = None
    room_obj = _get_chat_room(user, 20, True)

    _ = get_last_20_messages(str(room_obj.id), user.username)

    expected_messages: list[Message] = list(
        room_obj.message.order_by("-timestamp")[:20][::-1]
    )

    unread = []
    for msg in expected_messages:
        unread.append(msg.unread_by.all().exists())

    assert False not in unread
