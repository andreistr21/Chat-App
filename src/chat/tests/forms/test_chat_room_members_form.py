from uuid import uuid4

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from chat.forms import ChatRoomMembersForm
from chat.models import ChatRoom

URL = reverse("chat:add_members", args=(uuid4(),))


def test_field_attrs():
    form = ChatRoomMembersForm()

    assert form.fields["members_to_add"].label == "Usernames"
    assert (
        form.fields["members_to_add"].widget.attrs["placeholder"]
        == "Enter usernames separated by comma"
    )
    assert form.fields["members_to_add"].required is False


@pytest.mark.django_db
def test_update_members(user: User, room_no_members: ChatRoom):
    data = {"members_to_add": f"{user.username}, unexistent-user"}

    form = ChatRoomMembersForm(data=data)
    form.is_valid()
    form.update_members(room_no_members)

    assert list(room_no_members.members.all()) == [user]


@pytest.mark.django_db
def test_update_members_with_empty_field(
    user: User, room_no_members: ChatRoom
):
    data = {"members_to_add": ""}

    form = ChatRoomMembersForm(data=data)
    form.is_valid()
    form.update_members(room_no_members)

    assert not list(room_no_members.members.all())
