"""
Parser Bridge Client - Modular implementation with composition.

Clean architecture without multiple inheritance or hasattr checks.
"""

from typing import Optional, List
from unrealon_rpc.logging import get_logger

from .base import ParserBridgeClientBase
from .connection import ConnectionMixin
from .session import SessionMixin
from .commands import CommandsMixin
from .proxy import ProxyMixin
from .events import EventsMixin
from .health import HealthMixin
from .logging import LoggingMixin
from .html_parser import HTMLParserMixin
from .scheduler import SchedulerMixin

from ..models import (
    ParserInfo, ParserHealth, ParserStats, CommandResult, ProxyInfo
)

logger = get_logger(__name__)


class ParserBridgeClient(
    ParserBridgeClientBase,
    ConnectionMixin,
    SessionMixin, 
    CommandsMixin,
    ProxyMixin,
    EventsMixin,
    HealthMixin,
    LoggingMixin,
    HTMLParserMixin,
    SchedulerMixin
):
    """
    Complete Parser Bridge Client with all functionality.
    
    Combines all mixins to provide full parser client capabilities:
    - Connection and registration management
    - Session lifecycle
    - Command execution
    - Proxy management
    - Event logging and heartbeat
    - Health monitoring
    - Parser logging to Django
    - HTML parsing via AI/LLM
    - Task scheduling and management
    """

    def __init__(self, websocket_url: str, parser_type: str, parser_version: str = "1.0.0", capabilities: List[str] = None, api_key: str = None, **kwargs):
        """
        Initialize complete parser bridge client.

        Args:
            websocket_url: WebSocket server URL
            parser_type: Type of parser (encar, autotrader, etc.)
            parser_version: Parser version
            capabilities: List of parser capabilities
            api_key: API key for authentication
            **kwargs: Additional arguments for BridgeClient
        """
        super().__init__(websocket_url, parser_type, parser_version, capabilities, api_key, **kwargs)

    async def disconnect(self) -> None:
        """Enhanced disconnect with proper session cleanup."""
        if self.session_id:
            await self.end_session()
        
        # Call parent disconnect
        await super().disconnect()

    async def _log_command_event(self, event_type: str, message: str, level: str = "info", data: Optional[dict[str, str]] = None) -> None:
        """Override to provide actual event logging."""
        await self.log_event(event_type=event_type, message=message, level=level, data=data)
    
    def set_command_handler(self, handler) -> None:
        """
        Set command handler for daemon compatibility.
        
        Args:
            handler: Command handler function
        """
        # For now, just store the handler - can be extended later for actual command processing
        self._command_handler = handler
        logger.info("Command handler set for daemon compatibility")


__all__ = ["ParserBridgeClient"]
