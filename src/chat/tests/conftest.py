import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom


@pytest.fixture
@pytest.mark.django_db
def room(user: User) -> ChatRoom:
    room = ChatRoom.objects.create(admin=user)
    room.members.add(user)

    return room
