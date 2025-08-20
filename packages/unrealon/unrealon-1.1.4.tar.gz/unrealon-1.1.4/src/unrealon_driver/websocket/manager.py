"""
WebSocket Manager for unrealon_driver.

Manages shared WebSocket connection for multiple use cases:
- Logging transport
- HTML analysis requests  
- Other driver-server communication
"""

import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from .client import WebSocketClient, WebSocketConfig


class WebSocketManager:
    """
    Singleton WebSocket manager for the driver.
    
    Provides shared WebSocket connection for:
    - SmartLogger (log batching)
    - ParserManager (HTML analysis)
    - Other driver components
    """
    
    _instance: Optional['WebSocketManager'] = None
    _client: Optional[WebSocketClient] = None
    
    def __new__(cls) -> 'WebSocketManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._client = None
            self._config = None
    
    async def initialize(self, config: WebSocketConfig) -> bool:
        """Initialize WebSocket connection"""
        if self._client:
            await self._client.disconnect()
        
        self._config = config
        self._client = WebSocketClient(config)
        
        return await self._client.connect()
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message via WebSocket"""
        if not self._client:
            return False
        return await self._client.send_message(message)
    
    async def send_request(self, message: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send request and wait for response"""
        if not self._client:
            return None
        return await self._client.send_request(message, timeout)
    
    def add_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Add message handler"""
        if self._client:
            self._client.add_message_handler(message_type, handler)
    
    async def disconnect(self):
        """Disconnect WebSocket"""
        if self._client:
            await self._client.disconnect()
            self._client = None
    
    @property
    def connected(self) -> bool:
        """Check if connected"""
        return self._client is not None and self._client.connected
    
    @property
    def client(self) -> Optional[WebSocketClient]:
        """Get underlying client"""
        return self._client
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        if self._client:
            return self._client.get_stats()
        return {"connected": False}


# Global instance
websocket_manager = WebSocketManager()
