"""
Core logging functionality for automation logging library.
"""

from threading import Lock
from logging import Logger
from typing import Any
import logging
import os
import shutil
import sys
import getpass
import traceback
import platform
from enum import IntEnum
from datetime import datetime, timedelta

from .utils import add_logging_level
from .screenshots import ScreenshotManager
from .global_logger import set_global_log


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    STAT = 3
    WARNING = 4
    ERROR = 5
    EXCEPTION = 6
    CRITICAL = 7

    def to_logging_level(self):
        """Returns the corresponding logging level from the logging module."""
        if self == LogLevel.DEBUG:
            return logging.DEBUG
        elif self == LogLevel.INFO:
            return logging.INFO
        elif self == LogLevel.STAT:
            return logging.INFO + 5
        elif self == LogLevel.WARNING:
            return logging.WARNING
        elif self == LogLevel.ERROR:
            return logging.ERROR
        elif self == LogLevel.EXCEPTION:
            return logging.ERROR  # logging.exception also uses logging.ERROR level
        elif self == LogLevel.CRITICAL:
            return logging.CRITICAL
        else:
            raise ValueError(f"Unknown LogLevel: {self}")


class AutomationLogger:
    """
    Class used to log the program execution to a file

    Examples
    --------
    >>> log_dir = "./tests/Logs"
    >>> log = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True)
    >>>
    >>> log.info("Start of program")
    >>> for i in range(10):
    >>>     log.info(f"Iteration index: {i}")
    >>> try:
    >>>     error = 1 / 0
    >>> except Exception as exc:
    >>>     log.exception(f"Exception caught: {repr(exc)}")
    >>> log.info("End of program")
    """

    def __init__(
        self,
        script_path: str,
        log_dir: str | None = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        max_logs: int = 60,
        max_days: int = 30,
        encoding: str = "utf-8",
        as_logging_root: bool = False,
        as_global_log: bool = True,
        level_threshold: LogLevel = LogLevel.INFO,
    ) -> None:
        """
        Initializes a AutomationLogger object for standardized logging in a script or robot.

        This class introduces a log level called "STAT" (short for statistics), designed
        for dumping dictionaries of information usable with logging solutions (e.g., ELK stack).

        Parameters
        ----------
        script_path : str
            Absolute path of the script calling this function. Use __file__ or
            os.path.abspath(__file__) to retrieve the path.

        log_dir : str, optional
            Path to the directory where logs will be stored. If None, logs will be stored
            in the directory script_path/Logs.

        log_to_console : bool, optional
            If True, log messages will also appear on the console.

        log_to_file : bool, optional
            If True, creates a log file and writes to it

        max_logs : int, optional
            Number of log files to retain in the log directory.

        max_days : int, optional
            Number of days of log history to retain in the log folder.

        encoding : str, optional
            Encoding used by the logger object.

        as_logging_root: bool, optional
            Flag that controls if the root logger of the `logging` library will use the same configurations as AutomationLogger
            When set, code that uses `logging` functions (e.g info(), error()...) will follow the AutomationLogger configuration

            One reason to keep it as False is to avoid polluting the log with messages from packages that use `logging` internally

        as_global_log: bool, optional
            Flag that controls if this logger object will be set as the module's global logger.
            When set, it will be possible to use the module's logging functions without using set_global_log

        level_threshold: LogLevel
            Lowest log level that will be logged, Any level less severe than the current one will be ignored.
            The order from least severe to most severe: debug, info, state, warning, error, exception, critical

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If `mode` passed is invalid
        ValueError
            If `max_logs` is not a positive integer
        ValueError
            If `max_days` is not a positive integer

        Examples
        --------
        >>> import logging
        >>> from automation_logging import AutomationLogger
        >>>
        >>> log_dir = "./tests/Logs"
        >>> logger = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True, set_logging_root = True)
        >>> logger.info("This INFO message was written using a AutomationLogger method")
        >>> logging.info("This INFO message was written using a logging function and was written to the same file")
        """

        if not isinstance(max_logs, int) or max_logs <= 0:
            raise ValueError("max_logs parameter must be a positive integer")
        if not isinstance(max_days, int) or max_days <= 0:
            raise ValueError("max_days parameter must be a positive integer")
        if not isinstance(level_threshold, LogLevel):
            raise ValueError("level_threshold must be a LogLevel")
        if log_to_console is False and log_to_file is False:
            raise ValueError("log_to_console and log_to_file cannot be both False")

        log_dir = log_dir or os.path.join(os.path.dirname(script_path), "Logs")
        script_name = os.path.basename(script_path)
        script_name_no_ext = os.path.splitext(script_name)[0]
        log_name = f"{script_name_no_ext}.log"

        self.log_dir: str = log_dir
        self.log_name: str = log_name
        self.threshold: LogLevel = level_threshold
        # Include private mutex to make this class thread-safe
        self._mutex: Lock = Lock()

        # Initialize screenshot manager
        self._screenshot_manager: ScreenshotManager | None = None

        try:
            # Delete older files and create current directory
            if log_to_file:
                self.log_dir = self._clear_log_dir(
                    log_dir=log_dir,
                    max_logs=max_logs,
                    max_days=max_days,
                )
                self.log_file: str = os.path.join(self.log_dir, log_name)
            else:
                self.log_file = ""

            # Getting system and user information to include in the log
            system_name = platform.node()
            user_domain = os.environ.get("USERDOMAIN", "-")
            if user_domain == "-":
                complete_user = getpass.getuser()
            else:
                complete_user = f"{user_domain}\\{getpass.getuser()}"
            # Configuring the logger object
            # include -10s to levelname to make all messages start at the same column
            _log_format = (
                f"%(asctime)s | {system_name} | {complete_user} | %(name)s"
                " | %(levelname)-10s | %(message)s"
            )

            self._logger: Logger = logging.getLogger(name=script_name)
            self._logger.setLevel(level_threshold.to_logging_level())

            self._logger.handlers = []  # Reset handlers

            # Formatter
            formatter = logging.Formatter(_log_format, datefmt="%Y-%m-%d %H:%M:%S%z")

            # log to file
            if log_to_file:
                file_handler = logging.FileHandler(self.log_file, encoding=encoding)
                file_handler.setLevel(level_threshold.to_logging_level())
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)

            # print in console
            if log_to_console:
                self._logger.addHandler(logging.StreamHandler(sys.stdout))

            # Create new log level
            add_logging_level("STAT", LogLevel.STAT.to_logging_level())

            if as_logging_root:
                logging.root = self._logger
                logging.getLogger().handlers = self._logger.handlers
                logging.getLogger().setLevel(self._logger.level)

            if as_global_log:
                set_global_log(self)

            # Initialize screenshot manager after log directory is set
            if log_to_file:
                self._screenshot_manager = ScreenshotManager(self.log_dir, self._logger)

            self.info("AutomationLogger object instantiated")
        except Exception as exc:
            print(f"Error when instantiating AutomationLogger object: {repr(exc)}")
            error_traceback = traceback.format_exc()
            print(error_traceback)
            print("Writing the error inside log_error.txt")
            file_path = os.path.abspath("log_error.txt")
            with open(file_path, "w+", encoding="utf-8") as file:
                _ = file.write(
                    f"Error when instantiating AutomationLogger object: {repr(exc)}\n"
                )
                _ = file.write(
                    "----------------------------------------------------------\n"
                )
                _ = file.write(error_traceback)
            raise exc

    def _clear_log_dir(self, log_dir: str, max_logs: int, max_days: int) -> str:
        """
        Deletes old logs and creates the directory for the current log.

        Parameters
        ----------
        log_dir : str
            Path to the directory where logs will be stored. If None, logs will be stored
            in the directory specified during initialization.

        max_logs : int
            Number of log files to retain in the log directory.

        max_days : int
            Number of days of log history to retain in the log folder.

        Returns
        -------
        str
            String with the folder path for the current execution.
        """

        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("exec_%Y-%m-%d_%H-%M-%S")
        # Delete older execution if limit of executions has been reached
        # Condition 1) Delete based on the number of log files
        files = sorted(
            [
                x
                for x in os.listdir(log_dir)
                if os.path.isdir(os.path.join(log_dir, x)) and "exec_" in x.lower()
            ]
        )
        num_delete = max(len(files) - max_logs + 1, 0)
        for i in range(num_delete):
            try:
                shutil.rmtree(os.path.join(log_dir, files[i]))
            except PermissionError as exc:
                # In case of permission error when deleting files, instead of crashing the program,
                # the files won't be deleted (need to be manually deleted)
                print(f"Error when deleting old log files: {repr(exc)}")

        # Condition 2) Delete based on date in the file name and a cutoff date
        cutoff_date = datetime.now() - timedelta(days=max_days)
        files = [
            x
            for x in os.listdir(log_dir)
            if os.path.isdir(os.path.join(log_dir, x)) and "exec_" in x.lower()
        ]
        for file in files:
            try:
                file_date = datetime.strptime(file, "exec_%Y-%m-%d_%H-%M-%S")
                if file_date <= cutoff_date:
                    shutil.rmtree(os.path.join(log_dir, file))
            except Exception as exc:
                print(f"Error when deleting old log files: {repr(exc)}")

        log_dir = os.path.join(log_dir, timestamp)

        # Create log dir for the current execution
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _write(self, message: str, level: LogLevel) -> None:
        """Writes the message to the log file with the given level
        If the level is lower than the threshold, the message is not written

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None
        """

        if level < self.threshold:
            return None

        with self._mutex:
            if level == LogLevel.DEBUG:
                self._logger.debug(message)
            elif level == LogLevel.INFO:
                self._logger.info(message)
            elif level == LogLevel.STAT:
                self._logger.stat(message)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            elif level == LogLevel.WARNING:
                self._logger.warning(message)
            elif level == LogLevel.ERROR:
                self._logger.error(message)
            elif level == LogLevel.EXCEPTION:
                self._logger.exception(message)
            elif level == LogLevel.CRITICAL:
                self._logger.critical(message)

    def debug(self, message: str) -> None:
        """Writes the message to the log file with level DEBUG

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> log.debug(f"This is a DEBUG example")
        """

        self._write(message, LogLevel.DEBUG)

    def info(self, message: str) -> None:
        """
        Writes the message to the log file with level INFO.

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> log.info(f"This is an INFO example")
        """

        self._write(message, LogLevel.INFO)

    def warning(self, message: str) -> None:
        """
        Writes the message to the log file with level WARNING.

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> log.warning("This is a WARNING example")
        """

        self._write(message, LogLevel.WARNING)

    def error(self, message: str) -> None:
        """
        Writes the message to the log file with level ERROR.

        The difference between log.error and log.exception is that log.exception also prints
        the stack traceback of the exception.

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> try:
        >>>     a = 1/0
        >>> except Exception as exc:
        >>>     log.error(f"This is an ERROR example: {repr(exc)}")
        """

        self._write(message, LogLevel.ERROR)

    def critical(self, message: str) -> None:
        """
        Writes the message to the log file with level CRITICAL.

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> is_valid = check_critical_component(...)
        >>> if not is_valid:
        >>>     log.critical("This is a CRITICAL example, cannot continue")
        >>>     sys.exit(2)
        """

        self._write(message, LogLevel.CRITICAL)

    def exception(self, message: str) -> None:
        """
        Writes an exception to the log file with level ERROR.

        The difference between log.error and log.exception is that log.exception also prints
        the stack traceback of the exception.

        Parameters
        ----------
        message: str
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> try:
        >>>     a = 1/0
        >>> except Exception as exc:
        >>>     log.exception(f"This is an EXCEPTION example: {repr(exc)}")
        """

        self._write(message, LogLevel.EXCEPTION)

    def stat(self, message: str | dict[Any, Any]) -> None:
        """
        Writes a dictionary to the log file with level STAT.

        This method should be used to aggregate or summarize information in a single message
        to facilitate the use of analytics solutions like elastic and opensearch.

        Parameters
        ----------
        message: str | dict[Any, Any]
            Message to be logged

        Returns
        -------
        None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> info_dict = {"program_name": "Test Program", "var1": "StringVariable", "var2": 3}
        >>> log.stat(info_dict)
        """

        self._write(str(message), LogLevel.STAT)

    def capture_screenshot(
        self, filename: str | None = None, optimize_size: bool = False
    ) -> str:
        """
        Captures a screenshot of the entire screen and saves it in the log directory.

        Parameters
        ----------
        filename : str, optional
            Name of the screenshot.
        optimize_size : bool
            Flag to save the image using a memory efficient and lossless format (.webp)

        Returns
        -------
        filename : str
            The name of the file saved

        Raises
        ------
        ValueError
            If screenshot manager is not available (log_to_file=False)
        """
        if self._screenshot_manager is None:
            raise ValueError("Screenshot functionality requires log_to_file=True")
        return self._screenshot_manager.capture_screenshot(filename, optimize_size)

    def capture_screenshot_selenium(
        self, driver: Any, filename: str | None = None
    ) -> str:
        """
        Captures a screenshot of a Selenium driver instance.

        Parameters
        ----------
        driver : WebDriver
            Selenium WebDriver instance from which to capture the screenshot.
        filename : str, optional
            Name of the screenshot.

        Returns
        -------
        filename : str
            The name of the file saved

        Raises
        ------
        ValueError
            If screenshot manager is not available (log_to_file=False)
        """
        if self._screenshot_manager is None:
            raise ValueError("Screenshot functionality requires log_to_file=True")
        return self._screenshot_manager.capture_screenshot_selenium(driver, filename)

    def group_by_prefix(self, prefix: str | None = None, sep: str | None = None):
        """
        Group files in the log directory by prefix.

        Parameters
        ----------
        prefix: str, optional
            Prefix of files that will be grouped
        sep: str, optional
            Separator used to split file names and automatically determine file prefixes.

        Raises
        ------
        ValueError
            If screenshot manager is not available (log_to_file=False)
        """
        if self._screenshot_manager is None:
            raise ValueError("File grouping functionality requires log_to_file=True")
        return self._screenshot_manager.group_by_prefix(prefix, sep)
