import pytest
from django.contrib.auth.models import User

from chat.models import ChatRoom
from chat.selectors import is_chat_member
from chat.tests.services import multiple_users_generator


@pytest.mark.django_db
@pytest.mark.parametrize("num_members", (1, 2, 3))
def test_if_user_is_member(room_no_members: ChatRoom, num_members: int):
    multiple_users = multiple_users_generator()
    users = []
    for _ in range(num_members):
        user = next(multiple_users)
        room_no_members.members.add(user)
        users.append(user)

    is_member = is_chat_member(users[0].id, room_no_members)

    assert is_member


@pytest.mark.django_db
@pytest.mark.parametrize("num_members", (0, 1, 2, 3))
def test_if_user_is_not_member(
    user: User, room_no_members: ChatRoom, num_members: int
):
    multiple_users = multiple_users_generator()
    users = []
    for _ in range(num_members):
        temp_user = next(multiple_users)
        room_no_members.members.add(temp_user)
        users.append(temp_user)

    is_member = is_chat_member(user.id, room_no_members)

    assert not is_member
