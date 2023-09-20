import json
from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import InMemoryChannelLayer
from django.contrib.auth.models import User

from chat.models import ChatRoom, Message
from chat.selectors import (
    get_author,
    get_chat_members,
    get_room,
    get_users_channels,
    last_20_messages,
)
from chat.serializers import message_to_json, messages_to_json
from chat.services import remove_channel_name, save_channel_name


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands: dict[str, Callable] = {
            "fetch_messages": self.fetch_messages,
            "new_message": self.new_message,
        }

    def fetch_messages(self, data) -> None:
        """Fetches last 20 messages form database and send to the group"""
        messages = last_20_messages(data["room_id"])
        content = {
            "command": "messages",
            "messages": messages_to_json(messages),
        }
        self.send_message(content)

    def new_message(self, data: Dict[str, str]) -> None:
        """
        Saves new message to database and send to room group and to each member
        if he is online and not in this chat group.
        """
        author = data["from"]
        author_obj = get_author(author)
        room_obj = get_room(data["room_id"])
        # TODO: Something need to be done in case room doesn't exists anymore
        if room_obj is None:
            return None
        message = Message.objects.create(
            author=author_obj, content=data["message"], room=room_obj
        )

        message_json = message_to_json(message)

        self.send_chat_message(message_json)
        self.send_message_to_chats_list(
            author_obj, message_json, room_obj  # type: ignore
        )

    def connect(self) -> None:
        """Joins room group"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"
        self.channel_layer: InMemoryChannelLayer

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        save_channel_name(self.scope["user"].id, self.channel_name)

    def disconnect(self, _):
        """Leaves room group"""
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

        remove_channel_name(self.scope["user"].id, self.channel_name)

    def receive(self, text_data: str) -> None:
        """Receives message from WebSocket"""
        data = json.loads(text_data)
        func = self.commands[data["command"]]
        func(data)

    def send_chat_message(self, message_json: Dict[str, str]) -> None:
        """Sends message to room group"""
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "command": "new_message",
                    "message": message_json,
                },
            },
        )

    def send_message_to_chats_list(
        self, user_obj: User, message_json: Dict[str, str], room_obj: ChatRoom
    ) -> None:
        """
        Sends message to each channel that belongs to user.
        """
        chat_members = get_chat_members(room_obj)
        channels_names = get_users_channels(chat_members)

        content = {
            "type": "chat_message",
            "message": {
                "command": "chats_list_message",
                "room_id": str(room_obj.id),
                "message": message_json,
            },
        }
        # channel_layer = get_channel_layer()
        for user_channels in channels_names:
            for channel_name in user_channels:
                async_to_sync(self.channel_layer.send)(
                    channel_name.decode(),
                    content,
                )

    def send_message(self, message: Dict) -> None:
        """Sends message to current user (WebSocket)"""
        self.send(text_data=json.dumps(message))

    def chat_message(self, event: Dict):
        """Receives message from room group"""
        message = event["message"]

        self.send_message(message)
