# PySerialGps

[![Build](https://github.com/antoniovazquezblanco/pyserialgps/actions/workflows/build.yml/badge.svg)](https://github.com/antoniovazquezblanco/pyserialgps/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/pyserialgps)](https://pypi.org/project/pyserialgps/)
[![Snyk](https://snyk.io/advisor/python/pyserialgps/badge.svg)](https://snyk.io/advisor/python/pyserialgps)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE.md)

This module encapsulates detection and interaction with serial GPS modules.

It is purely implemented in Python, working OS independently.

## Usage

List GPS modules:

```python
import pyserialgps

modules = list(pyserialgps.list_modules())
print(modules)
```

You may use one of the returned GPS module objects or you may open a module from name and read data:

```python
module = GpsModule("COM9")
with module:
    while True:
        print(module.read())
```
