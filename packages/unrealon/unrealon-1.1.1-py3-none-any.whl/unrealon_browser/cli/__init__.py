"""
Browser CLI Module - Command-line interface using Click + questionary
Combines Click's command structure with questionary's interactive prompts
"""

from .browser_cli import browser
from .cookies_cli import cookies

__all__ = [
    "browser",
    "cookies",
]
