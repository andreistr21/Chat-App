from uuid import uuid4
import pytest

from chat.models import ChatRoom
from chat.selectors import get_room

@pytest.mark.django_db
def test_returns_room(room: ChatRoom):
    returned_room = get_room(str(room.id))
    
    assert returned_room == room

@pytest.mark.django_db
def test_no_returns_none():
    unexistent_room_id = str(uuid4())
    returned_room = get_room(unexistent_room_id)
    
    assert returned_room is None
