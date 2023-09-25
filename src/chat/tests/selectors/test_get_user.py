import pytest

from chat.selectors import get_user
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_return_user(user: User) -> None:
    returned_user = get_user(user.username)

    assert returned_user == user


@pytest.mark.django_db
def test_no_return_user() -> None:
    returned_user = get_user("unexistent-username")

    assert returned_user is None
