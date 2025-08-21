Redis Adapter for PyCasbin
====

[![build](https://github.com/officialpycasbin/redis-adapter/actions/workflows/build.yml/badge.svg)](https://github.com/officialpycasbin/redis-adapter/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/officialpycasbin/redis-adapter/badge.svg)](https://coveralls.io/github/officialpycasbin/redis-adapter)
[![Version](https://img.shields.io/pypi/v/casbin_redis_adapter.svg)](https://pypi.org/project/casbin_redis_adapter/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/casbin_redis_adapter.svg)](https://pypi.org/project/casbin_redis_adapter/)
[![Pyversions](https://img.shields.io/pypi/pyversions/casbin_redis_adapter.svg)](https://pypi.org/project/casbin_redis_adapter/)
[![Download](https://static.pepy.tech/badge/casbin_redis_adapter)](https://pypi.org/project/casbin_redis_adapter/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

Redis Adapter is the [Redis](https://redis.io/) adapter for [PyCasbin](https://github.com/casbin/pycasbin). With this library, Casbin can load policy from redis or save policy to it.

## Installation

```
pip install casbin_redis_adapter
```

## Simple Example

```python
import casbin_redis_adapter
import casbin

adapter = casbin_redis_adapter.Adapter('localhost', 6379)

e = casbin.Enforcer('path/to/model.conf', adapter, True)

sub = "alice"  # the user that wants to access a resource.
obj = "data1"  # the resource that is going to be accessed.
act = "read"  # the operation that the user performs on the resource.

if e.enforce(sub, obj, act):
    # permit alice to read data1casbin_sqlalchemy_adapter
    pass
else:
    # deny the request, show an error
    pass
```

## Configuration

`Adapter()` enable decode_responses by default and supports any Redis parameter configuration.

To use casbin_redis_adapter, you must provide the following parameter configuration

- `host`: address of the redis service
- `port`: redis service port

The following parameters are provided by default

- `db`: redis database, default is `0`
- `username`: redis username, default is `None`
- `password`: redis password, default is `None`
- `key`: casbin rule to store key, default is `casbin_rules`

For more parameters, please follow [redis-py](https://redis.readthedocs.io/en/stable/connections.html#redis.Redis)

### Getting Help

- [PyCasbin](https://github.com/casbin/pycasbin)

### License

This project is licensed under the [Apache 2.0 license](LICENSE).
