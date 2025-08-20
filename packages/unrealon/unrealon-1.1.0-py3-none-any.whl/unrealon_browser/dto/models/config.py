"""
Browser DTOs - Configuration Models

Configuration models for browser automation.
"""

from pydantic import BaseModel, Field, ConfigDict
from .enums import BrowserType, BrowserMode


class BrowserConfig(BaseModel):
    """Simplified browser configuration."""

    model_config = ConfigDict(extra="forbid")

    # Basic settings
    browser_type: BrowserType = Field(default=BrowserType.CHROMIUM)
    mode: BrowserMode = Field(default=BrowserMode.AUTO)

    # Timeouts
    page_load_timeout_seconds: float = Field(default=30.0)
    navigation_timeout_seconds: float = Field(default=30.0)

    # Proxy settings
    use_proxy_rotation: bool = Field(default=True)
    realistic_ports_only: bool = Field(default=False)
    parser_name: str = Field(default="default_parser")

    # Performance
    disable_images: bool = Field(default=False)
    enable_stealth_check: bool = Field(default=False)
