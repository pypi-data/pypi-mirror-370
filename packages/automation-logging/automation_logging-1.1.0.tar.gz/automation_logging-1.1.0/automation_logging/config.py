"""
Configuration and dependency management for automation logging library.
"""

import os
from importlib.util import find_spec

# Environment variable configuration
truthy_values = ["1", "true", "t", "yes", "y", "on"]
OPT_DISABLE_WEB = os.environ.get("alog_disable_web", "0").lower() in truthy_values
OPT_DISABLE_IMAGE = os.environ.get("alog_disable_image", "0").lower() in truthy_values

# Selenium dependency check
if OPT_DISABLE_WEB:
    web_enabled = False
else:
    web_enabled = find_spec("selenium") is not None

# Image capture dependency check
if OPT_DISABLE_IMAGE:
    image_enabled = False
else:
    image_enabled = (
        find_spec(name="pyautogui") is not None and find_spec(name="PIL") is not None
    )

# Import screenshot function if available
if image_enabled:
    from pyautogui import screenshot  # pyright: ignore[reportAssignmentType]
    from PIL.Image import Image  # pyright: ignore[reportAssignmentType]
else:

    class Image:
        """Dummy image class"""

        def save(self, *args, **kwargs) -> None:
            return None

    # Dummy implementations
    def screenshot(*args, **kwargs) -> Image:
        return Image()
