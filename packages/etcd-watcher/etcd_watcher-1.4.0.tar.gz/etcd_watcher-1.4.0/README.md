# etcd-watcher

[![tests](https://github.com/officialpycasbin/etcd-watcher/actions/workflows/release.yml/badge.svg)](https://github.com/officialpycasbin/etcd-watcher/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/officialpycasbin/etcd-watcher/badge.svg)](https://coveralls.io/github/officialpycasbin/etcd-watcher)
[![Version](https://img.shields.io/pypi/v/etcd-watcher.svg)](https://pypi.org/project/etcd-watcher/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/etcd-watcher.svg)](https://pypi.org/project/etcd-watcher/)
[![Pyversions](https://img.shields.io/pypi/pyversions/etcd-watcher.svg)](https://pypi.org/project/etcd-watcher/)
[![Download](https://img.shields.io/pypi/dm/etcd-watcher.svg)](https://pypi.org/project/etcd-watcher/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

Etcd Watcher is the [Etcd](https://github.com/coreos/etcd) watcher for [pycasbin](https://github.com/casbin/pycasbin). With this library, Casbin can synchronize the policy with the database in multiple enforcer instances.

## Installation

    pip install etcd-watcher

## Simple Example

```python
import casbin
from etcd_watcher import new_watcher

def update_callback_func(event):
    ...

watcher = new_watcher(endpoints=["localhost", 2379], keyname="/casbin")
watcher.set_update_callback(update_callback_func)

e = casbin.Enforcer(
	get_examples("rbac_model.conf"), get_examples("rbac_policy.csv")
)

e.set_watcher(watcher)
# update_callback_func will be called
e.save_policy()
```

## Getting Help

- [Casbin](https://github.com/casbin/pycasbin)

## License

This project is under Apache 2.0 License. See the [LICENSE](LICENSE) file for the full license text.
