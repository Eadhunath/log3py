# Log3Py
Formatter Logger for Python3

## Installation
### Test PyPi
```bash
pip install -i https://test.pypi.org/simple/ log3py
```
### From source
```bash
$ poetry build
$ python3 -m pip install dist/log3py-0.1.1-py3-none-any.whl
```
To install [poetry](https://python-poetry.org/) -> [Follow their installation guide](https://python-poetry.org/docs/#installation)
## Usage
### Simple logger
1. Import
```python
from log3py.log3py import Logger
```
2. Instantiate
```python
logger = Logger(__name__)
```
3. Log away! 
```python
logger.info("INFO log", extra={"abc": "123"})
logger.warning("WARN log")
logger.error("ERROR log")
try:
    raise FileNotFoundError("Custom exception message")
except Exception as e:
    logger.exception("EXCEPTION log", e)
```
### Using Stages

#### Idea
- Use stages to point to different execution levels of your code
- The stages are retained at a thread level
    - All modules, in the same thread, will have the same stages
    - All loggers, from the same thread will have the same stages
    - TODO : Making threads from a certain thread, will copy the stage of the main thread
- Stages need to be ended explicitly in a strictly reverse chronological order

#### Usage
1. Create stage enums for your codebase by extending `log_utils.Stage`
```python
class MyStage(log_utils.Stage):
    ONE = auto()
    TWO = auto()
    THREE = auto()
```
2. Use them with `log_utils.start_stage` and `log_utils.end_stage`
```python
from log3py import log_utils

log_utils.start_stage(MyStage.ONE)
logger.info("Log at stage ONE")
log_utils.start_stage(MyStage.TWO)
logger.info("Log at stage TWO, which is inside ONE")
log_utils.start_stage(MyStage.TWO)
log_utils.end_stage(MyStage.ONE)

log.utils.start_stage(MyStage.THREE)
logger.info("Log at stage THREE")
log.utils.end_stage(MyStage.THREE)
```

## Features
### Implemented
- Json Logger
- Stages in Logger

### Upcoming
- CSV Logger
- Log Timers

## Notes
- Extends Python's `logging.Logger`, so should be easily extendable and configurable very similarly

## Why am I making this?
- I want an easy goto logger, almost standardized in every project I make / work on
- I want to try and incorporate it at work projects, had to make them from scratch in 2-3 python projects now
- Learning experince
    -  First time learning how to package a python project
    -  First time understanding and using relative imports successfully
    -  Understanding CI/CD for python packages 
