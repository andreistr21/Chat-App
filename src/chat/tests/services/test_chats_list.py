from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from pytest_mock import MockerFixture

from chat.models import ChatRoom, Message
from chat.services import chats_list


def _create_room(admin: User, room_name: str | None) -> ChatRoom:
    return ChatRoom.objects.create(admin=admin, room_name=room_name)


def _create_message(author: User, room: ChatRoom) -> Message:
    return Message.objects.create(
        author=author, room=room, content="Message test content"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("room_name", "get_3_members", "last_msg", "is_current_room_id"),
    (
        ("room name", None, True, False),
        (None, "member1, member2, member3", True, False),
        (None, "member1, member2, member3", False, True),
    ),
)
def test_return_values_single_room(
    mocker: MockerFixture,
    user: User,
    room_name: str | None,
    get_3_members: str | None,
    last_msg: bool,
    is_current_room_id: bool,
):
    room = _create_room(user, room_name)
    message = _create_message(user, room) if last_msg else None
    mocker.patch("chat.services.get_last_message", return_value=message)
    mocker.patch("chat.services.get_3_members", return_value=get_3_members)
    expected_unread_msgs = 1 if is_current_room_id else 0
    mocker.patch(
        "chat.services.count_unread_msgs",
        return_value=expected_unread_msgs,
    )
    chat_rooms = user.admin.all()

    chats_info = chats_list(
        chat_rooms, user, str(room.id) if is_current_room_id else ""
    )

    expected_chats_info = [
        (
            room.id,
            room.room_name or get_3_members,
            message,
            expected_unread_msgs,
        )
    ]
    assert chats_info == expected_chats_info


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("room_name", "get_3_members", "message_1_none"),
    (
        ("room name", None, False),
        (None, "member1, member2, member3", True),
    ),
)
def test_return_values_4_rooms(
    mocker: MockerFixture,
    user: User,
    room_name: str | None,
    get_3_members: str | None,
    message_1_none: bool,
):
    dates = (
        # For room creation
        timezone.make_aware(datetime(2023, 10, 4, 1, 1, 1)),
        timezone.make_aware(datetime(2000, 1, 1, 1, 1, 1)),  # Not important
        timezone.make_aware(datetime(2000, 1, 1, 1, 1, 1)),  # Not important
        timezone.make_aware(datetime(2000, 1, 1, 1, 1, 1)),  # Not important
        # For messages creation
        timezone.make_aware(datetime(2023, 10, 2, 1, 1, 1)),
        timezone.make_aware(datetime(2023, 10, 3, 1, 1, 1)),
        timezone.make_aware(datetime(2023, 10, 5, 1, 1, 1)),
        timezone.make_aware(datetime(2023, 10, 6, 1, 1, 1)),
    )
    mocker.patch.object(timezone, "now", side_effect=dates)
    room1 = _create_room(user, room_name)
    room2 = _create_room(user, room_name)
    room3 = _create_room(user, room_name)
    room4 = _create_room(user, room_name)
    message1 = None if message_1_none else _create_message(user, room1)
    # If message1 is not created, we need manually get value from timezone.now,
    # so order will remain the same.
    # sourcery skip: no-conditionals-in-tests
    if message_1_none:
        timezone.now()
    message2 = _create_message(user, room1)
    message3 = _create_message(user, room3)
    message4 = _create_message(user, room4)
    messages = (message1, message2, message3, message4)
    mocker.patch("chat.services.get_last_message", side_effect=messages)
    mocker.patch("chat.services.get_3_members", return_value=get_3_members)
    mocker.patch(
        "chat.services.count_unread_msgs",
        side_effect=[3, 4, 1, 2],
    )
    chat_rooms = user.admin.all()

    chats_info = chats_list(chat_rooms, user)

    # sourcery skip: no-conditionals-in-tests
    if message_1_none:
        expected_chats_info = [
            (room4.id, room4.room_name or get_3_members, message4, 2),
            (room3.id, room3.room_name or get_3_members, message3, 1),
            (room1.id, room1.room_name or get_3_members, message1, 3),
            (room2.id, room2.room_name or get_3_members, message2, 4),
        ]
    else:
        expected_chats_info = [
            (room4.id, room4.room_name or get_3_members, message4, 2),
            (room3.id, room3.room_name or get_3_members, message3, 1),
            (room2.id, room2.room_name or get_3_members, message2, 4),
            (room1.id, room1.room_name or get_3_members, message1, 3),
        ]
    assert chats_info == expected_chats_info
