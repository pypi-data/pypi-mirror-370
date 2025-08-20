"""
Parser Bridge Server - Modular implementation with composition.

Clean architecture with separated handlers and no inheritance hell.
"""

from typing import Callable
from unrealon_rpc.logging import get_logger

from .base import ParserBridgeServerBase
from .handlers import ParserHandlers, SessionHandlers, CommandHandlers, ProxyHandlers, HTMLParserHandlers, LoggingHandlers, SchedulerHandlers

from ..models import ParserSystemStats

logger = get_logger(__name__)


class ParserBridgeServer(
    ParserBridgeServerBase,
    ParserHandlers,
    SessionHandlers,
    CommandHandlers,
    ProxyHandlers,
    HTMLParserHandlers,
    LoggingHandlers,
    SchedulerHandlers
):
    """
    Complete Parser Bridge Server with all functionality.
    
    Combines base server with all handlers to provide full server capabilities:
    - Parser registration and management
    - Session lifecycle management
    - Command execution and tracking
    - Proxy allocation and management
    - HTML parsing via AI/LLM integration
    - Parser logging to Django backend
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", rpc_channel: str = "parser_rpc", pubsub_prefix: str = "parser", **kwargs):
        """
        Initialize complete parser bridge server.

        Args:
            redis_url: Redis connection URL
            rpc_channel: RPC channel name
            pubsub_prefix: PubSub channel prefix
            **kwargs: Additional arguments for WebSocketBridge
        """
        super().__init__(redis_url, rpc_channel, pubsub_prefix, **kwargs)
        self._register_rpc_methods()

    def _register_rpc_methods(self) -> None:
        """Register all RPC methods with their handlers."""
        # Parser management
        self.parser_rpc.register_method("parser.register", self.handle_parser_register)
        self.parser_rpc.register_method("parser.get_status", self.handle_parser_get_status)
        self.parser_rpc.register_method("parser.list", self.handle_parser_list)
        self.parser_rpc.register_method("parser.get_health", self.handle_parser_get_health)

        # Session management
        self.parser_rpc.register_method("parser.start_session", self.handle_session_start)
        self.parser_rpc.register_method("parser.end_session", self.handle_session_end)

        # Command management
        self.parser_rpc.register_method("parser.execute_command", self.handle_command_execute)
        self.parser_rpc.register_method("command.create", self.handle_command_create)
        self.parser_rpc.register_method("command.get_status", self.handle_command_get_status)

        # Proxy management
        self.parser_rpc.register_method("proxy.allocate", self.handle_proxy_allocate)
        self.parser_rpc.register_method("proxy.release", self.handle_proxy_release)
        self.parser_rpc.register_method("proxy.check", self.handle_proxy_check)

        # HTML Parser management
        self.parser_rpc.register_method("html_parser.parse", self.handle_html_parse)

        # Parser Logging
        self.parser_rpc.register_method("parser.log", self.handle_parser_log)
        
        # Scheduler management
        self.parser_rpc.register_method("scheduler.create_task", self.handle_scheduler_create_task)
        self.parser_rpc.register_method("scheduler.list_tasks", self.handle_scheduler_list_tasks)
        self.parser_rpc.register_method("scheduler.get_task", self.handle_scheduler_get_task)
        self.parser_rpc.register_method("scheduler.cancel_task", self.handle_scheduler_cancel_task)
        self.parser_rpc.register_method("scheduler.update_parser_status", self.handle_scheduler_update_parser_status)
        self.parser_rpc.register_method("scheduler.get_parser_status", self.handle_scheduler_get_parser_status)
        self.parser_rpc.register_method("scheduler.get_stats", self.handle_scheduler_get_stats)


__all__ = ["ParserBridgeServer"]
