# `yapeco`: Yet Another Python Envvar Config Object

A positively miniscule utility module to access `.env` (and otherwise environment-defined) config values in a structured way through a Python object. Created out of annoyance with not being able to autocomplete said envvars in my editor :^)

## Features & Limitations

- Case-insensitive + snake-case (i.e. `SNAKE_case`) field names
- Primitives such as `str`, `bool`, `int` and `float` are supported (no guarantees with `float` though, because, well... floating point)
- Assuming use of the above primitives, supports `Optional[*]` types (and by extension `Union[*,None]`), but no others from `typing`
- Default values through class variable assignment; assumed to be `None` for optional types
- Will (intentionally) raise a `RuntimeError` if there is no value set and no default value
- Common boolean config formats (i.e. `VAR=0/1/true/false/True/False`) work as expected

## Usage

Installation (PyPI):

```bash
pip3 install yapeco
```

A simple example:

```bash
# -- [mock environment] ---------------------------
API_KEY=abc123
DELAY_MSEC=18
FEATURE_A_ENABLED=false
FEATURE_B_ENABLED=1
```

```python
# --- contrived_config.py -------------------------

from yapeco import BaseEnvironment as Env

class Config(Env):
    api_key: str
    delay_msec: int
    feature_a_enabled: bool
    feature_a_flags: str = "-a -b -c"
    feature_b_enabled: bool
    feature_b_flags: Optional[str]


# --- main.py -------------------------------------

from config import Config

Config.api_key # "abc123"
Config.delay_msec # 18
Config.feature_a_enabled # False
Config.feature_a_flags # "-a -b -c"
Config.feature_b_enabled # True
Config.feature_b_flags # None

# ...
# API_KEY=def456
# FEATURE_B_ENABLED=false

Config.refresh() # update environment

Config.api_key # "def456"
Config.feature_b_enabled # False
```

## Development

Requires [poetry](https://python-poetry.org/).

```bash
poetry install  # install dependencies
poetry build  # build package
poetry run pytest .  # run tests
poetry run pyright .  # run type checks
```

## Feature Backburner

- Support implied types (type conversion currently depends on `cls.__annotations__`)

## Extra

Pedantic note:

> As in Smalltalk, classes themselves are objects. 
>
> —[The Literal Python Documentation](https://docs.python.org/3/tutorial/classes.html)
