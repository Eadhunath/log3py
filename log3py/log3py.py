import logging
import threading

from .constants import LOG3PY_MDC
from .formatters.json_formatter import JsonFormatter


class Logger(logging.Logger):
    """PyLogger"""

    def __init__(
        self,
        name: str | None,
        log_level: int = logging.NOTSET,
        log_handler: logging.Handler | None = logging.StreamHandler(),
        log_formatter: logging.Formatter | None = JsonFormatter(),
    ):
        if name:
            super().__init__(name, log_level)
        else:
            super().__init__("root", log_level)

        if log_handler:
            handler = log_handler
            if log_formatter:
                handler.setFormatter(log_formatter)
            self.addHandler(handler)

        current_thread = threading.current_thread()
        if not hasattr(current_thread, LOG3PY_MDC):
            setattr(current_thread, LOG3PY_MDC, {})


def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    return Logger(name)
