from uuid import uuid4

import pytest
from channels.layers import InMemoryChannelLayer
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from pytest_mock import MockerFixture

from chat.consumers import ChatConsumer
from chat.models import ChatRoom


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_successful_connection(
    mocker: MockerFixture, async_room: ChatRoom
):
    mocker.patch("chat.consumers.save_channel_name", return_value=None)
    mocker.patch("chat.consumers.remove_channel_name", return_value=None)

    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{async_room.id}+f",
    )
    communicator.scope["url_route"] = {
        "kwargs": {"room_id": str(async_room.id)}
    }
    communicator.scope["user"] = async_room.admin

    communicator.scope["channel_layer"] = InMemoryChannelLayer()

    connected, _ = await communicator.connect()

    assert connected

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_denied_connection(mocker: MockerFixture, user: User):
    mocker.patch("chat.consumers.save_channel_name", return_value=None)
    mocker.patch("chat.consumers.remove_channel_name", return_value=None)

    unexistent_room_id = uuid4()
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{unexistent_room_id}",
    )
    communicator.scope["url_route"] = {
        "kwargs": {"room_id": str(unexistent_room_id)}
    }
    communicator.scope["user"] = user

    communicator.scope["channel_layer"] = InMemoryChannelLayer()

    with pytest.raises(ObjectDoesNotExist):
        await communicator.connect(timeout=0.1)
