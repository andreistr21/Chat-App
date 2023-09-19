from os import environ

from fakeredis import FakeStrictRedis

from chat.redis import get_redis_connection


def test_redis_connection(mocker, clear_redis_connection_cache):
    redis_connection_patched = mocker.patch(
        "chat.redis.from_url", return_value=FakeStrictRedis
    )
    environ["REDIS_URL"] = "redis_non_TSL_link"
    connection1 = get_redis_connection()
    connection2 = get_redis_connection()

    redis_connection_patched.assert_called_once_with("redis_non_TSL_link")
    assert connection1 == connection2


def test_redis_connection2(mocker, clear_redis_connection_cache):
    redis_connection_patched = mocker.patch(
        "chat.redis.from_url", return_value=FakeStrictRedis
    )
    environ["REDIS_URL"] = "rediss://:redis_TSL_link"
    connection1 = get_redis_connection()
    connection2 = get_redis_connection()

    redis_connection_patched.assert_called_once_with(
        "rediss://:redis_TSL_link", ssl_cert_reqs=None
    )
    assert connection1 == connection2
