from typing import List
from chat.models import Message
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


def last_20_messages() -> List[Message]:
    return Message.objects.order_by("-timestamp").all()[:20][::-1]  # type: ignore


def get_author(username: str) -> User:
    return get_user_model().objects.get(username=username)  # type: ignore
