"""
Create wheel for automation_logging

Use: python setup.py bdist_wheel
"""

from setuptools import setup

# optional dependencies
extras_require = {
    "selenium": ["selenium"],
    "pyautogui": ["pyautogui", "pyscreeze", "pillow"],
    "all": ["selenium", "pyautogui", "pyscreeze", "pillow"],
}

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

_ = setup(
    name="automation-logging",
    version="1.1.0",
    packages=["automation_logging"],
    url="https://github.com/VBenevides/automation-logging",
    license="MIT",
    author="Vinicius Benevides",
    author_email="massaki1999@gmail.com",
    description="Logging for automation, offering thread-safety, log cleanup and screenshot support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    extras_require=extras_require,
)
