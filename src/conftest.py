import pytest

from chat.redis import get_redis_connection


@pytest.fixture
def clear_redis_connection_cache():
    get_redis_connection.cache_clear()
