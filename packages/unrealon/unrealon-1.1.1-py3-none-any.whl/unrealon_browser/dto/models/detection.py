"""
Browser DTOs - Detection & Cookie Models

100% Pydantic v2 compliant models for CAPTCHA detection and cookie management.
COMPLIANCE: REQUIREMENTS_COMPLETE.md - All models use BaseModel.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from .enums import CaptchaType
from .core import ProxyInfo


class CaptchaDetection(BaseModel):
    """Captcha detection result - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    detected: bool = Field(..., description="Whether captcha was detected")
    captcha_type: CaptchaType = Field(default=CaptchaType.UNKNOWN, description="Type of captcha detected")
    page_url: str = Field(..., min_length=1, description="Page URL where detected")
    page_title: Optional[str] = Field(default=None, description="Page title")
    
    # Proxy context for cookie binding
    proxy_host: Optional[str] = Field(default=None, description="Proxy host")
    proxy_port: Optional[int] = Field(default=None, ge=1, le=65535, description="Proxy port")
    
    # Detection details
    indicators: List[str] = Field(default_factory=list, description="Detection indicators")
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Detection timestamp"
    )


class CaptchaDetectionResult(BaseModel):
    """Alias for backward compatibility - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    captcha_found: bool = Field(..., description="Whether captcha was detected")
    captcha_type: Optional[CaptchaType] = Field(default=None, description="Type of captcha")
    detection_details: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional detection details"
    )


class CookieMetadata(BaseModel):
    """Cookie storage metadata - 100% Pydantic v2."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    proxy_id: Optional[str] = Field(default=None, description="Associated proxy ID")
    domain_filter: Optional[str] = Field(default=None, description="Domain filter applied")
    total_cookies: int = Field(default=0, ge=0, description="Total cookies count")
    saved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Save timestamp"
    )
    parser_name: Optional[str] = Field(default=None, description="Parser name")
    cookies_count: int = Field(default=0, ge=0, description="Cookies count (legacy field)")
    proxy_info: Optional[ProxyInfo] = Field(default=None, description="Proxy information")
