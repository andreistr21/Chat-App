import json
from typing import Dict

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import InMemoryChannelLayer
from django.core.exceptions import ObjectDoesNotExist

from chat.models import ChatRoom
from chat.selectors import (
    get_chat_members,
    get_room,
    get_user,
    get_users_channels,
    is_chat_member,
    last_20_messages,
)
from chat.serializers import message_to_json, messages_to_json
from chat.services import (
    create_message,
    remove_channel_name,
    save_channel_name,
)


class ChatConsumer(AsyncWebsocketConsumer):
    reload_page_data = {"command": "reload_page"}

    async def fetch_messages(self, data) -> None:
        """
        Fetches last 20 messages form database and sends to the user
        """

        messages = await sync_to_async(last_20_messages)(data["room_id"])
        content = {
            "command": "messages",
            "messages": await sync_to_async(messages_to_json)(messages),
        }
        await self.send_message(content)

    async def new_message(self, data: Dict[str, str]) -> None:
        """
        Saves new message to database and send to room group and to each member
        if he is online and not in this chat group.
        """

        author = data["from"]
        author_obj = await sync_to_async(get_user)(author)
        room_obj = await sync_to_async(get_room)(data["room_id"])
        # TODO: Add handler to frontend. (Something need to be done in case room or author doesn't exists anymore)
        if room_obj is None or author_obj is None:
            return await self.send_message(self.reload_page_data)
        message = await sync_to_async(create_message)(
            author_obj, room_obj, data["message"]
        )

        message_json = await sync_to_async(message_to_json)(message)

        await self.send_chat_message(message_json)
        await self.send_message_to_chats_list(message_json, room_obj)

    async def connect(self) -> None:
        """Joins room group"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]

        if not await sync_to_async(is_chat_member)(
            self.scope["user"].id, self.room_name
        ):
            raise ObjectDoesNotExist(
                "User is not authorized to join this room or room doesn't"
                " exists."
            )

        self.room_group_name = f"chat_{self.room_name}"
        self.channel_layer: InMemoryChannelLayer

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        save_channel_name(self.scope["user"].id, self.channel_name)

    async def disconnect(self, _):
        """Leaves room group"""
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

        remove_channel_name(self.scope["user"].id, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """Receives message from WebSocket"""
        data = json.loads(text_data)
        command = data["command"]
        match command:
            case "fetch_messages":
                func = self.fetch_messages
            case "new_message":
                func = self.new_message

        await func(data)

    async def send_chat_message(self, message_json: Dict[str, str]) -> None:
        """Sends message to room group"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "command": "new_message",
                    "message": message_json,
                },
            },
        )

    async def send_message_to_chats_list(
        self, message_json: Dict[str, str], room_obj: ChatRoom
    ) -> None:
        """
        Sends message to each channel that belongs to user.
        """
        chat_members = await sync_to_async(get_chat_members)(room_obj)
        channels_names = await sync_to_async(get_users_channels)(chat_members)

        content = {
            "type": "chat_message",
            "message": {
                "command": "chats_list_message",
                "room_id": str(room_obj.id),
                "message": message_json,
            },
        }
        for user_channels in channels_names:
            for channel_name in user_channels:
                await self.channel_layer.send(
                    channel_name.decode(),
                    content,
                )

    async def send_message(self, message: Dict) -> None:
        """Sends message to current user (WebSocket)"""
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event: Dict):
        """Receives message from room group"""
        message = event["message"]

        await self.send_message(message)
