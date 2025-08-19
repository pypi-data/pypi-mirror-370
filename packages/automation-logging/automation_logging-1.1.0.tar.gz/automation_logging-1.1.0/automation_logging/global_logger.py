"""
Global logging functionality for automation logging library.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SupportsAutomationLogger(Protocol):
    def debug(self, message: str) -> None: ...
    def info(self, message: str) -> None: ...
    def stat(self, message: str | dict[Any, Any]) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def exception(self, message: str) -> None: ...
    def critical(self, message: str) -> None: ...
    def capture_screenshot(
        self, filename: str | None = None, optimize_size: bool = False
    ) -> str: ...
    def capture_screenshot_selenium(
        self, driver: Any, filename: str | None = None
    ) -> str: ...
    def group_by_prefix(
        self, prefix: str | None = None, sep: str | None = None
    ) -> None: ...


# Global logger instance
global_log: SupportsAutomationLogger | None = None


def get_global_log() -> SupportsAutomationLogger | None:
    """
    Returns the value of the global_log variable
    """

    return global_log


def set_global_log(logger: SupportsAutomationLogger) -> None:
    """
    Set the global log object of the `automation_logging` module

    Parameters
    ----------
    logger: AutomationLogger.
        The instance of AutomationLogger that will be used globally

    Returns
    -------
    None

    Examples
    --------
    >>> log_dir = "./tests/Logs"
    >>> log = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True)
    >>> set_global_log(log)
    >>> info("This was printed by the global log")

    Notes
    -----
    This function is thread-safe
    """

    global global_log
    global_log = logger


def debug(message: str) -> None:
    """Writes the message to the log file with level DEBUG

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> debug(f"This is a DEBUG example")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.debug(message)


def debug_else(message: str) -> None:
    """Calls debug if global_log is set, else calls print"""
    if global_log is not None:
        debug(message)
    else:
        print(f"{'DEBUG':<10} | {message}")


def info(message: str) -> None:
    """Writes the message to the log file with level INFO

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> info(f"This is an INFO example")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.info(message)


def info_else(message: str) -> None:
    """Calls info if global_log is set, else calls print"""
    if global_log is not None:
        info(message)
    else:
        print(f"{'INFO':<10} | {message}")


def stat(message: str | dict[Any, Any]) -> None:
    """Writes the message to the log file with level STAT

    Parameters
    ----------
    message: str | dict[Any, Any]
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> info_dict = {"program_name": "Test Program", "var1": "StringVariable", "var2": 3}
    >>> stat(info_dict)

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.stat(message)


def stat_else(message: str) -> None:
    """Calls stat if global_log is set, else calls print"""
    if global_log is not None:
        stat(message)
    else:
        print(f"{'STAT':<10} | {message}")


def warning(message: str) -> None:
    """Writes the message to the log file with level WARNING

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> warning(f"This is a WARNING example")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.warning(message)


def warning_else(message: str) -> None:
    """Calls warning if global_log is set, else calls print"""
    if global_log is not None:
        warning(message)
    else:
        print(f"{'WARNING':<10} | {message}")


def error(message: str) -> None:
    """Writes the message to the log file with level ERROR

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> error(f"This is an ERROR example")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.error(message)


def error_else(message: str) -> None:
    """Calls error if global_log is set, else calls print"""
    if global_log is not None:
        error(message)
    else:
        print(f"{'ERROR':<10} | {message}")


def exception(message: str) -> None:
    """Writes the message to the log file with level EXCEPTION

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> try:
    >>>     a = 1/0
    >>> except Exception as exc:
    >>>     exception(f"This is an EXCEPTION example: {repr(exc)}")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.exception(message)


def exception_else(message: str) -> None:
    """Calls exception if global_log is set, else calls print"""
    if global_log is not None:
        exception(message)
    else:
        print(f"{'EXCEPTION':<10} | {message}")


def critical(message: str) -> None:
    """Writes the message to the log file with level CRITICAL

    Parameters
    ----------
    message: str
        Message to be logged

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log = AutomationLogger(script_path=__file__)
    >>> set_global_log(log)
    >>> is_valid = check_critical_component(...)
    >>> if not is_valid:
    >>>     critical("This is a CRITICAL example, cannot continue")
    >>>     sys.exit(2)

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.critical(message)


def critical_else(message: str) -> None:
    """Calls critical if global_log is set, else calls print"""
    if global_log is not None:
        critical(message)
    else:
        print(f"{'CRITICAL':<10} | {message}")


def capture_screenshot(filename: str | None = None, optimize_size: bool = False) -> str:
    """
    Captures a screenshot of the entire screen and saves it in the log directory.

    The name of the screenshot is written with level INFO in the log file with the format:
    screenshot_log_timestamp.png (default) or the filename parameter.

    Parameters
    ----------
    filename : str, optional
        Name of the screenshot. If no extension is found in filename, it will be .png if `optimize_size` = False.
        If `optimize_size` is True, the extension will be .webp whether the extesion is found or not.

        If a file with the same name already exists, the new file will be named with a suffix (x), where x is
        the number of existing files with the same name. Example: image.png, image (1).png,
        image(2).png, image(3).png.

    optimize_size : bool
        Flag to save the image using a memory efficient and lossless format (.webp)

    Returns
    -------
    filename : str
        The name of the file saved

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log_dir = "./tests/Logs"
    >>> log = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True)
    >>> set_global_log(log)
    >>> capture_screenshot("example_screenshot.png")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    return global_log.capture_screenshot(filename, optimize_size)


def capture_screenshot_selenium(driver: Any, filename: str | None = None) -> str:
    """
    Captures a screenshot of a Selenium driver instance.

    The name of the screenshot is written with level INFO in the log file with the format:
    log_timestamp_screenshot_selenium.png or the filename parameter.

    Parameters
    ----------
    driver : WebDriver
        Selenium WebDriver instance from which to capture the screenshot.

    filename : str, optional
        Name of the screenshot. If a file with the same name already exists, the new file
        will be named with a suffix (x), where x is the number of existing files with the
        same name. Example: image.png, image (1).png, image(2).png, image(3).png.

    Returns
    -------
    filename : str
        The name of the file saved

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log_dir = "./tests/Logs"
    >>> log = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True)
    >>> set_global_log(log)
    >>> driver = selenium.webdriver.Chrome(...)
    >>> capture_screenshot_selenium(driver, "chromedriver_screenshot.png")

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    return global_log.capture_screenshot_selenium(driver, filename)


def group_by_prefix(prefix: str | None = None, sep: str | None = None) -> None:
    """
    Group files in the log directory by prefix.
    If `prefix` is given all files that don't have the prefix will be ignored.
    If `sep` is given all files will be grouped according to automatic prefixes defined by the
    text before the separator.
    `prefix` takes priority over `sep` if both are set

    This function is useful to group images captured during the execution

    Parameters
    ----------
    prefix: str, optional
        Prefix of files that will be grouped inside the folder `prefix` in the log directory

    sep: str, optional
        Separator used to split file names and automatically determine file prefixes.
        Files with the same prefix will be grouped inside the same folder in the log directory

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If global log is not set

    Examples
    --------
    >>> log_dir = "./tests/Logs"
    >>> log = AutomationLogger(script_path=__file__, log_dir=log_dir, log_to_console=True)
    >>> set_global_log(log)
    >>> # Manual prefix
    >>> capture_screenshot("ABC - Image 1")
    >>> capture_screenshot("ABC - Image 2")
    >>> capture_screenshot("ABC - Image 3")
    >>> group_by_prefix(prefix="ABC") # creates folder "ABC"
    >>> # Automatic Prefix
    >>> capture_screenshot("ABC - Image 1")
    >>> capture_screenshot("ABC - Image 2")
    >>> capture_screenshot("ABCD - Image 1")
    >>> group_by_prefix(sep="-") # creates folders "ABC" and "ABCD"

    Notes
    -----
    This function is thread-safe
    """
    if global_log is None:
        raise ValueError("This function requires the global log to be set")
    global_log.group_by_prefix(prefix, sep)
