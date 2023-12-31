import pytest
from django.contrib.auth.models import User
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from chat.models import ChatRoom
from chat.selectors import get_3_members, get_last_message
from chat.views import index


@pytest.mark.django_db
def test_url_pattern_and_view_used(
    user_client: Client,
):
    """
    Tests if url pattern resolved and what view was used.
    """
    response = user_client.get("/en/chat/")

    assert response.status_code == 200
    assert response.resolver_match.func == index


@pytest.mark.django_db
def test_index_url(
    user_client: Client, user: User, room: ChatRoom, chat_app_url_prefix: str
):
    expected_user_rooms = user.admin.all()
    expected_chats_info = [
        (
            room.id,
            room.room_name or get_3_members(room),
            get_last_message(room),
            0
        )
    ]

    url = reverse("chat:index")

    response = user_client.get(url)

    assert url == chat_app_url_prefix
    assert response.status_code == 200
    assertTemplateUsed(response, "chat/index.html")  # type: ignore
    # Asserting context variables
    assert list(response.context["chat_rooms"]) == list(expected_user_rooms)
    assert response.context["chats_info"] == expected_chats_info


@pytest.mark.parametrize(
    ["http_method_name", "expected_status_code"],
    [
        ("get", 200),
        ("post", 405),
        ("put", 405),
        ("delete", 405),
    ],
)
@pytest.mark.django_db
def test_http_methods(
    user_client: Client, http_method_name, expected_status_code: int
):
    client_methods = {
        "get": user_client.get,
        "post": user_client.post,
        "put": user_client.put,
        "delete": user_client.delete,
    }

    client_method = client_methods.get(http_method_name)

    response = client_method(reverse("chat:index"))  # type: ignore

    assert response.status_code == expected_status_code
