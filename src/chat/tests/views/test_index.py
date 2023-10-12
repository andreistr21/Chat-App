import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from django.urls import reverse
from pytest_mock import MockerFixture

from chat.views import index


@pytest.mark.django_db
def test_access_allowed(rf: RequestFactory, mocker: MockerFixture, user: User):
    """
    Tests index view with authenticated user.
    """
    mocker.patch("chat.views.get_user_chats")
    mocker.patch("chat.views.chats_list")

    request = rf.get(reverse("chat:index"))
    request.user = user

    response = index(request)

    assert response.status_code == 200


def test_access_denied(rf: RequestFactory):
    """
    Tests index view with anonymous user.
    """
    request = rf.get(reverse("chat:index"))
    request.user = AnonymousUser()

    response = index(request)

    assert response.status_code == 302
