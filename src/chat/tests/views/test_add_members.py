import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from pytest_mock import MockerFixture
from chat.forms import ChatRoomMembersForm
from chat.models import ChatRoom
from chat.tests.services import multiple_users_generator

from chat.views import add_members

URL_NAME = "chat:add_members"


@pytest.mark.django_db
def test_access_allowed(
    rf: RequestFactory, user: User, room_no_members: ChatRoom
):
    request = rf.get(reverse(URL_NAME, args=(room_no_members.id,)))
    request.user = user

    response = add_members(request, room_no_members.id)

    assert response.status_code == 200


@pytest.mark.django_db
def test_access_denied_no_chat_membership(
    rf: RequestFactory, user: User, room_no_members: ChatRoom
):
    request = rf.get(reverse(URL_NAME, args=(room_no_members.id,)))
    request.user = user

    response = add_members(request, room_no_members.id)

    assert response.status_code == 302


@pytest.mark.django_db
def test_access_denied_anonymous_user(
    rf: RequestFactory, user: User, room_no_members: ChatRoom
):
    request = rf.get(reverse(URL_NAME, args=(room_no_members.id,)))
    request.user = AnonymousUser()

    response = add_members(request, room_no_members.id)

    assert response.status_code == 302


@pytest.mark.django_db
def test_post_no_room(
    mocker: MockerFixture,
    rf: RequestFactory,
    user: User,
    room_no_members: ChatRoom,
):
    mocker.patch("chat.views.get_room", return_value=None)

    data = {"members_to_add": "username"}
    request = rf.post(reverse(URL_NAME, args=(room_no_members.id,)), data=data)
    request.user = user

    response = add_members(request, room_no_members.id)

    assert response.status_code == 302


@pytest.mark.django_db
def test_post_invalid_form(
    mocker: MockerFixture,
    rf: RequestFactory,
    user: User,
    room_no_members: ChatRoom,
):
    mocker.patch("chat.views.get_room", return_value=room_no_members)
    mocker.patch.object(ChatRoomMembersForm, "is_valid", return_value=False)

    data = {"members_to_add": "username"}
    request = rf.post(reverse(URL_NAME, args=(room_no_members.id,)), data=data)
    request.user = user

    response = add_members(request, room_no_members.id)

    assert response.status_code == 200


@pytest.mark.django_db
def test_post_valid_form(
    mocker: MockerFixture,
    rf: RequestFactory,
    user: User,
    room: ChatRoom,
):
    mocker.patch("chat.views.get_room", return_value=room)
    
    user_2 = next(multiple_users_generator())

    data = {"members_to_add": user_2.username}
    request = rf.post(reverse(URL_NAME, args=(room.id,)), data=data)
    request.user = user

    response = add_members(request, room.id)

    assert response.status_code == 302
    assert list(room.members.all()) == [user, user_2]
