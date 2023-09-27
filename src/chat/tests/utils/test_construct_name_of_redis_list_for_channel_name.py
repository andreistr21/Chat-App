import pytest

from chat.tests.services import (
    construct_name_of_redis_list_for_channel_name_test_method,
)
from chat.utils import construct_name_of_redis_list_for_channel_name


@pytest.mark.parametrize("user_id", ("21", 32))
def test_return_values(user_id: str | int):
    expected_channel_name = (
        construct_name_of_redis_list_for_channel_name_test_method(user_id)
    )

    channel_name = construct_name_of_redis_list_for_channel_name(user_id)

    assert channel_name == expected_channel_name
