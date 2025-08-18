from redis import Redis
from redis.asyncio import Redis as RedisAsync
from important.location import CONF_DIR
from yaml import safe_load
from gallop.config import BaseConfig
from typing import (
    Dict, Any, Optional, Callable
)
import uuid
import json
import logging
import hashlib
from datetime import timedelta, datetime


class RedisController:
    """
    A redis controller to set and retrieve data conveniently
    with complex redis key pattern, according to the configuration
    at redis.yaml
    """

    def __init__(
        self,
        client: Redis,
        conf: Dict[str, Any],
    ):
        """
        client: redis.Redis, we don't rewrite the redis client
        conf: Dict[str, Any], the configuration of the redis controller
            some must keys:
                pattern: str, the pattern of the redis key
                pattern_kwargs: List[str], the kwargs of the pattern
        """
        self.client = client
        self.config = BaseConfig(**conf)
        for key in ["pattern", "pattern_kwargs"]:
            if key not in self.config:
                raise KeyError(f"{key} not in {self.config}")
        self.ttl_seconds = None

    @classmethod
    def from_task(
        cls,
        client: Redis,
        task: str,
        conf_path: Optional[str] = None,
    ) -> "RedisController":
        f"""
        Instantiate RedisController from task name
        task: key name under 'redis_controller' at {CONF_DIR / "redis.yaml"}
        conf_path: path to the redis configuration file,
            we have default options, but 
        """
        conf_path = CONF_DIR/"redis.yaml" if conf_path is None else conf_path
        with open(conf_path, "r") as f:
            conf = safe_load(f)
        if task in conf['redis_controller']:
            config = conf['redis_controller'][task]
            return cls(client, config)
        else:
            logging.warning(f"🌀 Task {task} not found in redis.yaml")
            raise KeyError(f"Task {task} not found in redis.yaml")

    def __repr__(self,) -> str:
        return f"RedisController({self.config.pattern})"

    @staticmethod
    def ttl_to_seconds(**time_kwargs) -> int:
        """
        Convert ttl key value pairs to seconds
        """
        seconds = 0
        if 'months' in time_kwargs:
            seconds += time_kwargs['months']*30*24*60*60
        if 'days' in time_kwargs:
            seconds += time_kwargs['days']*24*60*60
        if 'hours' in time_kwargs:
            seconds += time_kwargs['hours']*60*60
        if 'minutes' in time_kwargs:
            seconds += time_kwargs['minutes']*60
        if 'seconds' in time_kwargs:
            seconds += time_kwargs['seconds']

        # check if any extra keys
        for key in time_kwargs:
            if key not in ['months', 'days', 'hours', 'minutes', 'seconds']:
                logging.error("supported keys are: months, days, hours, " +
                              "minutes, seconds")
                raise KeyError(f"❓ ttl_to_seconds: unknown key {key}")
        return seconds

    def mk_key(self, **kwargs) -> str:
        """
        Make key from kwargs.
        """
        try:
            return self.config.pattern.format(**kwargs)
        except KeyError as e:
            logging.error(f"❓ 🔑 KeyError: {e}, please input keys as")
            logging.error(self.config["pattern_kwargs"])
            raise e

    def __setitem__(self, kwargs: Dict[str, Any], value: str):
        """
        Set value to redis
        According to the pattern in config
        """
        key = self.mk_key(**kwargs)
        self.client.set(key, value, ex=self.ttl_seconds)
        return key

    def __getitem__(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Get value from redis
        According to the pattern in config
        """
        key = self.mk_key(**kwargs)
        value = self.client.get(key)
        if value is not None:
            return value.decode()
        return None


class RedisControllerAsync(RedisController):
    """
    Async version of RedisController
    """

    def __init__(self,
                 client: RedisAsync,
                 conf: Dict[str, Any],
                 ):
        """
        client: redis.Redis, we don't rewrite the redis client
        conf: Dict[str, Any], the configuration of the redis controller
            some must keys:
                pattern: str, the pattern of the redis key
                pattern_kwargs: List[str], the kwargs of the pattern
        """
        self.client = client
        self.config = BaseConfig(**conf)
        for key in ["pattern", "pattern_kwargs"]:
            if key not in self.config:
                raise KeyError(f"{key} not in {self.config}")
        if 'ttl' in self.config:
            self.ttl_seconds = self.ttl_to_seconds(**self.config.ttl)
        else:
            self.ttl_seconds = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def set(self, kwargs: Dict[str, Any], value: str):
        """
        Set value to redis
        According to the pattern in config
        """
        key = self.mk_key(**kwargs)
        await self.client.set(key, value, ex=self.ttl_seconds)
        return key

    async def __getitem__(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Get value from redis
        According to the pattern in config
        """
        key = self.mk_key(**kwargs)
        value = await self.client.get(key)
        if value is not None:
            return value.decode()
        return None


class CallableDictMixin:
    def __repr__(self, ) -> str:
        return f"CallableDictMixin({self.class_map.keys()})"

    def register(self, name: str, cls: Callable):
        """
        Register a class, function
        """
        self.class_map[name] = cls

    def hexify_conf(self, *args, **kwargs):
        """
        Hexify the configuration
        """
        data = dict(
            args=args,
            kwargs=kwargs,
        )
        data_string = json.dumps(data)

        return self.hasher(
            data_string.encode()).hexdigest()[0:8]

    def mk_func_pk(
        self,
        class_name: str,
        *args, **kwargs,
    ):
        """
        Make a function primary key
        """
        function_pk = f"{class_name}:{self.hexify_conf(*args, **kwargs)}"
        return function_pk

    def mk_func_pk_1st(
        self,
        class_name: str,
        *args, **kwargs,
    ):
        """
        Make a function primary key
        """
        function_pk = f"{class_name}:{self.hexify_conf(*args, **kwargs)}"
        if function_pk not in self.function_pks:
            self.function_pks[function_pk] = dict(
                class_name=class_name,
                args=args,
                kwargs=kwargs,
            )
        return function_pk

    def __setitem__(
            self, function_pk: str, callable: Callable):
        """
        Set value to redis
        According to the pattern in config
        """
        self.callables[function_pk] = callable

    def set(self, class_name: str, *args, **kwargs) -> Callable:
        """
        Set the callable
        """
        function_pk = self.mk_func_pk_1st(class_name, *args, **kwargs)
        return self[function_pk]


class CallableDict(RedisController, CallableDictMixin):
    """
    A class to store callable object in redis
    """

    def __init__(
        self,
        client: Redis,
        class_map: Dict[str, Callable] = dict(),
        delay: int = None,
        ttl: Dict[str, int] = dict(
            minutes=2, seconds=30,
        ),
        conf: Optional[Dict[str, Any]] = None,
    ):
        """
        client: redis.Redis, we don't rewrite the redis client
        class_map: Dict[str, Callable], the class map
        delay: int, the span of seconds we don't recheck with redis
        ttl: Dict[str, int], the ttl of redis key
        conf: Optional[Dict[str, Any]],
            the configuration of the redis controller
        """
        if conf is None:
            base_conf = BaseConfig.from_yaml(CONF_DIR/"redis.yaml")
            conf = base_conf["redis_controller"]["callable_dict"]
        super().__init__(client, conf)
        self.class_map = class_map
        self.callables = dict()
        self.function_pks = dict()
        self.uuid_pk_map = dict()
        self.delay_map = dict()
        self.hasher = hashlib.sha256
        ttl = BaseConfig(**ttl)
        self.ttl_seconds = self.ttl_to_seconds(**ttl)
        self.delay = delay

    def reload_callable(self, function_pk: str,) -> Callable:
        function_details = self.function_pks[function_pk]
        class_name = function_details["class_name"]
        args = function_details["args"]
        kwargs = function_details["kwargs"]
        class_ = self.class_map[class_name]
        callable = class_(*args, **kwargs)
        self.callables[function_pk] = callable
        return callable

    def reload(self, function_pk: str,) -> Callable:
        """
        Reload the callable, also register the uuid
        """
        logging.warning(f"✨ Initializing: {function_pk}")
        callable = self.reload_callable(function_pk)
        uuid_pk = str(uuid.uuid4())[:8]

        # set local expire with delay
        if self.delay is not None:
            local_expire = datetime.now() + \
                timedelta(seconds=self.delay)
            self.delay_map[uuid_pk] = local_expire

        self.uuid_pk_map[function_pk] = uuid_pk
        self.client.set(self.mk_key(
            function_pk=function_pk,
            uuid_pk=uuid_pk,
        ), 1, ex=self.ttl_seconds)
        return callable

    def __getitem__(self, function_pk: str) -> Optional[Callable]:
        """
        Get value from redis
        According to the pattern in config
        """
        # uuid is to check destory/ update triggered from redis
        uuid_pk = self.uuid_pk_map.get(function_pk)
        if uuid_pk is None:
            return self.reload(function_pk=function_pk)

        # has uuid but don't have such key in redis
        if self.delay is not None:
            if datetime.now() < self.delay_map.get(uuid_pk, datetime.now()):
                # not checking redis
                return self.callables[function_pk]

        # check redis
        redis_key = self.mk_key(
            function_pk=function_pk,
            uuid_pk=uuid_pk,
        )
        logging.debug("🍄 checking redis")
        if self.client.exists(redis_key) == 0:
            if self.delay is not None:
                if uuid_pk in self.delay_map:
                    del self.delay_map[uuid_pk]
            return self.reload(function_pk=function_pk)

        # prolong delay
        if self.delay is not None:
            self.delay_map[uuid_pk] = datetime.now() + \
                timedelta(seconds=self.delay)
        return self.callables[function_pk]

    def get(self, class_name: str, *args, **kwargs) -> Callable:
        """
        Get the callable
        """
        function_pk = self.mk_func_pk(class_name, *args, **kwargs)
        if function_pk not in self.function_pks:
            # raise KeyError(f"{function_pk} not in {self.function_pks}")
            self.set(class_name, *args, **kwargs)
        return self[function_pk]

    def delete(self, class_name: str, *args, **kwargs):
        """
        Delete the callable
        """
        function_pk = self.mk_func_pk(class_name, *args, **kwargs)
        redis_key = self.mk_key(function_pk=function_pk, uuid_pk="*")
        # delete redis key
        for key in self.client.keys(redis_key):
            logging.warning(f'🗡 [CACHE DELETE]: {key}')
            self.client.delete(key)


class CallableDictAsync(CallableDictMixin):
    def __init__(
        self,
        client: RedisAsync,
        class_map: Dict[str, Callable] = dict(),
        ttl: Dict[str, int] = dict(
            minutes=0,
            seconds=0,
        ),
        delay: int = None,
        conf: Optional[Dict[str, Any]] = None,
    ):
        if conf is None:
            base_conf = BaseConfig.from_yaml(CONF_DIR/"redis.yaml")
            conf = base_conf["redis_controller"]["callable_dict"]
        self.conf = conf
        self.ttl_seconds = RedisController.ttl_to_seconds(**conf["ttl"])
        self.client = client
        self.class_map = class_map
        self.callables = dict()
        self.function_pks = dict()
        self.uuid_pk_map = dict()
        self.delay_map = dict()
        self.hasher = hashlib.sha256
        self.ttl_seconds = RedisController.ttl_to_seconds(**ttl)
        self.delay = delay

    async def reload_callable(self, function_pk: str,) -> Callable:
        function_details = self.function_pks[function_pk]
        class_name = function_details["class_name"]
        args = function_details["args"]
        kwargs = function_details["kwargs"]
        class_ = self.class_map[class_name]
        callable = await class_(*args, **kwargs)
        self.callables[function_pk] = callable
        return callable

    async def reload(self, function_pk: str,) -> Callable:
        """
        Reload the callable, also register the uuid
        """
        logging.warning(f"✨ Initializing: {function_pk}")
        callable = await self.reload_callable(function_pk)
        uuid_pk = str(uuid.uuid4())[:8]

        # set local expire with delay
        if self.delay is not None:
            local_expire = datetime.now() + \
                timedelta(seconds=self.delay)
            self.delay_map[uuid_pk] = local_expire

        self.uuid_pk_map[function_pk] = uuid_pk
        await self.client.set(
            f"callable:{function_pk}:{uuid_pk}",
            1, ex=self.ttl_seconds)
        return callable

    async def get(self, class_name: str, *args, **kwargs) -> Callable:
        """
        Get the callable
        """
        function_pk = self.mk_func_pk_1st(class_name, *args, **kwargs)

        # uuid is to check destory/ update triggered from redis
        uuid_pk = self.uuid_pk_map.get(function_pk)
        if uuid_pk is None:
            return await self.reload(function_pk=function_pk)

        # has uuid but don't have such key in redis
        if self.delay is not None:
            if datetime.now() < self.delay_map.get(uuid_pk, datetime.now()):
                # not checking redis
                return self.callables[function_pk]

        # check redis
        redis_key = f"callable:{function_pk}:{uuid_pk}"

        logging.debug("🍄 checking redis")
        if await self.client.exists(redis_key) == 0:
            if self.delay is not None:
                if uuid_pk in self.delay_map:
                    del self.delay_map[uuid_pk]
            return await self.reload(function_pk=function_pk)

        # prolong delay
        if self.delay is not None:
            self.delay_map[uuid_pk] = datetime.now() + \
                timedelta(seconds=self.delay)
        return self.callables[function_pk]

    async def delete(self, class_name: str, *args, **kwargs):
        """
        Delete the callable
        """
        function_pk = self.mk_func_pk(class_name, *args, **kwargs)
        redis_key = self.mk_key(function_pk=function_pk, uuid_pk="*")

        for key in await self.client.keys(redis_key):
            logging.warning(f'🗡 [CACHE DELETE]: {key}')
            await self.client.delete(key)

    def mk_key(self, **kwargs) -> str:
        """
        Make key from kwargs.
        """
        try:
            return self.conf.pattern.format(**kwargs)
        except KeyError as e:
            logging.error(f"❓ 🔑 KeyError: {e}, please input keys as")
            logging.error(self.conf["pattern_kwargs"])
            raise e
