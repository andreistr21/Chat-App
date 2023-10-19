from time import sleep
from uuid import uuid4

import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom, Message
from chat.selectors import count_unread_msgs


def _add_unread_messages(user: User, room_obj: ChatRoom, num_messages: int):
    for i in range(num_messages):
        msg = Message.objects.create(
            author=user, room=room_obj, content=str(i)
        )
        msg.unread_by.add(user)
        # Necessary for difference in timestamps
        sleep(0.0001)


@pytest.mark.django_db
def test_room_is_current_page_room(user: User, room: ChatRoom):
    num_unread_msgs = count_unread_msgs(room, user, str(room.id))

    assert num_unread_msgs == 0


@pytest.mark.parametrize("num_messages", [0, 1, 10, 50])
@pytest.mark.django_db
def test_return_unread_msgs(user: User, room: ChatRoom, num_messages: int):
    _add_unread_messages(user, room, num_messages)

    num_unread_msgs = count_unread_msgs(room, user, str(uuid4()))

    assert num_unread_msgs == num_messages


@pytest.mark.django_db
def test_no_room_msgs(user: User, room: ChatRoom):
    num_unread_msgs = count_unread_msgs(room, user, str(uuid4()))

    assert num_unread_msgs == 0
