import pytest
from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from pytest_mock import MockerFixture

from chat.forms import ChatRoomForm
from chat.models import ChatRoom
from chat.views import create_room

URL = reverse("chat:create_room")


@pytest.mark.django_db
def test_url_pattern_and_view_used(
    user_client: Client,
):
    """
    Tests if url pattern resolved and what view was used.
    """
    response = user_client.get("/en/chat/create/")

    assert response.status_code == 200
    assert response.resolver_match.func == create_room


@pytest.mark.django_db
def test_url_get_render(
    user_client: Client, rf: RequestFactory, user: User
):
    request = rf.get(URL)
    request.user = user
    expected_chat_room_form = ChatRoomForm(request=request)

    response = user_client.get(URL)

    assert response.status_code == 200
    assertTemplateUsed(response, "chat/create_room.html")  # type: ignore
    # Asserting context variables
    assert str(response.context["chat_room_form"]) == str(
        expected_chat_room_form
    )


@pytest.mark.django_db
def test_url_post_render(
    user_client: Client, rf: RequestFactory, mocker: MockerFixture, user: User
):
    mocker.patch.object(ChatRoomForm, "is_valid", return_value=False)

    data = {"room_name": "room name"}
    request = rf.post(URL, data=data)
    request.user = user
    expected_chat_room_form = ChatRoomForm(data, request=request)

    response = user_client.post(URL, data=data)

    assert response.status_code == 200
    assertTemplateUsed(response, "chat/create_room.html")  # type: ignore
    # Asserting context variables
    assert str(response.context["chat_room_form"]) == str(
        expected_chat_room_form
    )


@pytest.mark.django_db
def test_url_post_redirect(user_client: Client):
    data = {"room_name": "room name"}
    response = user_client.post(URL, data=data)

    new_room = ChatRoom.objects.first()

    assertRedirects(response, reverse("chat:room", args=(new_room.id,)))  # type: ignore


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
):
    mocker.patch.object(ChatRoomForm, "is_valid", return_value=False)
    client_methods = {
        "get": user_client.get,
        "post": user_client.post,
        "put": user_client.put,
        "delete": user_client.delete,
    }

    client_method = client_methods.get(http_method_name)

    response = client_method(URL)  # type: ignore

    assert response.status_code == expected_status_code
