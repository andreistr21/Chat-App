import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from pytest_mock import MockerFixture

from chat.forms import ChatRoomMembersForm
from chat.models import ChatRoom
from chat.tests.services import multiple_users_generator
from chat.views import add_members

URL_NAME = "chat:add_members"


@pytest.mark.django_db
def test_url_pattern_and_view_used(user_client: Client, room: ChatRoom):
    """
    Tests if url pattern resolved and what view was used.
    """
    response = user_client.get(f"/en/chat/add-members/{room.id}/")

    assert response.status_code == 200
    assert response.resolver_match.func == add_members


@pytest.mark.django_db
def test_url_get_render(user_client: Client, room: ChatRoom):
    expected_chat_room_form = ChatRoomMembersForm()

    response = user_client.get(reverse(URL_NAME, args=(room.id,)))

    assert response.status_code == 200
    assertTemplateUsed(response, "chat/add_members.html")  # type: ignore
    # Asserting context variables
    assert str(response.context["chat_room_members_form"]) == str(
        expected_chat_room_form
    )


@pytest.mark.django_db
def test_url_post_render(
    user_client: Client, mocker: MockerFixture, room: ChatRoom
):
    mocker.patch("chat.views.get_room", return_value=room)
    mocker.patch.object(ChatRoomMembersForm, "is_valid", return_value=False)

    user_2 = next(multiple_users_generator())
    data = {"members_to_add": user_2.username}
    expected_chat_room_form = ChatRoomMembersForm(data=data)

    response = user_client.post(reverse(URL_NAME, args=(room.id,)), data=data)

    assert response.status_code == 200
    assertTemplateUsed(response, "chat/add_members.html")  # type: ignore
    # Asserting context variables
    assert str(response.context["chat_room_members_form"]) == str(
        expected_chat_room_form
    )


@pytest.mark.django_db
def test_url_post_redirect_no_user(
    user_client: Client, mocker: MockerFixture, room: ChatRoom
):
    mocker.patch("chat.views.get_room", return_value=None)
    mocker.patch.object(ChatRoomMembersForm, "is_valid", return_value=False)

    user_2 = next(multiple_users_generator())
    data = {"members_to_add": user_2.username}

    response = user_client.post(reverse(URL_NAME, args=(room.id,)), data=data)

    assertRedirects(response, reverse("chat:index"))  # type: ignore


@pytest.mark.django_db
def test_url_post_redirect_valid_form(
    user_client: Client, mocker: MockerFixture, room: ChatRoom
):
    mocker.patch("chat.views.get_room", return_value=room)

    user_2 = next(multiple_users_generator())
    data = {"members_to_add": user_2.username}

    response = user_client.post(reverse(URL_NAME, args=(room.id,)), data=data)

    assert user_2 in room.members.all()
    assertRedirects(response, reverse("chat:room", args=(room.id,)))  # type: ignore


@pytest.mark.parametrize(
    ["http_method_name", "expected_status_code"],
    [
        ("get", 200),
        ("post", 200),
        ("put", 405),
        ("delete", 405),
    ],
)
@pytest.mark.django_db
def test_http_methods(
    user_client: Client,
    mocker: MockerFixture,
    http_method_name: str,
    expected_status_code: int,
    room: ChatRoom,
):
    mocker.patch.object(ChatRoomMembersForm, "is_valid", return_value=False)
    client_methods = {
        "get": user_client.get,
        "post": user_client.post,
        "put": user_client.put,
        "delete": user_client.delete,
    }

    client_method = client_methods.get(http_method_name)

    response = client_method(reverse(URL_NAME, args=(room.id,)))  # type: ignore

    assert response.status_code == expected_status_code
