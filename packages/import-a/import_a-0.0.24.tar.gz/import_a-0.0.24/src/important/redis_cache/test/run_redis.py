import os

from important.redis_cache.redis_client import RedisClient

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT", 6379)
redis_client = RedisClient(redis_host, redis_port)

# Test String Set/Get
key = "test_string"
value_in = "hello world"
redis_client.set(key, value_in)
value_out = redis_client.get(key)
assert value_in == value_out
redis_client.delete(key)

# Test Float Set/Get
key = "test_float"
value_in = 5.3
redis_client.set(key, value_in)
value_out = redis_client.get(key)
assert value_in == value_out
redis_client.delete(key)

# Test List Implementation
key = "test_list_key"
redis_client.list_rpush(key, 1)
redis_client.list_rpush(key, 2)
redis_client.list_rpush(key, "3")
assert redis_client.llen(key) == 3
assert redis_client.list_lpop(key) == 1
assert redis_client.list_range(key) == [2, "3"]
redis_client.delete(key)

# Test Set Implementation
key = "test_set_key"
assert redis_client.srandmember(key) == None
redis_client.sadd(key, "1")
redis_client.sadd(key, "2")
assert redis_client.smembers(key) == {"1", "2"}
assert redis_client.srandmember(key, 2) == ["1", "2"]
assert redis_client.srandmember(key) in ["1", "2"]
redis_client.srem(key, "2")
redis_client.srem(key, "3")
assert redis_client.sismember(key, "1")
assert not redis_client.sismember(key, "2")
redis_client.delete(key)

# test the default fallback in getter
if redis_client.exists("test"):
    redis_client.delete("test")
assert not redis_client.exists("test")
default = "empty"
value_out = redis_client.get("test", default=default)
assert value_out == default


# test the fetch method
def toUpper(s):
    return s.upper()

def return_param(param):
    return param


redis_client.set("key", "value")
assert redis_client.fetch("key", toUpper, None, "lower") == "value"
redis_client.delete("key")

assert redis_client.fetch("empty_key", toUpper, None, "lower") == "LOWER"
redis_client.delete("empty_key")

assert redis_client.fetch("empty_key_num", len, None, "hello") == 5
redis_client.delete("empty_key_num")

assert redis_client.fetch("empty_key_num", return_param, None, None) is None
redis_client.delete("empty_key_num")

for item in [0, False, [], {}, ""]:
    assert redis_client.fetch("empty_key_num", return_param, None, item) == item
    redis_client.delete("empty_key_num")

# Test mset and mget
redis_client.mset(
    {
        "key1": "1",
        "key2": "2",
        "key3": "3",
    }
)
assert redis_client.mget(["key1", "key2", "key3"]) == ["1", "2", "3"]
redis_client.set("key3", 3)
assert redis_client.mget(["key1", "key2", "key3"]) == ["1", "2", 3]
for k in ["key1", "key2", "key3"]:
    redis_client.delete(k)

# Test increment
key = "key"
redis_client.incr(key, 1)
assert redis_client.incr(key) == 2
redis_client.delete(key)

print("All checks passed")
