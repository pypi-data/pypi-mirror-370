"""
Event logging and heartbeat for Parser Bridge Client.
"""

import uuid
from typing import Optional
from datetime import datetime
from unrealon_rpc.logging import get_logger

from ..models import ParserEvent, ParserStats

logger = get_logger(__name__)


class EventsMixin:
    """Mixin for event logging and heartbeat functionality."""

    async def log_event(self, event_type: str, message: str, level: str = "info", data: Optional[dict[str, str]] = None, command_id: Optional[str] = None) -> None:
        """
        Log parser event.

        Args:
            event_type: Type of event
            message: Event message
            level: Log level
            data: Additional event data (string values only)
            command_id: Associated command ID
        """
        if not self.registered:
            return

        event = ParserEvent(
            event_id=str(uuid.uuid4()),
            parser_id=self.parser_id,
            event_type=event_type,
            level=level,
            message=message,
            data=data or {},
            session_id=self.session_id,
            command_id=command_id
        )

        # Send event via PubSub
        await self.bridge_client.publish("parser_events", event.model_dump())

    async def send_heartbeat(self, stats: Optional[ParserStats] = None) -> None:
        """
        Send parser heartbeat with optional stats.

        Args:
            stats: Parser statistics
        """
        if not self.registered:
            return

        heartbeat_data = {
            "parser_id": self.parser_id, 
            "timestamp": datetime.now().isoformat(), 
            "session_id": self.session_id or ""
        }

        if stats:
            heartbeat_data["stats"] = stats.model_dump()

        await self.bridge_client.send_heartbeat("alive", heartbeat_data)
