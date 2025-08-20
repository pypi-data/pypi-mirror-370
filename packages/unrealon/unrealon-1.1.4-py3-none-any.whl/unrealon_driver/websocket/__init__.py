"""
WebSocket module for unrealon_driver.

Provides independent WebSocket connectivity for:
- Logging transport
- HTML analysis requests
- Other driver-server communication

Features automatic URL detection - no need to specify URLs in config files!
"""

from .client import WebSocketClient, WebSocketConfig
from .manager import WebSocketManager
from .config import (
    GlobalWebSocketConfig, Environment, global_websocket_config,
    get_websocket_url, get_environment, set_environment,
    get_debug_info, is_production, is_development, is_local
)

# Global websocket manager instance
websocket_manager = WebSocketManager()

__all__ = [
    # Client and manager
    "WebSocketClient", "WebSocketConfig", "WebSocketManager", "websocket_manager",
    # Global configuration
    "GlobalWebSocketConfig", "Environment", "global_websocket_config",
    # Convenience functions
    "get_websocket_url", "get_environment", "set_environment",
    "get_debug_info", "is_production", "is_development", "is_local"
]
