"""
Base Parser Bridge Client.

Core client functionality and state management.
"""

from typing import Optional, List
from unrealon_rpc.bridge import BridgeClient
from unrealon_rpc.logging import get_logger

logger = get_logger(__name__)


class ParserBridgeClientBase:
    """
    Base parser bridge client with core functionality.
    
    Manages connection state and provides foundation for specialized components.
    """

    def __init__(self, websocket_url: str, parser_type: str, parser_version: str = "1.0.0", capabilities: List[str] = None, api_key: str = None, **kwargs):
        """
        Initialize parser bridge client.

        Args:
            websocket_url: WebSocket server URL
            parser_type: Type of parser (encar, autotrader, etc.)
            parser_version: Parser version
            capabilities: List of parser capabilities
            api_key: API key for authentication
            **kwargs: Additional arguments for BridgeClient
        """
        self.parser_type = parser_type
        self.parser_version = parser_version
        self.capabilities = capabilities or []
        self.api_key = api_key

        # Initialize generic bridge client
        self.bridge_client = BridgeClient(
            websocket_url=websocket_url, 
            client_type=f"parser_{parser_type}", 
            client_version=parser_version, 
            api_key=api_key,
            **kwargs
        )

        # Parser state
        self.parser_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.registered = False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.bridge_client.is_connected

    @property
    def is_registered(self) -> bool:
        """Check if parser is registered."""
        return self.registered

    async def send_message(self, message: dict) -> None:
        """Send message through WebSocket bridge."""
        await self.bridge_client._send_message(message)
    
    def add_message_handler(self, message_type: str, handler) -> None:
        """Add message handler for specific message type."""
        self.bridge_client.message_handlers[message_type] = handler

    def _ensure_registered(self) -> None:
        """Ensure parser is registered, raise error if not."""
        if not self.registered:
            raise RuntimeError("Parser not registered")

    def _ensure_connected(self) -> None:
        """Ensure client is connected, raise error if not."""
        if not self.is_connected:
            raise RuntimeError("Client not connected")
