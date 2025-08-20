"""
Command-related models.

Contains models for command execution, tracking, and results.
"""

from typing import Optional, Dict, Literal, Any
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated

from .base import BaseParserModel


class ParserCommand(BaseParserModel):
    """Parser command definition and tracking."""

    command_id: Annotated[str, Field(min_length=1, description="Unique command identifier")]
    command_type: Annotated[str, Field(min_length=1, description="Type of command (scrape, parse, etc.)")]
    parser_id: Annotated[str, Field(min_length=1, description="Parser ID that will execute the command")]
    parameters: Dict[str, str] = Field(default_factory=dict, description="Command parameters")
    status: Literal["pending", "running", "completed", "failed", "cancelled"] = "pending"
    priority: Annotated[int, Field(ge=1, le=10)] = 5
    timeout: Annotated[int, Field(gt=0, le=3600, description="Command timeout in seconds")] = 300
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: Annotated[int, Field(ge=0)] = 0
    max_retries: Annotated[int, Field(ge=0)] = 3


class CommandResult(BaseParserModel):
    """Result of command execution."""

    command_id: Annotated[str, Field(min_length=1, description="Command ID")]
    success: bool = Field(description="Whether command executed successfully")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Command result data")
    error_message: Optional[str] = None
    execution_time: Annotated[float, Field(ge=0)] = 0.0
    output_size: Annotated[int, Field(ge=0)] = 0
    created_at: datetime = Field(default_factory=datetime.now)
