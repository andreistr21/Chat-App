import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

from chat.forms import ChatRoomForm

URL = reverse("chat:create_room")


@pytest.mark.django_db
def test_initialization(user: User, rf: RequestFactory):
    request = rf.get(URL)
    request.user = user

    form = ChatRoomForm(request=request)

    assert form.request == request


@pytest.mark.parametrize("room_name", ("", "test room name"))
@pytest.mark.django_db
def test_validation(rf: RequestFactory, user: User, room_name: str):
    request = rf.get(URL)
    request.user = user
    data = {"room_name": room_name}

    form = ChatRoomForm(data=data, request=request)

    assert form.is_valid()


@pytest.mark.django_db
def test_saving_with_commit_false(rf: RequestFactory, user: User):
    request = rf.get(URL)
    request.user = user
    data = {"room_name": "test room name"}

    form = ChatRoomForm(data=data, request=request)
    room = form.save(commit=False)

    assert not list(room.members.all())


@pytest.mark.django_db
def test_saving_with_commit_true(rf: RequestFactory, user: User):
    request = rf.get(URL)
    request.user = user
    data = {"room_name": "test room name"}

    form = ChatRoomForm(data=data, request=request)
    room = form.save()

    assert room.admin == user
    assert list(room.members.all()) == [user]
