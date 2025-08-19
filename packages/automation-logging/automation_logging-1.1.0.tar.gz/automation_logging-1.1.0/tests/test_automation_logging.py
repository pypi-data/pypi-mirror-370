import os
import shutil
from concurrent import futures
import unittest
import time
import warnings
import logging
from random import randrange

import automation_logging as alog


def delete_dir(log_dir):
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)


def disconnect_all_handlers():
    """Disconnects all handlers from all loggers."""
    warnings.filterwarnings("ignore", category=ResourceWarning)

    for logger in logging.Logger.manager.loggerDict.values():  # iterate over all loggers
        if isinstance(logger, logging.Logger):  # ensure it is a logger object.
            handlers = logger.handlers[:]  # create a copy to avoid modification during iteration
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)


class TestAutomationLogger(unittest.TestCase):
    def setUp(self):
        self.log_dir = "./local/test_logs"
        self.max_logs = 2
        delete_dir(self.log_dir)
        alog.global_logger.global_log = None

    def tearDown(self):
        disconnect_all_handlers()
        delete_dir(self.log_dir)

    def test_log_level(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        messages = []
        for i, level in enumerate(
            [alog.LogLevel.DEBUG, alog.LogLevel.INFO, alog.LogLevel.CRITICAL]
        ):
            log = alog.AutomationLogger(
                script_path=__file__,
                log_dir=self.log_dir,
                log_to_console=False,
                as_logging_root=True,
                as_global_log=False,
                level_threshold=level,
            )
            log.debug(f"debug {i}")
            log.info(f"info {i}")
            log.stat(f"stat {i}")
            log.warning(f"warning {i}")
            log.error(f"error {i}")
            try:
                _ = 1 / 0
            except:
                log.exception(f"exception {i}")
            log.critical(f"critical {i}")

            with open(log.log_file, "r", encoding="utf-8") as file:
                content = file.readlines()
                messages.extend(
                    [
                        x.split("|")[-1].strip()
                        for x in content
                        if "|" in x and str(i) in x.split("|")[-1] and "object" not in x
                    ]
                )

        self.assertEqual(
            messages,
            [
                "debug 0",
                "info 0",
                "stat 0",
                "warning 0",
                "error 0",
                "exception 0",
                "critical 0",
                "info 1",
                "stat 1",
                "warning 1",
                "error 1",
                "exception 1",
                "critical 1",
                "critical 2",
            ],
        )

    def test_else_funcs(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        # Try before setting the global log and functions without else
        try:
            alog.info("info message")
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        # Try before setting the global log and functions using else
        alog.info_else("info_else message")

        # Try after setting the global log
        _ = alog.AutomationLogger(
            script_path=__file__,
            log_dir=self.log_dir,
            log_to_console=False,
            as_global_log=True,
        )

        messages = [
            "info message (after setting global log)",
            "info_else message (after setting global log)",
        ]
        alog.info(messages[0])
        alog.info_else(messages[1])

        with open(alog.get_global_log().log_file, "r", encoding="utf-8") as file:
            content = file.read()
            for msg in messages:
                self.assertIn(msg, content)

        self.assertTrue(True)

    def test_logging_funcs(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        log = alog.AutomationLogger(
            script_path=__file__,
            log_dir=self.log_dir,
            log_to_console=False,
            as_logging_root=True,
            as_global_log=False,
            level_threshold=alog.LogLevel.DEBUG,
        )

        logging.debug("debug")
        logging.info("info")
        logging.stat("stat")
        logging.warning("warning")
        logging.error("error")
        try:
            _ = 1 / 0
        except:
            logging.exception("exception")
        logging.critical("critical")

        with open(log.log_file, "r", encoding="utf-8") as file:
            content = file.read()
            messages = ["debug", "info", "stat", "warning", "error"]
            for msg in messages:
                self.assertIn(msg, content)

    def test_threads(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        alog.AutomationLogger(
            script_path=__file__,
            log_dir=self.log_dir,
            log_to_console=False,
            as_logging_root=True,
            as_global_log=True,
            level_threshold=alog.LogLevel.DEBUG,
        )

        num_workers = 5
        num_msg_per_worker = 3

        def foo(thread_num):
            for i in range(num_msg_per_worker):
                time.sleep(randrange(50, 300) / 1000)
                alog.info(f"Thread {thread_num} - Message {i}")

        with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            fts = {executor.submit(foo, thread_num) for thread_num in range(num_workers)}
            _ = [ft.result() for ft in futures.as_completed(fts)]

        messages = []
        for i in range(num_workers):
            for j in range(num_msg_per_worker):
                messages.append(f"Thread {i} - Message {j}")
        with open(alog.get_global_log().log_file, "r", encoding="utf-8") as file:
            content = file.read()
            for msg in messages:
                self.assertIn(msg, content)

    def test_file_retention(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        for _ in range(2 * self.max_logs):
            alog.AutomationLogger(
                script_path=__file__,
                log_dir=self.log_dir,
                max_logs=self.max_logs,
                log_to_console=False,
                as_logging_root=True,
                as_global_log=False,
            )
            self.assertTrue(len(os.listdir(self.log_dir)) <= self.max_logs)
            # wait 1 second to change the directory name
            time.sleep(1)

    def test_screenshot(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        alog.AutomationLogger(
            script_path=__file__,
            log_dir=self.log_dir,
            log_to_console=False,
            as_logging_root=True,
            as_global_log=True,
            level_threshold=alog.LogLevel.INFO,
        )

        if not alog.image_enabled:
            print("pyautogui is not installed, skipping capture_screenshot test")
            self.assertTrue(True)
        else:
            files = []
            basename = "capture_screenshot"
            files.append(alog.capture_screenshot(f"{basename}.png"))

            # Testing multiple files
            files.append(alog.capture_screenshot(f"{basename}"))
            files.append(alog.capture_screenshot(f"{basename}.png"))
            files.append(alog.capture_screenshot())

            files.append(alog.capture_screenshot(f"1 {basename}", optimize_size=True))
            files.append(alog.capture_screenshot(optimize_size=True))
            for file in files:
                self.assertTrue(os.path.exists(os.path.join(alog.get_global_log().log_dir, file)))

    def test_selenium_screenshot(self):
        print(f"Running test: {self.__class__.__name__}.{self._testMethodName}")

        alog.AutomationLogger(
            script_path=__file__,
            log_dir=self.log_dir,
            log_to_console=False,
            as_logging_root=True,
            as_global_log=True,
            level_threshold=alog.LogLevel.INFO,
        )

        if not alog.web_enabled:
            print("selenium is not installed, skipping capture_screenshot_selenium test")
            self.assertTrue(True)
        else:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            service = Service()
            options = Options()
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options, service=service)
            driver.get("https://google.com")
            files = []
            basename = "capture_screenshot_selenium"
            files.append(alog.capture_screenshot_selenium(driver, f"{basename}.png"))

            # Testing multiple files
            files.append(alog.capture_screenshot_selenium(driver, f"{basename}"))
            files.append(alog.capture_screenshot_selenium(driver, f"{basename}.png"))
            files.append(alog.capture_screenshot_selenium(driver))

            for file in files:
                self.assertTrue(os.path.exists(os.path.join(alog.get_global_log().log_dir, file)))


if __name__ == "__main__":
    unittest.main()
