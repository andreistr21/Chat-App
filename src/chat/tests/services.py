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
