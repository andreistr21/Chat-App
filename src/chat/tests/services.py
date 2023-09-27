from typing import Generator

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


def multiple_users_generator() -> Generator[User, None, None]:
    """
    Generates users.
    """
    counter = 0
    while True:
        yield get_user_model().objects.create(
            username=f"test-user_{counter}", password="test-password"
        )
        counter += 1


def construct_name_of_redis_list_for_channel_name_test_method(
    user_id: str | int,
) -> str:
    """
    Construct name for redis list that contains django-channels name.
    """
    return f"asgi:users_channels_names:{user_id}"
