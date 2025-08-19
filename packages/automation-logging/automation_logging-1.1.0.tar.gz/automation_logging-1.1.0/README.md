# Automation Logging

## Overview 
Logging library for automation, offering thread-safety, log cleanup and screenshot support:
* **Thread-Safe Logging:** Ensures reliable and consistent logging from multi-threaded applications, preventing message corruption.
* **Automated Log Management:** Simplifies log file maintenance with configurable retention policies based on age or file count.
* **Seamless Integration:** Enables effortless integration with existing projects by allowing the library to override the standard `logging` module's root logger.
* **Integrated Screenshot Capture:** Captures informative screenshots directly within your logs, supporting full-screen captures (using `pyautogui`) and Selenium WebDriver screenshots, including headless browser support (using `selenium`).

-----------

## Instructions

### - How to create wheel

1. Create a virtual environment and install packages from build-requirements.txt
2. Activate the virtual environment
3. From the folder containing "setup.py", execute: `python setup.py bdist_wheel`
4. The wheel will be generated inside the `dist` folder
5. Install wheel using: `pip install dist/automation_logging[...].whl`

### - How to generate documentation

1. Create a virtual environment and install packages from build-requirements.txt
2. Activate the virtual environment
3. From the sphinx-doc folder, execute: `make html`
4. The documentation will be generated inside the `sphinx-doc/build/html` folder
5. To use the documentation, open the `index.html` file
