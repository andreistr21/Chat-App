from unittest.mock import Mock

import pytest
from django.http import HttpResponseRedirect
from pytest_mock import MockerFixture

from chat.decorators import chat_membership
from chat.models import ChatRoom


@pytest.fixture
def mock_get_room(mocker: MockerFixture) -> Mock:
    return mocker.patch("chat.decorators.get_room")


@pytest.fixture
def mock_room_obj(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=ChatRoom)


@pytest.fixture
def mock_request(mocker: MockerFixture) -> Mock:
    return mocker.Mock()


@pytest.fixture
def mock_user(mocker: MockerFixture) -> Mock:
    return mocker.Mock()


@pytest.fixture
def mock_view_func(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def mock_redirect(mocker: MockerFixture):
    return mocker.patch("chat.decorators.redirect", spec=HttpResponseRedirect)


@pytest.fixture
def mock_resolve_url(mocker: MockerFixture):
    return mocker.patch("chat.decorators.resolve_url")


def test_allow_access(
    mock_get_room: Mock,
    mock_room_obj: Mock,
    mock_request: Mock,
    mock_user: Mock,
    mock_view_func: Mock,
):
    room_id = "room1"
    mock_get_room.return_value = mock_room_obj
    mock_room_obj.members.filter.return_value.exists.return_value = True
    mock_request.user = mock_user

    result = chat_membership(mock_view_func)(mock_request, room_id)

    assert not isinstance(result, HttpResponseRedirect)
    mock_view_func.assert_called_once_with(mock_request, room_id)


@pytest.mark.parametrize(
    ("room_id", "room_exists", "user_belongs"),
    (
        # Room doesn't exists
        ("unexistent-room", False, False),
        # User doesn't belongs to room
        ("room", True, False),
    ),
)
def test_redirect(
    mock_get_room: Mock,
    mock_room_obj: Mock,
    mock_request: Mock,
    mock_user: Mock,
    mock_view_func: Mock,
    mock_redirect: Mock,
    mock_resolve_url: Mock,
    room_id: str,
    room_exists: bool,
    user_belongs: bool,
):
    # sourcery skip: no-conditionals-in-tests
    if room_exists:
        mock_get_room.return_value = mock_room_obj
        mock_room_obj.members.filter.return_value.exists.return_value = (
            user_belongs
        )
    else:
        mock_get_room.return_value = room_exists

    mock_request.user = mock_user
    mock_redirect.return_value = mock_redirect

    result = chat_membership(mock_view_func)(mock_request, room_id)

    assert isinstance(result, HttpResponseRedirect)
    mock_redirect.assert_called_once_with(
        mock_resolve_url.return_value, permanent=False
    )
