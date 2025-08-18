import pickle
import redis
from typing import Any, Dict, List, Optional


class RedisClient:
    def __init__(self, redis_host, redis_port):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    ##########
    # Getters
    ##########
    def get(self, key, default=None):
        """
        Retrieve the byte value. If key does not exist, return default.
        """
        cached_instance = self.redis_client.get(key)
        if cached_instance:
            return pickle.loads(cached_instance)
        else:
            return default

    def mget(self, keys, default=None):
        """
        Get the values of multiple keys at once. If the key does not exists,
        default value is returned instead.
        """
        response_list = self.redis_client.mget(keys)
        return [pickle.loads(res) or default for res in response_list]

    def fetch(self, key, func, ttl, *args, **kwargs):
        """
        Wrapper for Redis GET function, to help get the value
        to the key being passed in, if the key does not exist,
        call the callback function being passed in instead
        """
        cached_result = self.redis_client.get(key)
        if cached_result:
            return pickle.loads(cached_result)
        result = func(*args, **kwargs)
        if result is not None:
            serialized_result = pickle.dumps(result)
            self.redis_client.set(key, serialized_result, ttl)
        return result


    def exists(self, key):
        """
        Return 1 if the key exists.
        Return 0 if the key does not exist.
        """
        return self.redis_client.exists(key)

    def hgetall(self, key: str) -> Dict[str, Any]:
        """
        Retrieve all fields and values of the hash stored at key,
        deserializing the values.
        """
        raw_hash = self.redis_client.hgetall(key)
        return {k.decode("utf-8"): pickle.loads(v) for k, v in raw_hash.items()}

    def keys(self, pattern: str) -> List[str]:
        """
        Retrieves all keys matching pattern, decoding the keys into strings.
        """
        return [key.decode("utf-8") for key in self.redis_client.keys(pattern)]

    ##########
    # Setters
    ##########
    def set(self, key, value, expiry=None):
        """
        Set key to hold the byte value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time
        to live associated with the key is discarded on successful
        SET operation.
        """
        serialized_value = pickle.dumps(value)
        return self.redis_client.set(key, serialized_value, expiry)

    def mset(self, mapping):
        """
        Set multiple {key: value} pairs at once. Existing keys
        are overwritten, ttls are discarded.
        """
        if mapping:
            for key in mapping:
                mapping[key] = pickle.dumps(mapping[key])
            return self.redis_client.mset(mapping)

    def incr(self, key, amount=1, expiry=None):
        """
        Increment the integer value of a key by the given amount.
        """
        new_value = self.redis_client.incr(key, amount)
        if expiry:
            self.redis_client.expire(key, expiry)
        return new_value

    def hset(self, key: str, mapping: Optional[Dict[str, Any]] = None, **kwargs) -> int:
        """
        Set fields in a hash stored at key.

        If mapping is provided, all values are serialized and set at once. If no
        mapping is provided, kwargs are used as field-value pairs, similar to
        redis-py.
        """
        if mapping is None and kwargs:
            mapping = kwargs
        if mapping is not None:
            serialized_mapping = {k: pickle.dumps(v) for k, v in mapping.items()}
            return self.redis_client.hset(key, mapping=serialized_mapping)
        raise ValueError("No fields provided for hset.")

    ##########
    # List Operations
    ##########
    def list_rpush(self, key, value, expiry=None):
        serialized_value = pickle.dumps(value)
        res = self.redis_client.rpush(
            key, serialized_value
        )  # return the length of the list

        # Sets the expiry on the entire list, not the elements
        if expiry:
            self.redis_client.expire(key, expiry)

        return res

    def list_lpop(self, key):
        """
        Removes and returns the first element of the list stored at key.
        """
        res = self.redis_client.lpop(key)
        if res:
            return pickle.loads(res)
        else:
            return None

    def llen(self, key):
        """
        Returns the length of the list stored at key. If key does not
        exist, it is interpreted as an empty list and 0 is returned.
        An error is returned when the value stored at key is not a list.
        """
        return self.redis_client.llen(key)

    def list_range(self, key, start=0, stop=-1, default=[]):
        range = self.redis_client.lrange(key, start, stop)
        return [pickle.loads(res) or default for res in range]

    ##########
    # Set Operations
    ##########

    def sadd(self, key, value, expiry=None):
        serialized_value = pickle.dumps(value)
        res = self.redis_client.sadd(
            key, serialized_value
        )  # return 1 if item was added, 0 is not

        # Sets the expiry on the entire set, not the elements
        if expiry:
            self.redis_client.expire(key, expiry)
        return res

    def srem(self, key, value):
        serialized_value = pickle.dumps(value)
        return self.redis_client.srem(
            key, serialized_value
        )  # return 1 if item was removed, 0 is not

    def smembers(self, key):
        members = self.redis_client.smembers(key)
        return {pickle.loads(mem) for mem in members}

    def sismember(self, key, value):
        serialized_value = pickle.dumps(value)
        return self.redis_client.sismember(key, serialized_value)

    def srandmember(self, key, number=None):
        serialized_value = self.redis_client.srandmember(key, number)
        if number:
            return [pickle.loads(val) for val in serialized_value]
        elif serialized_value:
            return pickle.loads(serialized_value)
        else:
            return None

    ##########
    # Deletion/Expiry
    ##########
    def delete(self, key):
        self.redis_client.delete(key)

    def flushall(self, asynchronous=False):
        """
        Flush all keys - clear cache
        """
        return self.redis_client.flushall(asynchronous)

    def expire(self, key, expiry):
        """
        Set a timeout on key. After the timeout has expired, the key will
        automatically be deleted. A key with an associated timeout is often
        said to be volatile in Redis terminology.
        It is possible to call EXPIRE using as argument a key that already
        has an existing expire set. In this case the time to live of a key
        is updated to the new value.
        Return value:
        1 if the timeout was set.
        0 if key does not exist.
        """
        return self.redis_client.expire(key, expiry)

    def ttl(self, key):
        """
        Returns the remaining time to live of a key that has a timeout.
        This introspection capability allows a Redis client to check how
        many seconds a given key will continue to be part of the dataset.
        The command returns -2 if the key does not exist.
        The command returns -1 if the key exists but has no associated expire.
        """
        return self.redis_client.ttl(key)
