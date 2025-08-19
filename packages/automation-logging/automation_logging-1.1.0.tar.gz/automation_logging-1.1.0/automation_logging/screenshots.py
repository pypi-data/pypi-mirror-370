"""
Screenshot functionality for automation logging library.
"""

import os
import shutil
from datetime import datetime
from typing import Any
from threading import Lock

from .config import image_enabled, web_enabled, screenshot, Image


class ScreenshotManager:
    """Manages screenshot capture functionality for automation logging."""

    def __init__(self, log_dir: str, logger: Any):
        """
        Initialize screenshot manager.

        Parameters
        ----------
        log_dir : str
            Directory where screenshots will be saved
        logger : Any
            Logger instance for logging screenshot events
        """
        self.log_dir: str = log_dir
        self._logger = logger
        self._mutex: Lock = Lock()

    def capture_screenshot(
        self, filename: str | None = None, optimize_size: bool = False
    ) -> str:
        """
        Captures a screenshot of the entire screen and saves it in the log directory.

        The name of the screenshot is written with level INFO in the log file with the format:
        screenshot_log_timestamp.png (default) or the filename parameter.

        Parameters
        ----------
        filename : str, optional
            Name of the screenshot. If no extension is found in filename, it will be .png if `optimize_size` = False.
            If `optimize_size` is True, the extension will be .webp whether the extension is found or not.

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
        NotImplementedError
            If pyautogui and pillow/PIL are not installed
        ValueError
            If the `filename` passed is not a string

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> log.capture_screenshot("example_screenshot.png")
        """

        if not image_enabled:
            raise NotImplementedError(
                "Function is only available if pyautogui and pillow/PIL are installed"
            )

        if filename is not None and not isinstance(filename, str):
            raise ValueError("filename must be a string")

        if filename is None:
            timestamp = datetime.now().strftime(r"%Y_%m_%d-%H_%M_%S")
            basename = f"screenshot_{timestamp}"
            extension = ".png"
        else:
            basename, extension = os.path.splitext(filename)
            if extension == "":
                extension = ".png"

        if optimize_size:
            extension = ".webp"

        filename = basename + extension

        with self._mutex:
            suffix = 0
            # If file with same name exists, include a suffix (number)
            while os.path.exists(os.path.join(self.log_dir, filename)):
                suffix += 1
                filename = f"{basename} ({suffix}){extension}"
            filepath = os.path.join(self.log_dir, filename)
            img: Image = screenshot(filepath)
            if optimize_size:
                img.save(filepath, lossless=True, optimize=True)
            self._logger.info(f"Screenshot captured and saved as: {filename}")

        return filename

    def capture_screenshot_selenium(
        self, driver: Any, filename: str | None = None
    ) -> str:
        """
        Captures a screenshot of a Selenium driver instance.

        The name of the screenshot is written with level INFO in the log file with the format:
        selenium_screenshot_log_timestamp.png or the filename parameter.

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
        NotImplementedError
            If selenium is not installed
        ValueError
            If the `filename` passed is not a string

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> driver = selenium.webdriver.Chrome(...)
        >>> log.capture_screenshot_selenium(driver, "chromedriver_screenshot.png")
        """

        if not web_enabled:
            raise NotImplementedError(
                "Function is only available if selenium is installed"
            )

        if filename is not None and not isinstance(filename, str):
            raise ValueError("filename must be a string")

        if filename is None:
            timestamp = datetime.now().strftime(r"%Y_%m_%d-%H_%M_%S")
            basename = f"selenium_screenshot_{timestamp}"
        else:
            basename = os.path.splitext(filename)[0]
        filename = basename + ".png"

        with self._mutex:
            # If file with same name exists, include a suffix (number)
            suffix = 0
            while os.path.exists(os.path.join(self.log_dir, filename)):
                suffix += 1
                filename = f"{basename} ({suffix}).png"

            driver.save_screenshot(os.path.join(self.log_dir, filename))
            self._logger.info(f"Selenium screenshot captured and saved as: {filename}")

        return filename

    def group_by_prefix(self, prefix: str | None = None, sep: str | None = None):
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
            To ensure expected behaviour, the prefix in the file name must be followed by one of the following: [" ", "-", "_", "@"]

        sep: str, optional
            Separator used to split file names and automatically determine file prefixes.
            To ensure expected behaviour, the string before the separator must be followed by one of the following: [" ", "-", "_", "@", sep]

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the `prefix` and `sep` are None

        Examples
        --------
        >>> log = AutomationLogger(script_path=__file__)
        >>> # Manual prefix
        >>> log.capture_screenshot("ABC - Image 1")
        >>> log.capture_screenshot("ABC - Image 2")
        >>> log.capture_screenshot("ABC - Image 3")
        >>> log.group_by_prefix(prefix="ABC") # creates folder "ABC"
        >>> # Automatic Prefix
        >>> log.capture_screenshot("ABC - Image 1")
        >>> log.capture_screenshot("ABC - Image 2")
        >>> log.capture_screenshot("ABCD - Image 1")
        >>> log.group_by_prefix(sep="-") # creates folders "ABC" and "ABCD"
        """

        if prefix is None and sep is None:
            raise ValueError("prefix or sep must be set")

        with self._mutex:
            if prefix is not None:
                prefixes = [str(prefix)]
            else:
                sep = str(sep)
                files = [
                    x
                    for x in os.listdir(self.log_dir)
                    if sep in x and x != self._logger.name
                ]
                prefixes = set(x.split(sep)[0] for x in files)

            # There was a bug when a prefix is a substring of another, such as prefix1 and prefix10
            # An attempt to avoid it is to see if the prefix is separate from the rest of the text
            # by common separators
            separators = [" ", "_", "-", "@"]
            if sep is not None:
                separators.append(sep)

            for prefix in prefixes:
                prefix = prefix.strip()
                files: list[str] = []
                for file in os.listdir(self.log_dir):
                    if file == self._logger.name or not os.path.isfile(
                        os.path.join(self.log_dir, file)
                    ):
                        continue
                    if prefix[-1] in separators:
                        files.append(prefix[-1])
                    else:
                        for sep in separators:
                            if file.startswith(prefix + sep):
                                files.append(file)
                                break

                os.makedirs(os.path.join(self.log_dir, prefix), exist_ok=True)
                for file in files:
                    _ = shutil.move(
                        os.path.join(self.log_dir, file),
                        os.path.join(self.log_dir, prefix),
                    )
                self._logger.info(f"Grouped files by prefix: {prefix}")
