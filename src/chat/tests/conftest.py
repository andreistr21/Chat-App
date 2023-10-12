import pytest
from django.contrib.auth.models import User
from django.test import Client

from chat.models import ChatRoom


@pytest.fixture
@pytest.mark.django_db
def room(user: User) -> ChatRoom:
    room = ChatRoom.objects.create(admin=user)
    room.members.add(user)

    return room


@pytest.fixture
@pytest.mark.django_db
def room_no_members(user: User) -> ChatRoom:
    return ChatRoom.objects.create(admin=user)


@pytest.fixture
def chat_app_url_prefix() -> str:
    return "/en/chat/"


@pytest.fixture
def user_client(client: Client, user: User) -> Client:
    """
    Returns client with authenticated user.
    """
    client.force_login(user)
    return client
