"""
UnrealOn - Main Package
Enterprise browser automation framework with WebSocket bridge for distributed web scraping.
"""

from importlib.metadata import version

try:
    __version__ = version("unrealon")
except Exception:
    __version__ = "1.0.0"

# Re-export main modules
import unrealon_driver
import unrealon_bridge
import unrealon_browser

# Re-export all from submodules
from unrealon_driver import *
from unrealon_bridge import *
from unrealon_browser import *

__all__ = [
    # Version
    "__version__",
    # Re-export all from submodules
    *getattr(unrealon_driver, "__all__", []),
    *getattr(unrealon_bridge, "__all__", []),
    *getattr(unrealon_browser, "__all__", []),
]
