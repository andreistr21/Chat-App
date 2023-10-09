from time import sleep

import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom, Message
from chat.selectors import last_20_messages


def _create_room(user_obj: User) -> ChatRoom:
    chat_room = ChatRoom.objects.create(admin=user_obj)
    chat_room.members.add(user_obj)
    return chat_room


def _get_chat_room(user, num_messages: int):
    """
    Creates user and room objects, and appends room with specified number of
    messages.
    """
    room_obj = _create_room(user)
    for i in range(num_messages):
        Message.objects.create(author=user, room=room_obj, content=str(i))
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
def test_num_returned_items(num_messages, expected_num_messages, user) -> None:
    """
    Tests if number of returned items muches expected number.
    """
    room_obj = _get_chat_room(user, num_messages)
    messages = last_20_messages(str(room_obj.id))

    assert len(messages) == expected_num_messages


@pytest.mark.parametrize(
    "num_messages",
    [0, 1, 5, 19, 20, 21, 30, 50],
)
@pytest.mark.django_db
def test_order_returned_items(num_messages, user) -> None:
    room_obj = _get_chat_room(user, num_messages)
    messages = last_20_messages(str(room_obj.id))

    expected_messages = list(room_obj.message.order_by("-timestamp")[:20][::-1])

    assert messages == expected_messages
