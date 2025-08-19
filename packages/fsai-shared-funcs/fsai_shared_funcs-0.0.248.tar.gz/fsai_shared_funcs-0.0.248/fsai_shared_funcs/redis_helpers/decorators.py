import functools

from loguru import logger


class RedisCacheManager:
    def __init__(self, _redis, redis_key: str):
        self._redis = _redis
        self.redis_key = redis_key

    def exists(self):
        logger.debug(f'Checking if key "{self.redis_key}" exists')
        return self._redis.exists(self.redis_key)

    def get(self):
        logger.debug(f'Getting key "{self.redis_key}"')
        return self._redis.pget(self.redis_key)

    def set(self, data: int, exp: int = 43200):
        logger.debug(f'Setting key "{self.redis_key}"')
        self._redis.pset(self.redis_key, data, ex=exp)


def cache_return_data(redis, key, exp=43200):
    def decorator_repeat(data_fn):
        @functools.wraps(data_fn)
        async def wrapper_repeat(*args, **kwargs):
            logger.debug(f'Caching return data for key "{key}"')
            # Create the RedisCacheManager
            r = RedisCacheManager(redis, key)

            # If the key doesn't exist
            if not r.exists():
                # Get the data from the function
                data = await data_fn()
                # Set the data in the cache
                r.set(data, exp)

            # Return the data
            return r.get()

        return wrapper_repeat

    return decorator_repeat
