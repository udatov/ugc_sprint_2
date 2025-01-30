from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_cache() -> Redis:
    """
    Dependency function to get the Redis cache connection.

    :yield: The Redis cache connection.
    """
    try:
        yield redis
    finally:
        await redis.close()
