"""
UnrealOn - Main Package
Enterprise browser automation framework with WebSocket bridge for distributed web scraping.
"""

from importlib.metadata import version
from pydantic import BaseModel, Field, ConfigDict


try:
    __version__ = version("unrealon")
except Exception:
    __version__ = "1.1.5"


class VersionInfo(BaseModel):
    """Version information model."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    version: str = Field(default=__version__)


# Re-export main modules
import unrealon_driver
import unrealon_server
import unrealon_browser

# Re-export all from submodules
from unrealon_driver import *
from unrealon_server import *
from unrealon_browser import *

__all__ = [
    "VersionInfo",
    # Re-export all from submodules
    *getattr(unrealon_driver, "__all__", []),
    *getattr(unrealon_server, "__all__", []),
    *getattr(unrealon_browser, "__all__", []),
]
