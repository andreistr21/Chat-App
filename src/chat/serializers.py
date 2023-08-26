from typing import Dict, List

from chat.models import Message


def messages_to_json(messages: List[Message]) -> List[Dict[str, str]]:
    """Serializes messages to JSON"""
    return [message_to_json(message) for message in messages]


def message_to_json(message: Message) -> Dict[str, str]:
    """Serializes a message to JSON"""
    return {
        "author": message.author.username,
        "content": message.content,
        "timestamp": str(message.timestamp),
    }
