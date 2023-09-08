def construct_name_of_redis_list_for_channel_name(user_id: str) -> str:
    """
    Construct name for redis list that contains django-channels name.
    """
    return f"asgi:channels_name:{user_id}"