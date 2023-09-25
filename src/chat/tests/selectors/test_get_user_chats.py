import pytest
from django.contrib.auth.models import User
from django.db.models import QuerySet

from chat.models import ChatRoom
from chat.selectors import get_user_chats


def _create_chat(user: User) -> None:
    """
    Creates chat and add user as admin and member.
    """
    chat = ChatRoom.objects.create(admin=user)
    chat.members.add(user)


def _add_chats_to_user(user: User, num_chats: int) -> None:
    """
    Makes user a member of specified number of chats.
    """
    for _ in range(num_chats):
        _create_chat(user)


@pytest.mark.parametrize("expected_num_chats", [0, 1, 5, 10, 30])
@pytest.mark.django_db
def test_returns_one_chat(user: User, expected_num_chats: int):
    _add_chats_to_user(user, expected_num_chats)

    user_chats = get_user_chats(user)

    assert len(user_chats) == expected_num_chats


@pytest.mark.parametrize("expected_num_chats", [0, 1, 5])
@pytest.mark.django_db
def test_returns_query_set(user: User, expected_num_chats: int):
    _add_chats_to_user(user, expected_num_chats)

    user_chats = get_user_chats(user)

    assert isinstance(user_chats, QuerySet)  # type: ignore
