"""
Event and webhook-related models.

Contains models for parser events, logging, and webhook configurations.
"""

from typing import Optional, Dict, List, Literal
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated

from .base import BaseParserModel


class ParserEvent(BaseParserModel):
    """Parser event for logging and monitoring."""

    event_id: Annotated[str, Field(min_length=1, description="Unique event identifier")]
    parser_id: Annotated[str, Field(min_length=1, description="Parser ID")]
    event_type: Annotated[str, Field(min_length=1, description="Type of event")]
    level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    message: Annotated[str, Field(min_length=1, description="Event message")]
    data: Dict[str, str] = Field(default_factory=dict, description="Additional event data (string values only)")
    command_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    source: Optional[str] = None


class WebhookConfig(BaseParserModel):
    """Webhook configuration for parser events."""

    webhook_id: Annotated[str, Field(min_length=1, description="Unique webhook identifier")]
    parser_id: Annotated[str, Field(min_length=1, description="Parser ID")]
    url: Annotated[str, Field(min_length=1, description="Webhook URL")]
    events: List[str] = Field(default_factory=list, description="Events to trigger webhook")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    secret: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
