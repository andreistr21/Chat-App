from functools import lru_cache
from os import getenv

from redis import Redis, from_url


@lru_cache(maxsize=1)
def get_redis_connection() -> Redis:
    """
    Creates redis connection during first call and returns it. During next
    call cached value will be returned.
    """
    if getenv("REDIS_URL", "").split("://")[0] == "rediss":
        return from_url(getenv("REDIS_URL", ""), ssl_cert_reqs=None)
    return from_url(getenv("REDIS_URL", ""))