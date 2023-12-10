import threading
import time
import traceback
from abc import ABC, abstractmethod
from logging import LogRecord

from ..constants import LOG3PY_MDC


class Resolver(ABC):
    """Abstract class for all resolvers"""

    @abstractmethod
    def resolve(self, record: LogRecord) -> dict[str, str] | str | None:
        raise NotImplementedError("Need to override in child class")


class DateTimeResolver(Resolver):
    """Resolver to handle datetime, mainly the formatting of it"""

    default_time_format = "%Y-%m-%d %H:%M:%S"
    default_msec_format = "%s,%03d"

    def __init__(
        self, time_fmt=default_time_format, msec_fmt=default_msec_format
    ):
        self.time_fmt = time_fmt
        self.msec_fmt = msec_fmt

    def resolve(self, record: LogRecord) -> str:
        datetime = time.localtime(record.created)
        s = time.strftime(self.default_time_format, datetime)
        return s


class LoggerResolver(Resolver):
    """Resolver to handle outputting the log level"""

    def __init__(self, field_name):
        self.field_name = field_name

    def resolve(self, record: LogRecord) -> str:
        match self.field_name:
            case "name":
                return record.name
            case "levelName":
                return record.levelname
            case "levelNumber":
                return str(record.levelno)
            case _:
                raise RuntimeWarning(
                    "Asking for bad log level field. 'name',  and 'number' allowed"
                )


class MessageResolver(Resolver):
    """Resolver to handle message, nothing for now, just fitting to framework"""

    def resolve(self, record: LogRecord) -> str:
        return record.msg


class MDCResolver(Resolver):
    """Resolver to handle outputting items from current_thread's dict"""

    def resolve(self, record: LogRecord) -> dict[str, str]:
        log3py_mdc = getattr(threading.current_thread(), LOG3PY_MDC)
        return {key: str(value) for key, value in log3py_mdc.items()}


class ExceptionResolver(Resolver):
    """Resolver to handle outputting info about the exception and stacktaces"""

    def __init__(self, field_name):
        self.field_name = field_name

    def resolve(self, record: LogRecord) -> str | None:
        if not record.exc_info:
            return None
        ex_type, ex, tb = record.exc_info
        match self.field_name:
            case "className":
                return str(ex_type.__name__) if ex_type else None
            case "message":
                return str(ex) if ex else None
            case "stackTrace":
                return str(traceback.format_tb(tb)) if tb else None
            case _:
                raise RuntimeWarning(
                    "Asking for bad exception field. 'message', 'className', and 'stackTrace' allowed"
                )
