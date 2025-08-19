"""
Automation Logging
====
- Thread-Safe Logging: Ensures reliable and consistent logging from multi-threaded applications, preventing message corruption.
- Automated Log Management: Simplifies log file maintenance with configurable retention policies based on age or file count.
- Seamless Integration: Enables effortless integration with existing projects by allowing the library to override the standard `logging` module's root logger.
- Integrated Screenshot Capture: Captures informative screenshots directly within your logs, supporting full-screen captures (using `pyautogui`) and Selenium WebDriver screenshots, including headless browser support (using `selenium`).
"""

__version__ = "1.1.0"

# Import core components
from .core import LogLevel, AutomationLogger
from .screenshots import ScreenshotManager
from .utils import add_logging_level
from .global_logger import (
    set_global_log,
    get_global_log,
    debug,
    debug_else,
    info,
    info_else,
    stat,
    stat_else,
    warning,
    warning_else,
    error,
    error_else,
    exception,
    exception_else,
    critical,
    critical_else,
    capture_screenshot,
    capture_screenshot_selenium,
    group_by_prefix,
)
from .config import image_enabled, web_enabled

__all__ = [
    # Core classes
    "LogLevel",
    "AutomationLogger",
    "ScreenshotManager",
    # Global logging functions
    "set_global_log",
    "get_global_log",
    "debug",
    "debug_else",
    "info",
    "info_else",
    "stat",
    "stat_else",
    "warning",
    "warning_else",
    "error",
    "error_else",
    "exception",
    "exception_else",
    "critical",
    "critical_else",
    "capture_screenshot",
    "capture_screenshot_selenium",
    "group_by_prefix",
    # Utilities
    "add_logging_level",
    # Configuration
    "web_enabled",
    "image_enabled",
]
