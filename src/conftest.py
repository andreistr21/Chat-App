from django.test import Client
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from chat.redis import get_redis_connection

TEST_USERNAME = "test-user"
TEST_PASSWORD = "test-password"


@pytest.fixture
def user() -> User:
    return get_user_model().objects.create(
        username=TEST_USERNAME, password=TEST_PASSWORD
    )


@pytest.fixture
def clear_redis_connection_cache():
    get_redis_connection.cache_clear()


@pytest.fixture
def clear_redis_data():
    yield

    redis_connection = get_redis_connection()
    redis_connection.flushdb()


@pytest.fixture
def user_client(client: Client, user: User) -> Client:
    """
    Returns client with authenticated user.
    """
    client.force_login(user)
    return client
