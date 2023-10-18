import json
from asyncio import sleep
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
from channels.layers import InMemoryChannelLayer, get_channel_layer
from channels.testing import ApplicationCommunicator, WebsocketCommunicator
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from pytest_mock import MockerFixture

from chat.consumers import ChatConsumer
from chat.models import ChatRoom, Message
from chat.serializers import message_to_json, messages_to_json


@pytest.fixture
async def communicator_no_conn(async_room: ChatRoom) -> WebsocketCommunicator:
    """
    Returns communicator that is not connected yet.
    """
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        f"/ws/chat/{async_room.id}",
    )
    communicator.scope["url_route"] = {
        "kwargs": {"room_id": str(async_room.id)}
    }
    communicator.scope["user"] = async_room.admin

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
    mocker.patch("chat.consumers.read_by", return_value=None)

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


async def _async_create_room(user_obj: User) -> ChatRoom:
    chat_room = await sync_to_async(ChatRoom.objects.create)(admin=user_obj)
    await sync_to_async(chat_room.members.add)(user_obj)

    return chat_room


async def _async_get_chat_room(
    user: User, num_messages: int
) -> tuple[ChatRoom, list[Message]]:
    """
    Creates user and room objects, and appends room with specified number of
    messages.
    """

    room_obj = await _async_create_room(user)
    messages = []
    for i in range(num_messages):
        messages.append(
            await sync_to_async(Message.objects.create)(
                author=user, room=room_obj, content=f"async-test-message-{i}"
            )
        )
        # Necessary for difference in timestamps
        await sleep(0.0001)

    return room_obj, messages


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
            await communicator_no_conn.connect(timeout=0.1)


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
        await communicator.receive_nothing()

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
        await communicator.receive_nothing()

        data = self._get_data()

        # Capture the calls made to new_message_patched
        calls = new_message_patched.call_args_list
        assert len(calls) == 1
        assert calls[0] == mocker.call(json.loads(data))


@pytest.mark.django_db
@pytest.mark.asyncio
class TestChatConsumerFetchMessages:
    data = {
        "command": "fetch_messages",
        "message": "some message",
        "from": "some username",
        "room_id": "room-id",
    }

    async def test_send_message_called(
        self,
        mocker: MockerFixture,
        communicator: WebsocketCommunicator,
        async_user: User,
    ):
        room, messages = await _async_get_chat_room(async_user, 5)
        self.data["room_id"] = str(room.id)
        self.data["username"] = async_user.username
        messages_json = await sync_to_async(messages_to_json)(messages)
        mocker.patch("chat.consumers.get_last_20_messages", return_value=[])
        mocker.patch(
            "chat.consumers.messages_to_json", return_value=messages_json
        )
        send_message_patched = mocker.patch.object(
            ChatConsumer, "send_message", return_value=None
        )
        content = {
            "command": "messages",
            "messages": messages_json,
        }

        await communicator.send_json_to(self.data)
        # Since send_message mocked, data won't be sent back.
        await communicator.receive_nothing()

        send_message_patched.assert_called_once_with(content)


@pytest.mark.django_db
@pytest.mark.asyncio
class TestChatConsumerNewMessage:
    data = {
        "command": "new_message",
        "message": "web-socket message content",
        "from": "some username",
        "room_id": "some room-id",
    }
    reload_page_data = {"command": "reload_page"}

    async def test_new_message_success(
        self,
        mocker: MockerFixture,
        communicator: WebsocketCommunicator,
        async_room: ChatRoom,
    ):
        # Arrange
        user = async_room.admin
        self.data["from"] = str(user.id)
        self.data["room_id"] = str(async_room.id)
        message = await sync_to_async(Message.objects.create)(
            author=user, room=async_room, content="test message content"
        )
        message_json = await sync_to_async(message_to_json)(message)

        get_user_patched = mocker.patch(
            "chat.consumers.get_user", return_value=user
        )
        get_room_patched = mocker.patch(
            "chat.consumers.get_room", return_value=async_room
        )
        create_message_patched = mocker.patch(
            "chat.consumers.create_message", return_value=message
        )
        message_to_json_patched = mocker.patch(
            "chat.consumers.message_to_json", return_value=message_json
        )
        send_chat_message_patched = mocker.patch.object(
            ChatConsumer, "send_chat_message", return_value=None
        )
        send_message_to_chats_list_patched = mocker.patch.object(
            ChatConsumer, "send_message_to_chats_list", return_value=None
        )

        # Actions
        await communicator.send_json_to(self.data)
        # Since send_chat_message and send_message_to_chats_list are mocked, data won't be sent back.
        await communicator.receive_nothing()

        # Assertions
        get_user_patched.assert_called_once_with(str(user.id))
        get_room_patched.assert_called_once_with(str(async_room.id))
        create_message_patched.assert_called_once_with(
            user, async_room, self.data["message"]
        )
        message_to_json_patched.assert_called_once_with(message)
        send_chat_message_patched.assert_called_once_with(message_json)
        send_message_to_chats_list_patched.assert_called_once_with(
            message_json, async_room
        )

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.parametrize(
        ["author_obj_is_none", "room_obj_is_none"],
        [(True, False), (False, True), (True, True)],
    )
    async def test_new_message_fail(
        self,
        mocker: MockerFixture,
        communicator: WebsocketCommunicator,
        async_room: ChatRoom,
        author_obj_is_none: bool,
        room_obj_is_none: bool,
    ):
        # Arrange
        user = async_room.admin
        self.data["from"] = (
            "unexistent user" if author_obj_is_none else str(user.id)
        )
        self.data["room_id"] = (
            "unexistent room" if room_obj_is_none else str(async_room.id)
        )

        get_user_return_value = None if author_obj_is_none else user
        get_user_patched = mocker.patch(
            "chat.consumers.get_user", return_value=get_user_return_value
        )
        get_room_return_value = None if room_obj_is_none else async_room
        get_room_patched = mocker.patch(
            "chat.consumers.get_room", return_value=get_room_return_value
        )
        send_reload_page_patched = mocker.patch.object(
            ChatConsumer, "send_reload_page", return_value=None
        )

        create_message_patched = mocker.patch(
            "chat.consumers.create_message", return_value=None
        )
        message_to_json_patched = mocker.patch(
            "chat.consumers.message_to_json", return_value=None
        )
        send_chat_message_patched = mocker.patch.object(
            ChatConsumer, "send_chat_message", return_value=None
        )
        send_message_to_chats_list_patched = mocker.patch.object(
            ChatConsumer, "send_message_to_chats_list", return_value=None
        )

        # Actions
        await communicator.send_json_to(self.data)
        # Since send_chat_message and send_message_to_chats_list are mocked, data won't be sent back.
        await communicator.receive_nothing()

        # Assertions
        get_user_patched.assert_called_once_with(self.data["from"])
        get_room_patched.assert_called_once_with(self.data["room_id"])
        send_reload_page_patched.assert_called_once()

        create_message_patched.assert_not_called()
        message_to_json_patched.assert_not_called()
        send_chat_message_patched.assert_not_called()
        send_message_to_chats_list_patched.assert_not_called()
