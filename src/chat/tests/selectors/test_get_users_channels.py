from typing import Generator

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from fakeredis import FakeStrictRedis
from pytest_mock import MockerFixture
from redis import Redis

from chat.redis import get_redis_connection
from chat.selectors import get_users_channels


def _add_data_to_redis(
    redis_connection: Redis, user_id: int, num_channels: int
) -> list[bytes]:
    """
    Appends data to redis list.
    """
    data = []
    for i in range(num_channels):
        redis_connection.lpush(
            _construct_name_of_redis_list_for_channel_name(user_id),
            f"name_{i}",
        )
        data.append(f"name_{i}".encode())

    return data[::-1]


def _construct_name_of_redis_list_for_channel_name(user_id: str | int) -> str:
    return f"asgi:users_channels_names:{user_id}"


def _multiple_users() -> Generator[User, None, None]:
    """
    Generates users.
    """
    counter = 0
    while True:
        yield get_user_model().objects.create(
            username=f"test-user_{counter}", password="test-password"
        )
        counter += 1


@pytest.mark.django_db
@pytest.mark.parametrize("num_users", (0, 1, 5))
@pytest.mark.parametrize("num_channels", (0, 1, 5, 10, 30))
def test_return_values_and_transaction_used(
    clear_redis_data: None,
    mocker: MockerFixture,
    num_channels: int,
    num_users: int,
):
    redis_patched = mocker.patch("chat.redis.from_url", FakeStrictRedis)
    mocker.patch(
        "chat.selectors.construct_name_of_redis_list_for_channel_name",
        _construct_name_of_redis_list_for_channel_name,
    )

    redis_connection = get_redis_connection()

    multiple_users = _multiple_users()
    users = [next(multiple_users) for _ in range(num_users)]

    expected_channels = [
        _add_data_to_redis(redis_connection, user.id, num_channels)
        for user in users
    ]
    channels = get_users_channels(users)

    assert channels == expected_channels
