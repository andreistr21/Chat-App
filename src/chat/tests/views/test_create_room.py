import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from pytest_mock import MockerFixture
from chat.forms import ChatRoomForm

from chat.views import create_room

URL = reverse("chat:create_room")


@pytest.mark.django_db
def test_access_allowed(rf: RequestFactory, user: User):
    request = rf.get(URL)
    request.user = user

    response = create_room(request)

    assert response.status_code == 200


def test_access_denied(rf: RequestFactory):
    request = rf.get(URL)
    request.user = AnonymousUser()

    response = create_room(request)

    assert response.status_code == 302


@pytest.mark.django_db
def test_post_invalid_form(
    rf: RequestFactory, user: User, mocker: MockerFixture
):
    mocker.patch.object(ChatRoomForm, "is_valid", return_value=False)

    data = {"room_name": "invalid_form"}
    request = rf.post(URL, data=data)
    request.user = user

    response = create_room(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_post_valid_form(
    rf: RequestFactory, user: User, mocker: MockerFixture
):
    mocker.patch.object(ChatRoomForm, "is_valid", return_value=True)

    data = {"room_name": "invalid_form"}
    request = rf.post(URL, data=data)
    request.user = user

    response = create_room(request)

    assert response.status_code == 302
