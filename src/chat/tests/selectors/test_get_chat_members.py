import pytest
from django.contrib.auth.models import User
from django.db.models import QuerySet

from chat.models import ChatRoom
from chat.selectors import get_chat_members
from chat.tests.services import multiple_users_generator


def _add_members_to_chat(users: list[User], room: ChatRoom) -> None:
    for user in users:
        room.members.add(user)


@pytest.mark.django_db
@pytest.mark.parametrize("num_members", (0, 1, 2, 5, 10, 30))
def test_return_values(room: ChatRoom, num_members: int):
    """
    Asserts what what type and values will be returned.
    """

    current_member = room.members.all()[0]
    room.members.remove(current_member)
    multiple_users = multiple_users_generator()
    expected_users = [next(multiple_users) for _ in range(num_members)]
    _add_members_to_chat(expected_users, room)

    users = get_chat_members(room)

    # Asserts that users variable is type of QuerySet
    assert type(users) == QuerySet
    # Asserts values to be exact as expected
    assert list(users) == expected_users
