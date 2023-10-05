from unittest.mock import Mock

import pytest
from django.http import HttpResponseRedirect
from pytest_mock import MockerFixture

from chat.decorators import chat_membership


@pytest.fixture
def mock_is_chat_member(mocker: MockerFixture) -> Mock:
    return mocker.patch("chat.decorators.is_chat_member")


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
    mock_is_chat_member: Mock,
    mock_request: Mock,
    mock_user: Mock,
    mock_view_func: Mock,
):
    room_id = "room1"
    mock_is_chat_member.return_value = True
    mock_request.user = mock_user

    result = chat_membership(mock_view_func)(mock_request, room_id)

    assert not isinstance(result, HttpResponseRedirect)
    mock_view_func.assert_called_once_with(mock_request, room_id)


def test_redirect(
    mock_is_chat_member: Mock,
    mock_request: Mock,
    mock_user: Mock,
    mock_view_func: Mock,
    mock_redirect: Mock,
    mock_resolve_url: Mock,
):
    mock_is_chat_member.return_value = False

    mock_request.user = mock_user
    mock_redirect.return_value = mock_redirect

    result = chat_membership(mock_view_func)(
        mock_request,
        "unexistent-room",
    )

    assert isinstance(result, HttpResponseRedirect)
    mock_redirect.assert_called_once_with(
        mock_resolve_url.return_value, permanent=False
    )
