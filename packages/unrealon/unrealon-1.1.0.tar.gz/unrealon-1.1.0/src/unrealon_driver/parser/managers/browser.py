"""
Browser Manager - Wrapper over unrealon_driver.browser

Simple wrapper that inherits from the main BrowserManager
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from unrealon_driver.browser import BrowserManager as BaseBrowserManager, BrowserConfig as BaseBrowserConfig


class BrowserConfig(BaseBrowserConfig):
    """Extended browser configuration for parser manager"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class BrowserStats(BaseModel):
    """Browser usage statistics"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    pages_visited: int = Field(default=0, ge=0)
    total_load_time: float = Field(default=0.0, ge=0.0)
    average_load_time: float = Field(default=0.0, ge=0.0)
    screenshots_taken: int = Field(default=0, ge=0)
    cookies_saved: int = Field(default=0, ge=0)
    errors_count: int = Field(default=0, ge=0)
    session_duration: float = Field(default=0.0, ge=0.0)


class BrowserManager(BaseBrowserManager):
    """
    🌐 Browser Manager - Wrapper over base browser manager

    Simple wrapper that extends the base BrowserManager with parser-specific functionality
    """

    def __init__(self, config: BrowserConfig):
        super().__init__(config)
        self._stats = BrowserStats()

    def get_stats(self) -> BrowserStats:
        """Get browser usage statistics"""
        return self._stats

    async def health_check(self) -> Dict[str, Any]:
        """Browser health check"""
        base_health = await super().health_check()
        return {**base_health, "parser_manager": True}
