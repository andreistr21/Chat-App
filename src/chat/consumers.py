import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import InMemoryChannelLayer
from django.contrib.auth import get_user_model

from chat.models import Message
from chat.selectors import last_20_messages


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        """Fetches last 20 messages form database and send to the group"""
        messages = last_20_messages()
        content = {
            "command": "messages",
            "messages": self.messages_to_json(messages),
        }
        self.send_message(content)

    def new_message(self, data):
        """Saves new message to database and send to room group"""
        author = data["from"]
        author_user = get_user_model().objects.get(username=author)
        message = Message.objects.create(
            author=author_user,
            content=data["message"],
        )

        content = {
            "command": "new_message",
            "message": self.message_to_json(message),
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        """Serializes messages to JSON"""
        return [self.message_to_json(message) for message in messages]

    def message_to_json(self, message: Message):
        """Serializes a message to JSON"""
        return {
            "author": message.author.username,
            "content": message.content,
            "timestamp": str(message.timestamp),
        }

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
    }

    def connect(self):
        """Joins room group"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.channel_layer: InMemoryChannelLayer

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        """Leaves room group"""
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        """Receives message from WebSocket"""
        data = json.loads(text_data)
        func = self.commands[data["command"]]
        func(self, data)

    def send_chat_message(self, message):
        """Sends message to room group"""
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

    def send_message(self, message):
        """Sends message to current user"""
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        """Receives message from room group"""
        message = event["message"]

        self.send_message(message)
