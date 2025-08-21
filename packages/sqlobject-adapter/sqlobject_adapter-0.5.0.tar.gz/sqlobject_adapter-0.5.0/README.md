SQLObject Adapter for PyCasbin
====

[![GitHub Action](https://github.com/officialpycasbin/sqlobject-adapter/workflows/build/badge.svg)](https://github.com/officialpycasbin/sqlobject-adapter/actions)
[![Coverage Status](https://coveralls.io/repos/github/officialpycasbin/sqlobject-adapter/badge.svg)](https://coveralls.io/github/officialpycasbin/sqlobject-adapter)
[![Version](https://img.shields.io/pypi/v/sqlobject_adapter.svg)](https://pypi.org/project/sqlobject_adapter/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/sqlobject_adapter.svg)](https://pypi.org/project/sqlobject_adapter/)
[![Pyversions](https://img.shields.io/pypi/pyversions/sqlobject_adapter.svg)](https://pypi.org/project/sqlobject_adapter/)
[![Download](https://static.pepy.tech/badge/sqlobject_adapter)](https://pypi.org/project/sqlobject_adapter/)
[![License](https://img.shields.io/pypi/l/sqlobject_adapter.svg)](https://pypi.org/project/sqlobject_adapter/)

SQLObject Adapter is the [SQLObject](http://www.sqlobject.org/index.html) adapter for [PyCasbin](https://github.com/casbin/pycasbin). With this library, Casbin can load policy from SQLObject supported database or save policy to it.

The current supported databases are:

- PostgreSQL
- MySQL
- SQLite
- Microsoft SQL Server
- Firebird
- Sybase
- MAX DB
- pyfirebirdsql

## Installation

```
pip install sqlobject_adapter
```

## Simple Example

```python
import sqlobject_adapter
import casbin

adapter = sqlobject_adapter.Adapter('sqlite:///test.db')

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


### Getting Help

- [PyCasbin](https://github.com/casbin/pycasbin)

### License

This project is licensed under the [Apache 2.0 license](LICENSE).
