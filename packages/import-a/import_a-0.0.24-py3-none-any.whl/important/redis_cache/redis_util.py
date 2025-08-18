import hashlib
import json
from functools import wraps

from important.redis_cache.redis_client import RedisClient


class RedisUtil:
    def __init__(self, redis_host, redis_port):
        self.redis_client = RedisClient(redis_host, redis_port)

    def cache(self, expiry=None):
        """
        A decorator that caches function results in Redis. If the key exists,
        return the cached value. If not, call the function and cache the result.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate a unique cache key based on function name and hashed arguments
                serialized_args = json.dumps(
                    {"args": args, "kwargs": kwargs}, sort_keys=True, default=str
                )
                hashed_args = hashlib.sha256(serialized_args.encode()).hexdigest()
                cache_key = f"{func.__name__}:{hashed_args}"
                # Return the cached result if it exists, otherwise call the function and cache the result
                return self.redis_client.fetch(cache_key, func, expiry, *args, **kwargs)

            return wrapper

        return decorator
