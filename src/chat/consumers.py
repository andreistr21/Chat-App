import json
from typing import Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import InMemoryChannelLayer

from chat.models import Message
from chat.selectors import get_author, get_room, last_20_messages
from chat.serializers import message_to_json, messages_to_json


# TODO: substitute all "get_room" with "get_room_or_redirect"
class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data) -> None:
        """Fetches last 20 messages form database and send to the group"""
        messages = last_20_messages(data["room_id"])
        content = {
            "command": "messages",
            "messages": messages_to_json(messages),
        }
        self.send_message(content)

    def new_message(self, data: Dict[str, str]) -> None:
        """Saves new message to database and send to room group"""
        author = data["from"]
        author_user = get_author(author)
        room_obj = get_room(data["room_id"])
        message = Message.objects.create(
            author=author_user, content=data["message"], room=room_obj
        )

        content = {
            "command": "new_message",
            "message": message_to_json(message),
        }
        return self.send_chat_message(content)

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
    }

    def connect(self) -> None:
        """Joins room group"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"
        self.channel_layer: InMemoryChannelLayer

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, _):
        """Leaves room group"""
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data: str) -> None:
        """Receives message from WebSocket"""
        data = json.loads(text_data)
        func = self.commands[data["command"]]
        func(self, data)

    def send_chat_message(self, message: Dict[str, str]) -> None:
        """Sends message to room group"""
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

    def send_message(self, message: Dict) -> None:
        """Sends message to current user (WebSocket)"""
        self.send(text_data=json.dumps(message))

    def chat_message(self, event: Dict):
        """Receives message from room group"""
        message = event["message"]

        self.send_message(message)
