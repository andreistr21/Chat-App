from fakeredis import FakeStrictRedis
from pytest_mock import MockerFixture

from chat.services import remove_channel_name


def _test_construct_name_of_redis_list_for_channel_name(
    user_id: int | str,
) -> str:
    return f"asgi:users_channels_names:{user_id}"


def test_remove_channel_name(mocker: MockerFixture):
    fake_redis_con = FakeStrictRedis()
    mocker.patch(
        "chat.services.get_redis_connection",
        return_value=fake_redis_con,
    )

    mocker.patch(
        "chat.services.construct_name_of_redis_list_for_channel_name",
        new=_test_construct_name_of_redis_list_for_channel_name,
    )
    user_id = "1"
    channel_name = "test-channel-name"
    redis_key_name = _test_construct_name_of_redis_list_for_channel_name(
        user_id
    )
    fake_redis_con.lpush(redis_key_name, channel_name)

    # Asserts that element exist before removing
    assert len(fake_redis_con.lrange(redis_key_name, 0, -1)) == 1  # type: ignore

    remove_channel_name(user_id, channel_name)

    # Asserts that element removed
    assert len(fake_redis_con.lrange(redis_key_name, 0, -1)) == 0  # type: ignore
