import json
from uuid import uuid4

import pytest
from channels.layers import InMemoryChannelLayer, get_channel_layer
from channels.testing import WebsocketCommunicator
from django.core.exceptions import ObjectDoesNotExist
from pytest_mock import MockerFixture

from chat.consumers import ChatConsumer
from chat.models import ChatRoom


@pytest.fixture
def communicator_no_conn(room: ChatRoom) -> WebsocketCommunicator:
    """
    Returns communicator that is not connected yet.
    """
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{room.id}",
    )
    communicator.scope["url_route"] = {"kwargs": {"room_id": str(room.id)}}
    communicator.scope["user"] = room.admin

    communicator.scope["channel_layer"] = InMemoryChannelLayer()

    return communicator


@pytest.fixture
async def communicator_no_discon(
    mocker: MockerFixture,
    communicator_no_conn: WebsocketCommunicator,
) -> WebsocketCommunicator:
    """
    Returns communicator that is already connected.
    """
    mocker.patch("chat.consumers.is_chat_member", return_value=True)
    mocker.patch("chat.consumers.save_channel_name", return_value=None)
    mocker.patch("chat.consumers.remove_channel_name", return_value=None)

    await communicator_no_conn.connect()

    return communicator_no_conn


@pytest.fixture
async def communicator(
    communicator_no_discon: WebsocketCommunicator,
) -> WebsocketCommunicator:
    """
    Returns communicator that is already connected and will disconnect it after
    a test is done. If not disconnected, RuntimeWarnings can be raised about
    things never being awaited.
    """

    yield communicator_no_discon

    await communicator_no_discon.disconnect()


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
    async def test_successful_disconnect(
        self, communicator_no_discon: WebsocketCommunicator
    ):
        channel_layer = get_channel_layer()

        # Asserts that consumer is a member of group before disconnection
        assert channel_layer.groups
        await communicator_no_discon.disconnect()
        # Asserts that consumer is no longer a member of group
        assert not channel_layer.groups

    async def test_disconnect_twice(
        self, communicator_no_discon: WebsocketCommunicator
    ):
        channel_layer = get_channel_layer()

        # Asserts that consumer is a member of group before disconnection
        assert channel_layer.groups
        # Disconnect user, so next disconnection will fail
        await communicator_no_discon.disconnect()
        # Asserts that consumer is no longer a member of group
        assert not channel_layer.groups
        # Second disconnection, should through exception, just None
        assert not await communicator_no_discon.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestChatConsumerReceive:
    data = {
        "command": "command",
        "message": "some message",
        "from": "some username",
        "room_id": str(uuid4()),
    }

    def _get_data(self) -> str:
        data_str = str(self.data)
        # Makes str parentness <'>, and not <">, because json.loads need so.
        return data_str.replace("'", '"')

    @pytest.mark.asyncio
    async def test_call_fetch_messages(
        self, mocker: MockerFixture, communicator: WebsocketCommunicator
    ):
        self.data["command"] = "fetch_messages"
        fetch_messages_patched = mocker.patch.object(
            ChatConsumer, "fetch_messages", return_value=None
        )

        await communicator.send_json_to(self.data)
        # Since fetch_messages mocked, data won't be sent back.
        with pytest.raises(TimeoutError):
            await communicator.receive_json_from(timeout=0.1)

        data = self._get_data()

        # Capture the calls made to fetch_messages_patched
        calls = fetch_messages_patched.call_args_list
        assert len(calls) == 1
        assert calls[0] == mocker.call(json.loads(data))

    @pytest.mark.asyncio
    async def test_call_new_message(
        self, mocker: MockerFixture, communicator: WebsocketCommunicator
    ):
        self.data["command"] = "new_message"
        new_message_patched = mocker.patch.object(
            ChatConsumer, "new_message", return_value=None
        )

        await communicator.send_json_to(self.data)
        # Since new_message mocked, data won't be sent back.
        with pytest.raises(TimeoutError):
            await communicator.receive_json_from(timeout=0.1)

        data = self._get_data()

        # Capture the calls made to new_message_patched
        calls = new_message_patched.call_args_list
        assert len(calls) == 1
        assert calls[0] == mocker.call(json.loads(data))
