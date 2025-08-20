"""
Common models for smart logging system.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class LogLevel(str, Enum):
    """Log levels for driver logger"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structure for log entry"""
    timestamp: str
    level: str
    message: str
    parser_id: str
    session_id: Optional[str] = None
    url: Optional[str] = None
    operation: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class LogContext(BaseModel):
    """Log context information"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    session_id: Optional[str] = Field(default=None)
    command_id: Optional[str] = Field(default=None)
    operation: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    additional_data: dict[str, Any] = Field(default_factory=dict)
