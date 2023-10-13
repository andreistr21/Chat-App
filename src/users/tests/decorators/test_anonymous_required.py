from unittest.mock import Mock

import pytest
from django.conf import settings
from django.http import HttpResponseRedirect
from pytest_mock import MockerFixture

from users.decorators import anonymous_required


def test_allowed_access(mocker: MockerFixture):
    request_mock = mocker.Mock()
    request_mock.user.is_authenticated = False
    view_fun_mock = mocker.Mock()

    result = anonymous_required(view_fun_mock)(request_mock)

    assert isinstance(result, Mock)


def test_denied_access(mocker: MockerFixture):
    request_mock = mocker.Mock()
    request_mock.user.is_authenticated = True
    redirect_mock = mocker.patch(
        "users.decorators.redirect", spec=HttpResponseRedirect
    )
    redirect_mock.return_value = redirect_mock
    reverse_mock = mocker.patch("users.decorators.resolve_url")
    view_fun_mock = mocker.Mock()

    result = anonymous_required(view_fun_mock)(request_mock)

    assert isinstance(result, HttpResponseRedirect)
    view_fun_mock.assert_not_called()
    reverse_mock.assert_called_once_with(settings.ANONYMOUS_REDIRECT_URL)
    redirect_mock.assert_called_once_with(reverse_mock.return_value)


@pytest.mark.parametrize(
    ("redirect_url", "expected_redirect_url"),
    (
        [None, settings.ANONYMOUS_REDIRECT_URL],  # Default
        ["/pl/chat/", "/pl/chat/"],
    ),
)
def test_redirect_url(
    mocker: MockerFixture, redirect_url: str, expected_redirect_url: str
):
    request_mock = mocker.Mock()
    request_mock.user.is_authenticated = True
    redirect_mock = mocker.patch(
        "users.decorators.redirect", spec=HttpResponseRedirect
    )
    redirect_mock.return_value = redirect_mock
    reverse_mock = mocker.patch("users.decorators.resolve_url")
    view_fun_mock = mocker.Mock()

    if redirect_url:
        result = anonymous_required(view_fun_mock, redirect_url=redirect_url)(
            request_mock
        )
    else:
        result = anonymous_required(view_fun_mock)(request_mock)

    assert isinstance(result, HttpResponseRedirect)
    reverse_mock.assert_called_once_with(expected_redirect_url)
    redirect_mock.assert_called_once_with(reverse_mock.return_value)
