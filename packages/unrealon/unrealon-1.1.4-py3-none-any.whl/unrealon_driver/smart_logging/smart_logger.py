"""
SmartLogger: Intelligent logging with batching and WebSocket transport.

Features:
- Automatic batching of logs (every 5 seconds)
- Smart WebSocket connection management (daemon vs script mode)
- Local file/console logging as fallback
- Standard logging API for developers
- No blocking of main thread
"""

import asyncio
import json
import logging
import time
import weakref
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from collections import deque

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException


@dataclass
class LogEntry:
    """Structure for log entry"""
    timestamp: str
    level: str
    message: str
    parser_id: str
    session_id: Optional[str] = None
    url: Optional[str] = None
    operation: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class LogBuffer:
    """Thread-safe buffer for accumulating logs"""
    
    def __init__(self, max_size: int = 1000):
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = asyncio.Lock()
    
    async def add(self, entry: LogEntry):
        """Add log entry to buffer"""
        async with self.lock:
            self.buffer.append(entry)
    
    async def flush(self) -> List[LogEntry]:
        """Get all logs and clear buffer"""
        async with self.lock:
            entries = list(self.buffer)
            self.buffer.clear()
            return entries
    
    def size(self) -> int:
        """Get buffer size"""
        return len(self.buffer)


class ConnectionManager:
    """Smart WebSocket connection manager"""
    
    def __init__(self, bridge_logs_url: str, parser_id: str):
        self.bridge_logs_url = bridge_logs_url
        self.parser_id = parser_id
        self.websocket = None
        self.is_connected = False
        self.connection_lock = asyncio.Lock()
        self.last_activity = time.time()
        
        # Connection mode
        self.daemon_mode = False
        self.connection_timeout = 30  # Close connection after 30s of inactivity
    
    async def ensure_connection(self) -> bool:
        """Ensure active WebSocket connection"""
        async with self.connection_lock:
            if self.is_connected and self.websocket:
                return True
            
            try:
                self.websocket = await websockets.connect(
                    self.bridge_logs_url,
                    ping_interval=20,
                    ping_timeout=10
                )
                self.is_connected = True
                self.last_activity = time.time()
                return True
                
            except Exception:
                self.is_connected = False
                self.websocket = None
                return False
    
    async def send_batch(self, entries: List[LogEntry]) -> bool:
        """Send batch of logs"""
        if not entries:
            return True
        
        if not await self.ensure_connection():
            return False
        
        try:
            # Prepare batch
            batch = {
                "type": "log_batch",
                "parser_id": self.parser_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "entries": [asdict(entry) for entry in entries]
            }
            
            # Send batch
            await self.websocket.send(json.dumps(batch))
            self.last_activity = time.time()
            
            # In script mode, close connection immediately
            if not self.daemon_mode:
                await self.close()
            
            return True
            
        except Exception:
            self.is_connected = False
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
                finally:
                    self.websocket = None
            return False
    
    async def close(self):
        """Close WebSocket connection"""
        async with self.connection_lock:
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
                finally:
                    self.websocket = None
                    self.is_connected = False
    
    def set_daemon_mode(self, daemon_mode: bool):
        """Set connection mode"""
        self.daemon_mode = daemon_mode


class SmartLogger:
    """
    Smart logger with batching and WebSocket transport.
    
    Features:
    - Buffers logs in memory
    - Sends batches every 5 seconds
    - Smart WebSocket connection management
    - Auto-detects daemon vs script mode
    - Local logs as fallback
    """
    
    # Global registry for cleanup
    _instances = weakref.WeakSet()
    _cleanup_task = None
    
    def __init__(
        self,
        parser_id: str,
        bridge_logs_url: Optional[str] = None,
        log_file: Optional[Path] = None,
        console_enabled: bool = True,
        batch_interval: float = 5.0,
        daemon_mode: Optional[bool] = None
    ):
        self.parser_id = parser_id
        self.bridge_logs_url = bridge_logs_url
        self.batch_interval = batch_interval
        self.session_id = None
        
        # Local logger (always works)
        self.local_logger = self._setup_local_logger(log_file, console_enabled)
        
        # Bridge components (optional)
        self.bridge_enabled = bridge_logs_url is not None
        self.log_buffer = LogBuffer() if self.bridge_enabled else None
        self.connection_manager = ConnectionManager(bridge_logs_url, parser_id) if self.bridge_enabled else None
        
        # Detect daemon mode
        if daemon_mode is None:
            daemon_mode = self._detect_daemon_mode()
        
        if self.connection_manager:
            self.connection_manager.set_daemon_mode(daemon_mode)
        
        # Batch timer (lazy initialization)
        self._batch_task = None
        self._batch_timer_started = False
        
        # Register for cleanup
        SmartLogger._instances.add(self)
        
        # Global cleanup task (lazy initialization)
        self._ensure_global_cleanup()
    
    def info(self, message: str, **kwargs):
        """Log INFO message"""
        self._log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR message"""
        self._log("ERROR", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING message"""
        self._log("WARNING", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log DEBUG message"""
        self._log("DEBUG", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log CRITICAL message"""
        self._log("CRITICAL", message, **kwargs)
    
    def set_session(self, session_id: str):
        """Set session ID for all future logs"""
        self.session_id = session_id
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method"""
        # Local log (always, synchronous)
        extra = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool))}
        getattr(self.local_logger, level.lower())(message, extra=extra)
        
        # Bridge log (asynchronous, if enabled)
        if self.bridge_enabled and self.log_buffer:
            entry = LogEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                level=level,
                message=message,
                parser_id=self.parser_id,
                session_id=self.session_id,
                url=kwargs.get('url'),
                operation=kwargs.get('operation'),
                extra=kwargs if kwargs else None
            )
            
            # Add to buffer (non-blocking)
            asyncio.create_task(self.log_buffer.add(entry))
    
    def _detect_daemon_mode(self) -> bool:
        """Auto-detect daemon vs script mode"""
        try:
            # If there's an active event loop, likely daemon mode
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
    
    def _ensure_global_cleanup(self):
        """Ensure global cleanup task is started (lazy)"""
        try:
            # Only start if we have an event loop
            asyncio.get_running_loop()
            if SmartLogger._cleanup_task is None:
                SmartLogger._cleanup_task = asyncio.create_task(SmartLogger._global_cleanup())
        except RuntimeError:
            # No event loop, will start later when needed
            pass
    
    def _ensure_batch_timer(self):
        """Ensure batch timer is started (lazy)"""
        if not self.bridge_enabled or self._batch_timer_started:
            return
        
        try:
            # Only start if we have an event loop
            asyncio.get_running_loop()
            self._start_batch_timer()
            self._batch_timer_started = True
        except RuntimeError:
            # No event loop, will start later when logging happens
            pass
    
    def _start_batch_timer(self):
        """Start batch timer"""
        if self._batch_task is None or self._batch_task.done():
            self._batch_task = asyncio.create_task(self._batch_loop())
    
    async def _batch_loop(self):
        """Main batch sending loop"""
        try:
            while True:
                await asyncio.sleep(self.batch_interval)
                await self._send_batch()
        except asyncio.CancelledError:
            # Final batch send on cancellation
            await self._send_batch()
            raise
    
    async def _send_batch(self):
        """Send accumulated logs"""
        if not self.log_buffer or not self.connection_manager:
            return
        
        entries = await self.log_buffer.flush()
        if entries:
            success = await self.connection_manager.send_batch(entries)
            # If sending failed, logs are already saved locally
    
    async def flush(self):
        """Force send all accumulated logs"""
        if self.bridge_enabled:
            await self._send_batch()
    
    async def close(self):
        """Close logger and cleanup resources"""
        # Send remaining logs
        await self.flush()
        
        # Stop batch timer
        if self._batch_task and not self._batch_task.done():
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
        
        # Close connection
        if self.connection_manager:
            await self.connection_manager.close()
    
    def _setup_local_logger(self, log_file: Optional[Path], console_enabled: bool):
        """Setup local file/console logger"""
        logger = logging.getLogger(f"unrealon_parser_{self.parser_id}")
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
        
        # Console handler
        if console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
            )
            logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    async def _global_cleanup(cls):
        """Global cleanup of all loggers on program exit"""
        try:
            # Wait for program termination
            while True:
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            # Close all active loggers
            for logger in list(cls._instances):
                try:
                    await logger.close()
                except:
                    pass
    
    def __del__(self):
        """Destructor - attempt to cleanup resources"""
        if self._batch_task and not self._batch_task.done():
            self._batch_task.cancel()


def create_smart_logger(
    parser_id: str,
    bridge_logs_url: Optional[str] = None,
    **kwargs
) -> SmartLogger:
    """
    Create smart logger with optimal settings.
    
    Args:
        parser_id: Parser identifier
        bridge_logs_url: WebSocket URL for Bridge logs (ws://localhost:8001/logs)
        **kwargs: Additional parameters
    
    Returns:
        Configured SmartLogger instance
    """
    return SmartLogger(
        parser_id=parser_id,
        bridge_logs_url=bridge_logs_url,
        **kwargs
    )
