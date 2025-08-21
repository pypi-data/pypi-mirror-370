"""
Browser DTOs - Statistics Models

Statistics models for browser operations.
"""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class BrowserManagerStatistics(BaseModel):
    """Browser manager navigation statistics - 100% Pydantic v2 compliant."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Navigation metrics (matching BrowserManager usage)
    total_navigations: int = Field(default=0, ge=0, description="Total navigation count")
    successful_navigations: int = Field(default=0, ge=0, description="Successful navigation count")
    failed_navigations: int = Field(default=0, ge=0, description="Failed navigation count")
    session_start_time: Optional[datetime] = Field(default=None, description="Session start timestamp")
    session_duration_seconds: float = Field(default=0.0, ge=0.0, description="Session duration in seconds")
    
    def increment_total(self) -> None:
        """Increment total navigation count."""
        self.total_navigations += 1
    
    def increment_successful(self) -> None:
        """Increment successful navigation count."""
        self.successful_navigations += 1
    
    def increment_failed(self) -> None:
        """Increment failed navigation count."""
        self.failed_navigations += 1
    
    def set_session_start(self) -> None:
        """Set session start time to current time."""
        self.session_start_time = datetime.now(timezone.utc)
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_navigations == 0:
            return 0.0
        return (self.successful_navigations / self.total_navigations) * 100.0


class BrowserStatistics(BaseModel):
    """Browser operation statistics."""
    
    model_config = ConfigDict(extra="forbid")
    
    # Basic metrics
    total_requests: int = Field(default=0)
    successful_requests: int = Field(default=0)
    failed_requests: int = Field(default=0)
    pages_loaded: int = Field(default=0)
    
    # Proxy metrics
    proxy_requests: int = Field(default=0)
    direct_requests: int = Field(default=0)
    proxy_failures: int = Field(default=0)
    
    # Captcha metrics
    captcha_encounters: int = Field(default=0)
    captcha_solved: int = Field(default=0)
    captcha_timeouts: int = Field(default=0)
    
    # Performance
    avg_page_load_time_ms: float = Field(default=0.0)
    memory_usage_mb: float = Field(default=0.0)
    
    # Session info
    session_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
