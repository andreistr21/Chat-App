from typing import Generator
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from chat.redis import get_redis_connection


@pytest.fixture
def user() -> User:
    return get_user_model().objects.create(
        username="test-user", password="test-password"
    )


@pytest.fixture
def clear_redis_connection_cache():
    get_redis_connection.cache_clear()


@pytest.fixture
def clear_redis_data():
    yield

    redis_connection = get_redis_connection()
    redis_connection.flushdb()
