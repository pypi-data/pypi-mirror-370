import logging
import inspect
from typing import Any
from gc import collect
from types import FrameType


def get_frame_info() -> str:
    """Get frame info from the last frame before entering automation_logging modules"""

    nf_alog = False
    cf_alog = False
    frame = inspect.currentframe()
    frames: list[tuple[FrameType, str]] = []
    try:
        while frame:
            frames.append((frame, inspect.getfile(frame)))
            frame = frame.f_back
        frame_data: dict[str, Any] = {}
        for i in range(len(frames) - 1, 0, -1):
            cf = frames[i]
            nf = frames[i - 1]
            cf_alog = "automation_logging" in cf[1]
            nf_alog = "automation_logging" in nf[1]
            if nf_alog and not cf_alog:
                frame = cf[0]
                frame_data["module"] = inspect.getmodulename(inspect.getfile(frame))
                frame_data["lineno"] = inspect.getlineno(frame)
                frame_data["function"] = frame.f_code.co_name
                break
    finally:
        del frame
        for f, _ in frames:
            del f
        _ = collect()

    if len(frame_data) == 0:
        return "-"
    return f"{frame_data['module']}.{frame_data['function']}:{frame_data['lineno']}"


def add_logging_level(levelName: str, levelNum: int, methodName: str | None = None) -> None:
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    Parameters
    ----------
    levelName : str
        Name of the new logging level.

    levelNum : int
        Numeric value assigned to the new logging level.

    methodName : str, optional
        Name of the convenience method for the new logging level. If not specified,
        `levelName.lower()` is used.

    Returns
    -------
    None

    Examples
    --------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    Notes
    -----
    This method was extracted from:
    https://stackoverflow.com/q/2183233/35804945#35804945
    The behavior was modified to return None if the level is already defined
    instead of throwing an exception, allowing re-initialization of the log.
    """
    if not methodName:
        methodName = levelName.lower()

    if (
        hasattr(logging, levelName)
        or hasattr(logging, methodName)
        or hasattr(logging.getLoggerClass(), methodName)
    ):
        return None

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)
