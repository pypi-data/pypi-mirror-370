"""
Proxy-related models.

Contains models for proxy allocation, management, and health checking.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated

from .base import BaseParserModel


class ProxyRequest(BaseParserModel):
    """Request for proxy allocation."""

    parser_id: Annotated[str, Field(min_length=1, description="Parser ID requesting proxy")]
    proxy_type: Literal["http", "https", "socks4", "socks5"] = "http"
    location: Optional[Annotated[str, Field(min_length=1, description="Preferred proxy location")]] = None
    session_duration: Annotated[int, Field(gt=0, le=86400, description="Session duration in seconds")] = 3600
    bandwidth_limit: Optional[Annotated[int, Field(gt=0, description="Bandwidth limit in MB/s")]] = None


class ProxyInfo(BaseParserModel):
    """Proxy allocation information."""

    proxy_id: Annotated[str, Field(min_length=1, description="Unique proxy identifier")]
    parser_id: Annotated[str, Field(min_length=1, description="Parser ID using this proxy")]
    host: Annotated[str, Field(min_length=1, description="Proxy host")]
    port: Annotated[int, Field(gt=0, le=65535, description="Proxy port")]
    proxy_type: Literal["http", "https", "socks4", "socks5"] = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    location: Optional[str] = None
    status: Literal["active", "inactive", "error"] = "active"
    allocated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: Annotated[int, Field(ge=0)] = 0
    bandwidth_used: Annotated[float, Field(ge=0)] = 0.0
