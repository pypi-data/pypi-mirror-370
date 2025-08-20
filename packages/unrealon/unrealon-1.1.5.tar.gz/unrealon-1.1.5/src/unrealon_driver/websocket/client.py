"""
Independent WebSocket Client for unrealon_driver.

Provides WebSocket connectivity without dependencies on unrealon_server or unrealon_rpc.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass
from datetime import datetime, timezone

import websockets


@dataclass
class WebSocketConfig:
    """WebSocket client configuration"""
    url: str
    api_key: Optional[str] = None
    parser_id: Optional[str] = None
    reconnect_interval: float = 5.0
    max_reconnect_attempts: int = 10
    ping_interval: float = 30.0
    ping_timeout: float = 10.0


class WebSocketClient:
    """
    Independent WebSocket client for driver-server communication.
    
    Features:
    - Auto-reconnection
    - Message queuing during disconnection
    - Request-response pattern support
    - Event-based message handling
    """
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self._websocket = None
        self._connected = False
        self._reconnect_task = None
        self._message_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._message_queue = []
        self._logger = logging.getLogger(__name__)
        
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        try:
            # Build connection parameters
            connect_params = {
                "ping_interval": self.config.ping_interval,
                "ping_timeout": self.config.ping_timeout
            }
            
            # Add headers if supported (websockets >= 10.0)
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            if self.config.parser_id:
                headers["X-Parser-ID"] = self.config.parser_id
            
            if headers:
                try:
                    # Try with extra_headers first (newer versions)
                    connect_params["extra_headers"] = headers
                    self._websocket = await websockets.connect(self.config.url, **connect_params)
                except TypeError:
                    # Fallback for older versions without extra_headers support
                    connect_params.pop("extra_headers", None)
                    self._websocket = await websockets.connect(self.config.url, **connect_params)
            else:
                self._websocket = await websockets.connect(self.config.url, **connect_params)
            
            self._connected = True
            self._logger.info(f"Connected to WebSocket: {self.config.url}")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
            # Send queued messages
            await self._send_queued_messages()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to connect to WebSocket: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        self._connected = False
        
        if self._reconnect_task:
            self._reconnect_task.cancel()
            
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
            
        self._logger.info("Disconnected from WebSocket")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to server"""
        if not self._connected or not self._websocket:
            # Queue message for later
            self._message_queue.append(message)
            self._logger.debug("Message queued (not connected)")
            return False
            
        try:
            await self._websocket.send(json.dumps(message))
            return True
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")
            self._connected = False
            self._message_queue.append(message)  # Re-queue
            asyncio.create_task(self._reconnect())
            return False
    
    async def send_request(self, message: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send request and wait for response"""
        import uuid
        
        request_id = str(uuid.uuid4())
        message["request_id"] = request_id
        
        # Create future for response
        future = asyncio.Future()
        self._pending_requests[request_id] = future
        
        try:
            # Send request
            success = await self.send_message(message)
            if not success:
                return None
                
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            self._logger.error(f"Request timeout: {request_id}")
            return None
        except Exception as e:
            self._logger.error(f"Request failed: {e}")
            return None
        finally:
            # Clean up
            self._pending_requests.pop(request_id, None)
    
    def add_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Add handler for specific message type"""
        self._message_handlers[message_type] = handler
    
    async def _message_listener(self):
        """Listen for incoming messages"""
        try:
            async for message_str in self._websocket:
                try:
                    message = json.loads(message_str)
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    self._logger.error(f"Invalid JSON received: {message_str}")
                except Exception as e:
                    self._logger.error(f"Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self._logger.warning("WebSocket connection closed")
            self._connected = False
            asyncio.create_task(self._reconnect())
        except Exception as e:
            self._logger.error(f"Message listener error: {e}")
            self._connected = False
            asyncio.create_task(self._reconnect())
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        # Check if it's a response to a pending request
        request_id = message.get("request_id")
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests[request_id]
            if not future.done():
                future.set_result(message)
            return
        
        # Handle by message type
        message_type = message.get("type")
        if message_type and message_type in self._message_handlers:
            try:
                await self._message_handlers[message_type](message)
            except Exception as e:
                self._logger.error(f"Handler error for {message_type}: {e}")
    
    async def _send_queued_messages(self):
        """Send all queued messages"""
        while self._message_queue and self._connected:
            message = self._message_queue.pop(0)
            success = await self.send_message(message)
            if not success:
                # Re-queue and stop
                self._message_queue.insert(0, message)
                break
    
    async def _reconnect(self):
        """Auto-reconnect with exponential backoff"""
        if self._reconnect_task:
            return  # Already reconnecting
            
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
        """Reconnection loop with backoff"""
        attempt = 0
        
        while attempt < self.config.max_reconnect_attempts and not self._connected:
            attempt += 1
            wait_time = min(self.config.reconnect_interval * (2 ** (attempt - 1)), 60)
            
            self._logger.info(f"Reconnecting in {wait_time}s (attempt {attempt}/{self.config.max_reconnect_attempts})")
            await asyncio.sleep(wait_time)
            
            if await self.connect():
                self._logger.info("Reconnected successfully")
                break
        
        if not self._connected:
            self._logger.error("Max reconnection attempts reached")
        
        self._reconnect_task = None
    
    @property
    def connected(self) -> bool:
        """Check if connected"""
        return self._connected and self._websocket is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "connected": self._connected,
            "url": self.config.url,
            "queued_messages": len(self._message_queue),
            "pending_requests": len(self._pending_requests),
            "handlers": list(self._message_handlers.keys())
        }
