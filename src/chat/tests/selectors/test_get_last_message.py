from time import sleep
import pytest

from chat.models import ChatRoom, Message
from django.contrib.auth.models import User

from chat.selectors import get_last_message


def _add_messages_to_chat(
    user: User, chat: ChatRoom, num_messages: int
) -> None:
    for i in range(num_messages):
        Message.objects.create(author=user, room=chat, content=str(i + 1))
        sleep(0.0001)


@pytest.mark.parametrize(
    ("num_messages", "expected_message"),
    ((0, None), (1, "1"), (2, "2"), (5, "5"), (30, "30")),
)
@pytest.mark.django_db
def test_return_message(
    num_messages: int, expected_message: str | None, room: ChatRoom, user: User
):
    _add_messages_to_chat(user, room, num_messages)
    last_msg = get_last_message(room)

    assert (
        last_msg.content
        if last_msg is not None
        else last_msg == expected_message
    )
