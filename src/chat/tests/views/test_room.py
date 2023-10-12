import pytest
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.urls import reverse
from pytest_mock import MockerFixture

from chat.models import ChatRoom
from chat.tests.services import multiple_users_generator
from chat.views import room as room_view


@pytest.mark.django_db
def test_access_allowed(
    rf: RequestFactory, mocker: MockerFixture, room: ChatRoom
):
    """
    Tests room view with auth user that has membership in a chat.
    """
    mocker.patch("chat.views.get_user_chats")
    mocker.patch("chat.views.chats_list")

    request = rf.get(reverse("chat:room", args=(str(room.id),)))
    request.user = room.admin

    response = room_view(request, room.id)

    assert response.status_code == 200


@pytest.mark.django_db
def test_no_chat_membership_redirect(
    rf: RequestFactory, mocker: MockerFixture, room: ChatRoom
):
    """
    Tests room view with auth user that doesn't has membership in a chat.
    """
    users_generator = multiple_users_generator()
    user = next(users_generator)
    request = rf.get(reverse("chat:room", args=(str(room.id),)))
    request.user = user

    response = room_view(request, room.id)

    assert response.status_code == 302


@pytest.mark.django_db
def test_anonymous_user_redirect(
    rf: RequestFactory, mocker: MockerFixture, room: ChatRoom
):
    """
    Tests room view with not auth user.
    """
    request = rf.get(reverse("chat:room", args=(str(room.id),)))
    request.user = AnonymousUser()

    response = room_view(request, room.id)

    assert response.status_code == 302
