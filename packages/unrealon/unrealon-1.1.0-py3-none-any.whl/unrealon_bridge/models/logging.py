"""
Parser logging models.

Models for sending parser logs to Django via WebSocket/Redis.
"""

from datetime import datetime
from typing import Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .base import BaseParserModel


class ParserLogLevel(str, Enum):
    """Parser log levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ParserLogEntry(BaseParserModel):
    """Parser log entry to send to Django."""
    
    parser_id: str = Field(..., description="ID of the parser")
    level: str = Field(..., description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the log was created")
    
    # Optional context
    session_id: Optional[str] = Field(None, description="Parser session ID")
    command_id: Optional[str] = Field(None, description="Command ID if related to command")
    url: Optional[str] = Field(None, description="URL being processed")
    operation: Optional[str] = Field(None, description="Operation being performed")
    
    # Additional data
    data: Dict[str, str] = Field(default_factory=dict, description="Additional log data")
    error_details: Optional[str] = Field(None, description="Error details if error log")


class ParserLogRequest(BaseParserModel):
    """RPC request for sending parser log."""
    
    log_entry: ParserLogEntry


class ParserLogResponse(BaseParserModel):
    """RPC response for parser log."""
    
    success: bool = Field(..., description="Whether log was sent successfully")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
