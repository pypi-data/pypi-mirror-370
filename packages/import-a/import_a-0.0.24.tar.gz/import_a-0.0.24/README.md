# important
> 🎁 Import Ant 🐜 The folder of python functions and classes we can import

[![PyPI version](https://img.shields.io/pypi/v/import-a)](https://pypi.org/project/import-a/)
[![test](https://github.com/loopsocial/important/actions/workflows/test.yml/badge.svg)](https://github.com/loopsocial/important/actions/workflows/test.yml) [![pypi build](https://github.com/loopsocial/important/actions/workflows/publish.yml/badge.svg)](https://github.com/loopsocial/important/actions/workflows/publish.yml)

![import ant avatar](import-ant.jpeg)

## 📦 Installation

Import Ant is meant to be as light weight as possible, say you want to import some re-useable code for redis, but you don't want to install every dependency for kafka, snowflake, etc. You can install just the redis part with out worring to manage the distribution about anything else.

### Very simple version
```shell
pip install import-a
```

### With other distributions
```shell
pip install "import-a[redis]"
```

or

```shell
pip install "import-a[kafka,redis]"
```

```shell
pip install "import-a[kafka,snowflake]"
```

or just get greedy and install everything, with a specified version 🚀🏎💣🔪🔫🔨🧨🧱🧲🧪🧬🧯🧰

```shell
pip install "import-a[all]==0.0.1"
```


## 🔌 Connectors
### ❄️ Snowflake
```python
from important.snowflake import SnowFlakeDatabricks
sf = SnowFlakeDatabricks.from_config()

# read data into a pandas dataframe
df = sf("SELECT * FROM some_table")
```
### 🍄 Redis
```python
from important.redis import Redis, RedisAsync, RedisController
```
#### Vanilla Redis
```python
# connect to redis
redis_client = Redis(host="localhost", db=0)

control = RedisController.from_task(redis_client, task="channel_pop")

# save data by key
control[dict(channel_id=137, user_id=424242)] = "Some string data"
```
#### Async Redis
```python
redis_client = RedisAsync(host="localhost", db=0)

control = RedisControllerAsync.from_task(
    redis_client, task="channel_pop")

# save data by key, sadly the await expression doesn't support the [] syntax
await control.set(dict(channel_id=137, user_id=424242), "Some string data")

# get data by key
await control[dict(channel_id=137, user_id=424242)]
```
