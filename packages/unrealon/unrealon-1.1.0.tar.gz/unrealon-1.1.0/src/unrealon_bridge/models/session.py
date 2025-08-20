"""
Session-related models.

Contains models for parser session management and tracking.
"""

from typing import Optional, Dict, Literal
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated

from .base import BaseParserModel


class ParserSession(BaseParserModel):
    """Parser session information and tracking."""

    session_id: Annotated[str, Field(min_length=1, description="Unique session identifier")]
    parser_id: Annotated[str, Field(min_length=1, description="Parser ID")]
    session_type: Annotated[str, Field(min_length=1, description="Type of session (scraping, parsing, etc.)")]
    status: Literal["active", "paused", "completed", "failed", "cancelled"] = "active"
    metadata: Dict[str, str] = Field(default_factory=dict, description="Session metadata")
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[Annotated[int, Field(ge=0)]] = None
    commands_executed: Annotated[int, Field(ge=0)] = 0
    data_processed: Annotated[int, Field(ge=0)] = 0
    errors_count: Annotated[int, Field(ge=0)] = 0
