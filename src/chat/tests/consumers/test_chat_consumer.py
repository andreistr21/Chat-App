import pytest
from channels.layers import InMemoryChannelLayer
from channels.testing import WebsocketCommunicator
from django.core.exceptions import ObjectDoesNotExist
from pytest_mock import MockerFixture

from chat.consumers import ChatConsumer
from chat.models import ChatRoom


@pytest.fixture
def communicator(room: ChatRoom) -> WebsocketCommunicator:
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{room.id}",
    )
    communicator.scope["url_route"] = {"kwargs": {"room_id": str(room.id)}}
    communicator.scope["user"] = room.admin

    communicator.scope["channel_layer"] = InMemoryChannelLayer()

    return communicator


@pytest.mark.asyncio
@pytest.mark.django_db
class TestChatConsumerConnect:
    async def test_successful_connection(
        self, mocker: MockerFixture, communicator: WebsocketCommunicator
    ):
        mocker.patch("chat.consumers.is_chat_member", return_value=True)
        mocker.patch("chat.consumers.save_channel_name", return_value=None)
        mocker.patch("chat.consumers.remove_channel_name", return_value=None)

        connected, _ = await communicator.connect()

        assert connected

        await communicator.disconnect()

    async def test_denied_connection(
        self, mocker: MockerFixture, communicator: WebsocketCommunicator
    ):
        mocker.patch("chat.consumers.is_chat_member", return_value=False)

        with pytest.raises(
            ObjectDoesNotExist,
        ):
            await communicator.connect()
