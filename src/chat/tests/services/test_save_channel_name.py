from django.conf import settings
from fakeredis import FakeStrictRedis
from pytest_mock import MockerFixture
from redis.client import Redis

from chat.services import save_channel_name


def _test_construct_name_of_redis_list_for_channel_name(
    user_id: int | str,
) -> str:
    return f"asgi:users_channels_names:{user_id}"


def test_save_channel_name(mocker: MockerFixture):
    fake_redis_con = FakeStrictRedis()
    mocker.patch(
        "chat.services.get_redis_connection",
        return_value=fake_redis_con,
    )

    mocker.patch(
        "chat.services.construct_name_of_redis_list_for_channel_name",
        new=_test_construct_name_of_redis_list_for_channel_name,
    )
    redis_expire_patched = mocker.patch.object(Redis, "expire")
    user_id = "1"
    expected_channel_name = "test-channel-name"
    redis_key_name = _test_construct_name_of_redis_list_for_channel_name(
        user_id
    )

    save_channel_name(user_id, expected_channel_name)

    channel_name = fake_redis_con.lrange(redis_key_name, 0, -1)
    assert len(channel_name) == 1  # type: ignore
    assert channel_name[0].decode() == expected_channel_name  # type: ignore
    redis_expire_patched.assert_called_once_with(
        redis_key_name, settings.USERS_CHANNELS_NAMES_TTL
    )
