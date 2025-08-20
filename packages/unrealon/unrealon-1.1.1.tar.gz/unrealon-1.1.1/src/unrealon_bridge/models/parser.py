"""
Parser-related models.

Contains models for parser registration, information, and statistics.
"""

from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated

from .base import BaseParserModel


class ParserInfo(BaseParserModel):
    """Parser registration and status information."""

    parser_id: Annotated[str, Field(min_length=1, description="Unique parser identifier")]
    parser_type: Annotated[str, Field(min_length=1, description="Type of parser (encar, autotrader, etc.)")]
    version: Annotated[str, Field(min_length=1, description="Parser version")]
    capabilities: List[str] = Field(default_factory=list, description="List of parser capabilities")
    status: Literal["active", "inactive", "error"] = "active"
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional parser metadata")
    registered_at: datetime = Field(default_factory=datetime.now)
    last_heartbeat: datetime = Field(default_factory=datetime.now)


class ParserStats(BaseParserModel):
    """Parser performance and usage statistics."""

    parser_id: Annotated[str, Field(min_length=1, description="Parser ID")]
    total_commands: Annotated[int, Field(ge=0)] = 0
    successful_commands: Annotated[int, Field(ge=0)] = 0
    failed_commands: Annotated[int, Field(ge=0)] = 0
    average_response_time: Annotated[float, Field(ge=0)] = 0.0
    uptime_seconds: Annotated[int, Field(ge=0)] = 0
    memory_usage_mb: Annotated[float, Field(ge=0)] = 0.0
    cpu_usage_percent: Annotated[float, Field(ge=0, le=100)] = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)


class ParserHealth(BaseParserModel):
    """Parser health check information."""

    parser_id: Annotated[str, Field(min_length=1, description="Parser ID")]
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    last_check: datetime = Field(default_factory=datetime.now)
    response_time: Annotated[float, Field(ge=0)] = 0.0
    memory_usage: Annotated[float, Field(ge=0)] = 0.0
    cpu_usage: Annotated[float, Field(ge=0, le=100)] = 0.0
    active_connections: Annotated[int, Field(ge=0)] = 0
    queue_size: Annotated[int, Field(ge=0)] = 0
    errors: List[str] = Field(default_factory=list)


class ParserSystemStats(BaseParserModel):
    """System-wide parser statistics."""

    total_parsers: Annotated[int, Field(ge=0)] = 0
    active_sessions: Annotated[int, Field(ge=0)] = 0
    total_commands: Annotated[int, Field(ge=0)] = 0
    allocated_proxies: Annotated[int, Field(ge=0)] = 0
    parser_types: Dict[str, int] = Field(default_factory=dict, description="Count by parser type")
