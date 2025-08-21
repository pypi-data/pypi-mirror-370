"""
Browser DTOs - Pydantic Models

100% Pydantic v2 compliant models for browser operations.
COMPLIANCE: REQUIREMENTS_COMPLETE.md - No dataclasses allowed!
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, computed_field
from .enums import BrowserSessionStatus


class ProxyInfo(BaseModel):
    """Proxy information for browser session - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    host: str = Field(..., min_length=1, description="Proxy host")
    port: int = Field(..., ge=1, le=65535, description="Proxy port")
    username: Optional[str] = Field(default=None, description="Proxy username")
    password: Optional[str] = Field(default=None, description="Proxy password")
    ip: Optional[str] = Field(default=None, description="Proxy IP address")
    
    @computed_field
    @property
    def proxy_key(self) -> str:
        """Generate proxy key."""
        return f"{self.host}:{self.port}"


class PageResult(BaseModel):
    """Page loading result - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool = Field(..., description="Whether page loaded successfully")
    url: str = Field(..., description="Requested URL")
    current_url: str = Field(..., description="Current page URL")
    title: str = Field(..., description="Page title")
    content: Optional[str] = Field(default=None, description="Page content")
    response_time: float = Field(default=0.0, ge=0.0, description="Response time in seconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    proxy: Optional[ProxyInfo] = Field(default=None, description="Proxy used for request")


class BrowserSession(BaseModel):
    """Browser session info - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    session_id: str = Field(..., min_length=1, description="Unique session ID")
    parser_name: str = Field(..., min_length=1, description="Parser name")
    proxy: Optional[ProxyInfo] = Field(default=None, description="Proxy information")
    profile_path: str = Field(..., description="Browser profile path")
    created_at: datetime = Field(..., description="Session creation time")
    is_active: bool = Field(default=True, description="Whether session is active")
    page_count: int = Field(default=0, ge=0, description="Number of pages loaded")
    browser_type: Optional[str] = Field(default=None, description="Browser type for logger bridge")
    current_status: BrowserSessionStatus = Field(default=BrowserSessionStatus.INITIALIZING, description="Current session status")
