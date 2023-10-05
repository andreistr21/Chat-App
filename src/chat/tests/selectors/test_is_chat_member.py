import pytest
from django.contrib.auth.models import User
from pytest_mock import MockerFixture

from chat.models import ChatRoom
from chat.selectors import is_chat_member
from chat.tests.services import multiple_users_generator


def _add_users_to_room(num_members: int, room: ChatRoom) -> list[User]:
    multiple_users = multiple_users_generator()
    users = []
    for _ in range(num_members):
        user = next(multiple_users)
        room.members.add(user)
        users.append(user)

    return users


@pytest.mark.django_db
@pytest.mark.parametrize(
    "num_members",
    (1, 2, 3),
)
def test_if_room_exists_user_is_member(
    mocker: MockerFixture,
    room_no_members: ChatRoom,
    num_members: int,
):
    mocker.patch("chat.selectors.get_room", return_value=room_no_members)

    users = _add_users_to_room(num_members, room_no_members)

    is_member = is_chat_member(users[0].id, str(room_no_members.id))

    assert is_member


@pytest.mark.django_db
@pytest.mark.parametrize(
    "num_members",
    (1, 2, 3),
)
def test_if_room_doesnt_exists_user_is_member(
    mocker: MockerFixture,
    room_no_members: ChatRoom,
    num_members: int,
):
    mocker.patch("chat.selectors.get_room", return_value=None)

    users = _add_users_to_room(num_members, room_no_members)

    is_member = is_chat_member(users[0].id, str(room_no_members.id))

    assert not is_member


@pytest.mark.django_db
@pytest.mark.parametrize("num_members", (0, 1, 2, 3))
def test_if_room_exists_user_is_not_member(
    mocker: MockerFixture,
    user: User,
    room_no_members: ChatRoom,
    num_members: int,
):
    mocker.patch("chat.selectors.get_room", return_value=room_no_members)

    _add_users_to_room(num_members, room_no_members)

    is_member = is_chat_member(user.id, str(room_no_members.id))

    assert not is_member


@pytest.mark.django_db
@pytest.mark.parametrize("num_members", (0, 1, 2, 3))
def test_if_room_doesnt_exists_user_is_not_member(
    mocker: MockerFixture,
    user: User,
    room_no_members: ChatRoom,
    num_members: int,
):
    mocker.patch("chat.selectors.get_room", return_value=None)

    _add_users_to_room(num_members, room_no_members)

    is_member = is_chat_member(user.id, str(room_no_members.id))

    assert not is_member
