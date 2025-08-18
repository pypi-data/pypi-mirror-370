import os
import logging
from subprocess import call
from important.redis import (
    RedisController, RedisControllerAsync,
    CallableDict)
from important.location import CONF_DIR
from redis import Redis
from redis.asyncio import Redis as RedisAsync
import asyncio
from time import sleep


logging.info(
    "Make sure you have ran the 'test/start-env.sh' " +
    "before you start this test")


os.environ['REDIS_HOST'] = "localhost"


redis_client = Redis(host="localhost", db=0)
redis_client_async = RedisAsync(host="localhost", db=0)


control = RedisController.from_task(redis_client, task="channel_pop")


logging.debug(control)


def test_ttl_to_seconds():
    # let's try to reconstruct the ttl description to seconds
    assert RedisController.ttl_to_seconds(
        months=1, days=1, hours=1, minutes=1, seconds=1) == 2682061
    assert RedisController.ttl_to_seconds(
        minutes=1, seconds=1) == 61
    assert RedisController.ttl_to_seconds(
        hours=1, seconds=1) == 3601


def test_mk_key():
    channel_id = 1776
    user_id = 123123

    key = control.mk_key(channel_id=channel_id, user_id=user_id)
    assert key == f"chnl_pop:{channel_id}"
    try:
        key = control.mk_key(user_id=user_id)
        raise NotImplementedError("Failed to raise KeyError")
    except KeyError:
        logging.info("No worry, the above keyerror is a calculated error")
        assert True
    except Exception:
        raise NotImplementedError("Failed to raise KeyError")


def test_set_get():
    control[dict(channel_id=123123)] = 'dummy result'
    assert control[dict(channel_id=123123)] == 'dummy result'


def test_async_set_get():
    async def async_test():
        contorl = RedisControllerAsync.from_task(
            redis_client_async, task="channel_pop")
        await contorl.set(dict(channel_id=123123), 'dummy result')
        assert await contorl[dict(channel_id=123123)] == 'dummy result'
        # test the ttl
        logging.info("Let's count out 2.5 seconds to expire the key")
        sleep(2.5)
        assert await contorl[dict(channel_id=123123)] is None
    asyncio.run(async_test())


redis_client.set("some_global", 1, ex=10)


def func_builder(
    in_func_arg1,
    in_func_arg2,
    in_func_key1=None,
    in_func_key2=1
):
    logging.debug(f"loading func_builder with {locals()}")

    def func(*args, **kwargs):
        return dict(
            in_func_arg1=in_func_arg1,
            in_func_arg2=in_func_arg2,
            in_func_key1=in_func_key1,
            in_func_key2=in_func_key2,
            args=args,
            kwargs=kwargs,
            some_global=int(redis_client.get("some_global"))
        )
    return func


def test_callable_dict(caplog):
    callable_dict = CallableDict(
        client=redis_client,
        class_map=dict(func_builder=func_builder),
        delay=1,
    )
    for i in range(20):
        callable_dict.set("func_builder",
                          "key1", "key2",
                          in_func_key1="key3",
                          in_func_key2="key3")
        callable = callable_dict.get("func_builder",
                                     "key1", "key2",
                                     in_func_key1="key3",
                                     in_func_key2="key3")

        result = callable(i+1)

        assert result == dict(
            in_func_arg1="key1",
            in_func_arg2="key2",
            in_func_key1="key3",
            in_func_key2="key3",
            args=(i+1,),
            kwargs={},
            some_global=1,
        )

    # no redis checking
    assert str(caplog.text).count("🍄") == 0
    # 1 initialization
    assert str(caplog.text).count("✨") == 1

    sleep(1.1)
    for i in range(2):  # to test the delay prolong is working
        callable = callable_dict.get("func_builder",
                                     "key1", "key2",
                                     in_func_key1="key3",
                                     in_func_key2="key3")

    assert callable("local_expired") == dict(
        in_func_arg1="key1",
        in_func_arg2="key2",
        in_func_key1="key3",
        in_func_key2="key3",
        args=("local_expired",),
        kwargs={}, some_global=1,
    )
    # checking redis when local expired
    assert str(caplog.text).count("🍄") == 1

    callable_dict.delete("func_builder",
                         "key1", "key2",
                         in_func_key1="key3",
                         in_func_key2="key3")

    # change the global variable in redis
    # WE DO THIS TEST BECAUSE WE WANT IT TO RELOAD THE FUNCTION
    # WHEN THE GLOBAL VARIABLE CHANGES OR CONFIG IN DATABASE CHANGES

    redis_client.set("some_global", 2, ex=10)
    sleep(1.1)
    for i in range(3):
        callable = callable_dict.get("func_builder",
                                     "key1", "key2",
                                     in_func_key1="key3",
                                     in_func_key2="key3")

    assert callable("test_global") == dict(
        in_func_arg1="key1",
        in_func_arg2="key2",
        in_func_key1="key3",
        in_func_key2="key3",
        args=("test_global",),
        kwargs={},
        some_global=2,
    )
    assert str(caplog.text).count("✨") == 2
    assert str(caplog.text).count("🍄") == 2
