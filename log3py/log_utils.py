import threading
from enum import Enum

from .constants import LOG3PY_MDC
from .log3py import Logger

_LOGGER = Logger(__name__)


class Stage(Enum):
    """Inheritable enum to make Enums for stages in the code pipeline."""

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.__class__.__name__) + "." + str(self.name)


class Stages(list[Stage]):
    """Not really for public use, just a typed list for Stage enums."""

    def __repr__(self) -> str:
        return "/".join(map(str, self))

    def __str__(self) -> str:
        return self.__repr__()


def _get_mdc_from_thread():
    current_thread = threading.current_thread()
    if hasattr(current_thread, LOG3PY_MDC):
        return getattr(current_thread, LOG3PY_MDC)
    else:
        raise LookupError("No LOG3PY_MDC in thread exists")


def start_stage(stage_name: Stage) -> None:
    """Marks start of a stage in the execution of the code

    If the Stage does not exist in the current list, it is added into it.
    If it already exists, a warning is given no stage action is taken

    Args:
        stage_name (Stage): Stage enum to indicate beginning of a stage
    """
    log3py_mdc = _get_mdc_from_thread()
    if not "stage" in log3py_mdc:
        log3py_mdc["stage"] = Stages()
    stages = log3py_mdc["stage"]

    if not stage_name in stages:
        stages.append(stage_name)
        _LOGGER.debug("START_STAGE %s", str(stage_name))
    else:
        _LOGGER.warning(
            "Trying to add Stage %s more than once. Cannot allow!",
            str(stage_name),
        )


def end_stage(stage_name: Stage) -> None:
    """Marks the end of a stage.

    It is mandatory that for a stage to be "ended"
        - it has to have started.
        - it needs to be the latest stage, not an intermediate stage
            - this means, stages NEED to be closed in a reverse chronological order
    Else a warning is given and no stage operations are taken

    Args:
        stage_name (Stage): Stage enum to be ended
    """
    log3py_mdc = _get_mdc_from_thread()
    if not "stage" in log3py_mdc:
        _LOGGER.warning("No stages ever started to close. Cannot allow!")
        return

    stages = log3py_mdc["stage"]
    if stages[-1] == stage_name:
        stages.pop(-1)
        _LOGGER.debug("START_END %s", str(stage_name))
    else:
        _LOGGER.warning(
            "Trying to remove a Stage %s which is not the last stage. Cannot allow!",
            stage_name,
        )
