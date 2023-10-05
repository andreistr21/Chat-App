import pytest
from channels.layers import InMemoryChannelLayer, get_channel_layer
from channels.testing import WebsocketCommunicator
from django.core.exceptions import ObjectDoesNotExist
from pytest_mock import MockerFixture

from chat.consumers import ChatConsumer
from chat.models import ChatRoom


@pytest.fixture
def communicator_no_conn(room: ChatRoom) -> WebsocketCommunicator:
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{room.id}",
    )
    communicator.scope["url_route"] = {"kwargs": {"room_id": str(room.id)}}
    communicator.scope["user"] = room.admin

    communicator.scope["channel_layer"] = InMemoryChannelLayer()

    return communicator


@pytest.fixture
# @pytest_asyncio.fixture
async def communicator(
    mocker: MockerFixture,
    communicator_no_conn: WebsocketCommunicator,
) -> WebsocketCommunicator:
    mocker.patch("chat.consumers.is_chat_member", return_value=True)
    mocker.patch("chat.consumers.save_channel_name", return_value=None)

    await communicator_no_conn.connect()

    return communicator_no_conn


@pytest.mark.asyncio
@pytest.mark.django_db
class TestChatConsumerConnect:
    async def test_successful_connection(
        self,
        mocker: MockerFixture,
        communicator_no_conn: WebsocketCommunicator,
    ):
        mocker.patch("chat.consumers.is_chat_member", return_value=True)
        mocker.patch("chat.consumers.save_channel_name", return_value=None)
        mocker.patch("chat.consumers.remove_channel_name", return_value=None)

        connected, _ = await communicator_no_conn.connect()

        assert connected

        await communicator_no_conn.disconnect()

    async def test_denied_connection(
        self,
        mocker: MockerFixture,
        communicator_no_conn: WebsocketCommunicator,
    ):
        mocker.patch("chat.consumers.is_chat_member", return_value=False)

        with pytest.raises(
            ObjectDoesNotExist,
        ):
            await communicator_no_conn.connect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestChatConsumerDisconnect:
    @pytest.fixture(autouse=True)
    def remove_channel_name_patch(self, mocker: MockerFixture):
        mocker.patch("chat.consumers.remove_channel_name", return_value=None)

    async def test_successful_disconnect(
        self, communicator: WebsocketCommunicator
    ):
        channel_layer = get_channel_layer()

        # Asserts that consumer is a member of group before disconnection
        assert channel_layer.groups
        await communicator.disconnect()
        # Asserts that consumer is no longer a member of group
        assert not channel_layer.groups

    async def test_disconnect_twice(self, communicator: WebsocketCommunicator):
        channel_layer = get_channel_layer()

        # Asserts that consumer is a member of group before disconnection
        assert channel_layer.groups
        # Disconnect user, so next disconnection will fail
        await communicator.disconnect()
        # Asserts that consumer is no longer a member of group
        assert not channel_layer.groups
        # Second disconnection, should through exception, just None
        assert not await communicator.disconnect()
