from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
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
async def async_user():
    return await sync_to_async(User.objects.create)(
        username=f"test-user-{uuid4()}", password="test-password"
    )


@pytest.fixture
async def async_room(async_user: User) -> ChatRoom:
    room = await sync_to_async(ChatRoom.objects.create)(admin=async_user)
    await sync_to_async(room.members.add)(async_user)

    return room
