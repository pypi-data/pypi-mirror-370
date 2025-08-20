"""
Base Parser Bridge Server.

Core server functionality and state management.
"""

import asyncio
from typing import Dict, Callable, Optional, List
from unrealon_rpc.bridge import WebSocketBridge
from unrealon_rpc.rpc import RPCServer
from unrealon_rpc.pubsub import PubSubSubscriber
from unrealon_rpc.logging import get_logger

from ..models import (
    ParserInfo, ParserCommand, ParserSession, ParserEvent, ParserSystemStats
)

logger = get_logger(__name__)


class ParserBridgeServerBase:
    """
    Base parser bridge server with core functionality.
    
    Manages server state and provides foundation for specialized handlers.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", rpc_channel: str = "parser_rpc", pubsub_prefix: str = "parser", **kwargs):
        """
        Initialize parser bridge server.

        Args:
            redis_url: Redis connection URL
            rpc_channel: RPC channel name
            pubsub_prefix: PubSub channel prefix
            **kwargs: Additional arguments for WebSocketBridge
        """
        self.redis_url = redis_url
        self.rpc_channel = rpc_channel
        self.pubsub_prefix = pubsub_prefix

        # Initialize bridge components
        self.bridge = WebSocketBridge(
            redis_url=redis_url,
            rpc_channel=rpc_channel,
            pubsub_prefix=pubsub_prefix,
            **kwargs
        )

        # Initialize RPC and PubSub
        self.parser_rpc = RPCServer(channel=rpc_channel, redis_url=redis_url)
        self.parser_pubsub = PubSubSubscriber(channel_prefix=pubsub_prefix, redis_url=redis_url)

        # Server state
        self.parsers: Dict[str, ParserInfo] = {}
        self.sessions: Dict[str, ParserSession] = {}
        self.commands: Dict[str, ParserCommand] = {}
        self.proxies: Dict[str, any] = {}  # Will be typed properly in proxy handler
        
        # Mapping between parser_id and client_id for WebSocket forwarding
        self.parser_to_client: Dict[str, str] = {}

        # Custom command handlers
        self.command_handlers: Dict[str, Callable] = {}

        # Background tasks
        self._tasks: List[asyncio.Task] = []
        self._running = False
    
    def get_client_by_parser_id(self, parser_id: str):
        """Get WebSocket client by parser_id."""
        client_id = self.parser_to_client.get(parser_id)
        if client_id and client_id in self.bridge.connections:
            return self.bridge.connections[client_id]
        return None

    async def start(self) -> None:
        """Start the parser bridge server."""
        if self._running:
            return

        logger.info("Starting Parser Bridge Server...")

        # Start bridge components
        await self.bridge.start()
        await self.parser_rpc.start()
        await self.parser_pubsub.start()

        # Start background tasks
        self._tasks.append(asyncio.create_task(self._pubsub_listener()))

        self._running = True
        logger.info("Parser Bridge Server started")

    async def stop(self) -> None:
        """Stop the parser bridge server."""
        if not self._running:
            return

        logger.info("Stopping Parser Bridge Server...")

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        # Stop bridge components
        await self.parser_pubsub.stop()
        await self.parser_rpc.stop()
        await self.bridge.stop()

        self._running = False
        logger.info("Parser Bridge Server stopped")

    async def _pubsub_listener(self) -> None:
        """Listen to parser events via PubSub."""
        try:
            # Register handler for parser events
            @self.parser_pubsub.subscribe("parser_events")
            async def event_handler(payload: dict):
                try:
                    event = ParserEvent.model_validate(payload)
                    await self._handle_parser_event(event)
                except Exception as e:
                    logger.error(f"Error processing parser event: {e}")
            
            # Start the subscriber (this will run indefinitely)
            await self.parser_pubsub.start()
            
        except asyncio.CancelledError:
            logger.info("PubSub listener cancelled")
        except Exception as e:
            logger.error(f"PubSub listener error: {e}")

    async def _handle_parser_event(self, event: ParserEvent) -> None:
        """
        Handle parser event from PubSub.

        Args:
            event: Parser event to handle
        """
        logger.debug(f"Parser event: {event.event_type} from {event.parser_id}")

    def register_command_handler(self, command_type: str, handler: Callable) -> None:
        """
        Register custom command handler.

        Args:
            command_type: Type of command to handle
            handler: Async handler function
        """
        self.command_handlers[command_type] = handler
        logger.info(f"Registered command handler for: {command_type}")

    def get_parser_stats(self) -> ParserSystemStats:
        """Get parser statistics."""
        parser_types = {}
        for parser in self.parsers.values():
            parser_types[parser.parser_type] = parser_types.get(parser.parser_type, 0) + 1
        
        return ParserSystemStats(
            total_parsers=len(self.parsers),
            active_sessions=len([s for s in self.sessions.values() if s.status == "active"]),
            total_commands=len(self.commands),
            allocated_proxies=len(self.proxies),
            parser_types=parser_types
        )
