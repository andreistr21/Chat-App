import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom
from chat.selectors import get_3_members
from django.contrib.auth import get_user_model


def _create_room(admin: User) -> ChatRoom:
    return ChatRoom.objects.create(admin=admin)


def _get_room(admin: User, num_members: int) -> ChatRoom:
    """
    Creates room object and adds members to it.
    """
    room = _create_room(admin)

    for i in range(num_members):
        room.members.add(
            get_user_model().objects.create(
                username=f"test-user{i}", password="test-password"
            )
        )

    return room


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("num_members", "expected_to_return_num_members"),
    ((0, 0), (1, 1), (2, 2), (3, 3), (4, 3), (5, 3), (10, 3), (30, 3)),
)
def test_returns_num_members(
    user: User, num_members: int, expected_to_return_num_members: int
):
    room = _get_room(user, num_members)
    members = get_3_members(room)

    members_len = len(members.split(", ")) if len(members) > 0 else 0

    assert members_len == expected_to_return_num_members


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("num_members", "expected_to_return_num_members"),
    ((0, 0), (1, 1), (2, 2), (3, 3), (4, 3), (5, 3), (10, 3), (30, 3)),
)
def test_returns_str(
    user: User, num_members: int, expected_to_return_num_members: int
):
    room = _get_room(user, num_members)
    members = get_3_members(room)
    
    assert isinstance(members, str)
