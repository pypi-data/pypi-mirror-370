"""
Unified Logger: Smart + Rich + Structured.

Combines:
- SmartLogger: WebSocket batching, connection management
- Rich console: Beautiful colored output
- Structured logging: Context management and metadata
"""

import asyncio
import logging
import yaml
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

from rich.console import Console
from rich.text import Text

from .smart_logger import ConnectionManager, LogBuffer
from .models import LogLevel, LogContext, LogEntry


def get_project_root() -> Path:
    """
    Get the project root directory (backend/unrealon-rpc/).
    
    Returns:
        Path to the project root directory
    """
    # This file is in src/unrealon_driver/smart_logging/unified_logger.py
    # Path levels: unified_logger.py -> smart_logging -> unrealon_driver -> src -> backend/unrealon-rpc/
    return Path(__file__).parent.parent.parent.parent


def resolve_log_path(relative_path: str) -> Path:
    """
    Resolve a relative log path to an absolute path within the project.
    
    Args:
        relative_path: Relative path like "logs/parser_name.log"
        
    Returns:
        Absolute path to the log file
    """
    project_root = get_project_root()
    return project_root / relative_path


class UnifiedLoggerConfig(BaseModel):
    """Configuration for unified logger"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Parser identity
    parser_id: str = Field(..., min_length=1)
    parser_name: str = Field(..., min_length=1)
    
    # Local logging
    log_file: Optional[Path] = Field(default=None)
    console_enabled: bool = Field(default=True)
    file_enabled: bool = Field(default=True)
    
    # WebSocket logging
    bridge_logs_url: Optional[str] = Field(default=None)
    batch_interval: float = Field(default=5.0, gt=0.0)
    daemon_mode: Optional[bool] = Field(default=None)
    
    # Log levels
    console_level: LogLevel = Field(default=LogLevel.INFO)
    file_level: LogLevel = Field(default=LogLevel.DEBUG)
    bridge_level: LogLevel = Field(default=LogLevel.INFO)


class UnifiedLogger:
    """
    🚀 Unified Logger: Smart + Rich + Structured
    
    Features from SmartLogger:
    - WebSocket batching and transport
    - Smart connection management
    - Daemon vs script mode detection
    
    Features from LegacyManager:
    - Rich console output with colors
    - Structured logging with context
    - Multiple output destinations
    
    Developer Experience:
    - Simple API: logger.info("message")
    - Context management: logger.set_session("123")
    - Automatic batching and fallback
    """
    
    def __init__(self, config: UnifiedLoggerConfig):
        self.config = config
        self._context = LogContext()
        
        # Rich console
        self.console = Console() if config.console_enabled else None
        
        # Local file logger
        self.file_logger = self._setup_file_logger() if config.file_enabled else None
        
        # SmartLogger components (WebSocket)
        self.bridge_enabled = config.bridge_logs_url is not None
        if self.bridge_enabled:
            self.log_buffer = LogBuffer()
            self.connection_manager = ConnectionManager(
                config.bridge_logs_url, 
                config.parser_id
            )
            
            # Detect daemon mode
            daemon_mode = config.daemon_mode
            if daemon_mode is None:
                daemon_mode = self._detect_daemon_mode()
            self.connection_manager.set_daemon_mode(daemon_mode)
            
            # Start batch timer
            self._batch_task = None
            self._ensure_batch_timer()
        else:
            self.log_buffer = None
            self.connection_manager = None
            self._batch_task = None
    
    # ==========================================
    # PUBLIC LOGGING API
    # ==========================================
    
    def debug(self, message: str, **kwargs):
        """Log DEBUG message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log INFO message"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING message"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR message"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log CRITICAL message"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    # Aliases
    warn = warning
    
    # ==========================================
    # CONTEXT MANAGEMENT
    # ==========================================
    
    def set_session(self, session_id: str):
        """Set session ID for all future logs"""
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")
        self._context.session_id = session_id
    
    def set_operation(self, operation: str):
        """Set current operation"""
        if not operation.strip():
            raise ValueError("Operation cannot be empty")
        self._context.operation = operation
    
    def set_url(self, url: str):
        """Set current URL"""
        if not url.strip():
            raise ValueError("URL cannot be empty")
        self._context.url = url
    
    def add_context_data(self, key: str, value: str):
        """Add additional context data"""
        if not key.strip():
            raise ValueError("Context key cannot be empty")
        self._context.additional_data[key] = str(value)
    
    def clear_context(self):
        """Clear all context"""
        self._context = LogContext()
    
    # ==========================================
    # SPECIALIZED LOGGING METHODS
    # ==========================================
    
    def start_operation(self, operation: str, **kwargs):
        """Log start of operation"""
        self.set_operation(operation)
        self.info(f"🚀 Starting {operation}", **kwargs)
    
    def end_operation(self, operation: str, duration: Optional[float] = None, **kwargs):
        """Log end of operation"""
        if duration is not None:
            self.info(f"✅ Completed {operation} in {duration:.2f}s", duration=str(duration), **kwargs)
        else:
            self.info(f"✅ Completed {operation}", **kwargs)
    
    def fail_operation(self, operation: str, error: str, **kwargs):
        """Log failed operation"""
        self.error(f"❌ Failed {operation}: {error}", error=error, **kwargs)
    
    def url_access(self, url: str, status: str = "accessing", **kwargs):
        """Log URL access"""
        self.set_url(url)
        self.info(f"🌐 {status.title()} URL: {url}", status=status, **kwargs)
    
    def data_extracted(self, data_type: str, count: int, **kwargs):
        """Log data extraction"""
        if count < 0:
            raise ValueError("Count must be non-negative")
        
        self.info(
            f"📦 Extracted {count} {data_type}",
            data_type=data_type,
            count=str(count),
            **kwargs
        )
    
    # ==========================================
    # INTERNAL IMPLEMENTATION
    # ==========================================
    
    def _format_value_for_console(self, value: Any) -> str:
        """Format value for console output with YAML for complex objects"""
        if value is None:
            return "None"
        elif isinstance(value, (str, int, float, bool)):
            return str(value)
        elif isinstance(value, (dict, list, tuple)):
            try:
                # Use YAML for complex objects - more readable than JSON
                yaml_str = yaml.dump(value, default_flow_style=True, allow_unicode=True)
                # Remove trailing newline and make it one-line for console
                return yaml_str.strip().replace('\n', ' ')
            except Exception:
                return str(value)
        else:
            # For custom objects, try to convert to dict first
            try:
                if hasattr(value, 'model_dump'):  # Pydantic
                    dict_value = value.model_dump()
                elif hasattr(value, '__dict__'):  # Regular objects
                    dict_value = value.__dict__
                else:
                    return str(value)
                
                yaml_str = yaml.dump(dict_value, default_flow_style=True, allow_unicode=True)
                return yaml_str.strip().replace('\n', ' ')
            except Exception:
                return str(value)
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method"""
        # Create context from current context + kwargs
        context = self._create_context(**kwargs)
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level.value,
            message=message,
            parser_id=self.config.parser_id,
            session_id=context.session_id,
            url=context.url,
            operation=context.operation,
            extra=context.additional_data if context.additional_data else None
        )
        
        # Console output (Rich)
        if self.console and self._should_log_to_console(level):
            self._log_to_console(log_entry, level)
        
        # File output
        if self.file_logger and self._should_log_to_file(level):
            self._log_to_file(log_entry, level)
        
        # WebSocket output (batched) - ALWAYS send to bridge regardless of level
        if self.bridge_enabled:
            self._log_to_bridge(log_entry)
    
    def _create_context(self, **kwargs) -> LogContext:
        """Create log context from current context and kwargs"""
        context_data = self._context.additional_data.copy()
        
        # Add kwargs - keep original types for console formatting
        for key, value in kwargs.items():
            if key not in ['session_id', 'command_id', 'operation', 'url']:
                context_data[key] = value  # Keep original type
        
        return LogContext(
            session_id=kwargs.get('session_id') or self._context.session_id,
            command_id=kwargs.get('command_id') or self._context.command_id,
            operation=kwargs.get('operation') or self._context.operation,
            url=kwargs.get('url') or self._context.url,
            additional_data=context_data
        )
    
    def _should_log_to_console(self, level: LogLevel) -> bool:
        """Check if should log to console"""
        level_value = getattr(logging, level.value)
        console_level_value = getattr(logging, self.config.console_level.value)
        return level_value >= console_level_value
    
    def _should_log_to_file(self, level: LogLevel) -> bool:
        """Check if should log to file"""
        level_value = getattr(logging, level.value)
        file_level_value = getattr(logging, self.config.file_level.value)
        return level_value >= file_level_value
    
    def _should_log_to_bridge(self, level: LogLevel) -> bool:
        """Check if should log to bridge - ALWAYS True now"""
        return True  # Always send to bridge regardless of level
    
    def _log_to_console(self, log_entry: LogEntry, level: LogLevel):
        """Log to console with Rich formatting"""
        if not self.console:
            return
        
        # Parse timestamp for display
        try:
            from datetime import datetime
            timestamp = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
            time_str = timestamp.strftime('%H:%M:%S')
        except:
            time_str = "00:00:00"
        
        # Color based on level
        level_colors = {
            LogLevel.DEBUG: "dim white",
            LogLevel.INFO: "bright_blue",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red"
        }
        
        level_color = level_colors.get(level, "white")
        
        # Format message
        formatted_message = Text()
        formatted_message.append(f"[{time_str}] ", style="dim")
        formatted_message.append(f"{level.value}", style=level_color)
        formatted_message.append(f" - {self.config.parser_name} - ", style="dim")
        formatted_message.append(log_entry.message, style="white")
        
        # Add context if available
        context_parts = []
        if log_entry.extra:
            for key, value in log_entry.extra.items():
                context_parts.append(f"{key}={value}")
        
        if context_parts:
            formatted_message.append(f" ({', '.join(context_parts)})", style="dim")
        
        self.console.print(formatted_message)
    
    def _log_to_file(self, log_entry: LogEntry, level: LogLevel):
        """Log to file"""
        if not self.file_logger:
            return
        
        try:
            # Create log message with context
            extra_info = ""
            if log_entry.extra:
                context_parts = [f"{k}={v}" for k, v in log_entry.extra.items()]
                extra_info = f" - {', '.join(context_parts)}"
            
            full_message = f"{log_entry.message}{extra_info}"
            
            # Log to file
            log_level = getattr(logging, level.value)
            self.file_logger.log(log_level, full_message)
            
        except Exception:
            # Fail silently for file logging
            pass
    
    def _log_to_bridge(self, log_entry: LogEntry):
        """Log to bridge via WebSocket (batched)"""
        if not self.log_buffer:
            return
        
        # Add to buffer (non-blocking)
        try:
            asyncio.create_task(self.log_buffer.add(log_entry))
        except RuntimeError:
            # No event loop, skip bridge logging
            pass
    
    def _setup_file_logger(self) -> Optional[logging.Logger]:
        """Setup file logger"""
        if not self.config.log_file:
            return None
        
        # Ensure log directory exists
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file logger
        logger_name = f"unified_{self.config.parser_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, self.config.file_level.value))
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add file handler
        file_handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.config.file_level.value))
        
        # Format for file logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.propagate = False
        
        return logger
    
    def _detect_daemon_mode(self) -> bool:
        """Auto-detect daemon vs script mode"""
        try:
            # If there's an active event loop, likely daemon mode
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
    
    def _ensure_batch_timer(self):
        """Ensure batch timer is started"""
        if self._batch_task is None or self._batch_task.done():
            try:
                asyncio.get_running_loop()
                self._batch_task = asyncio.create_task(self._batch_loop())
            except RuntimeError:
                # No event loop, will start later
                pass
    
    async def _batch_loop(self):
        """Main batch sending loop"""
        try:
            while True:
                await asyncio.sleep(self.config.batch_interval)
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
            await self.connection_manager.send_batch(entries)
    
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


def create_unified_logger(
    parser_id: str,
    parser_name: str,
    bridge_logs_url: Optional[str] = None,
    log_file: Optional[Path] = None,
    **kwargs
) -> UnifiedLogger:
    """
    Create unified logger with optimal settings.
    
    Args:
        parser_id: Parser identifier
        parser_name: Parser name
        bridge_logs_url: WebSocket URL for Bridge logs
        log_file: Local log file path (if None, creates default path)
        **kwargs: Additional configuration
    
    Returns:
        Configured UnifiedLogger instance
    """
    # Auto-create log file path if not provided
    if log_file is None and kwargs.get('file_enabled', True):
        log_file = resolve_log_path(f"logs/{parser_name}.log")
    
    config = UnifiedLoggerConfig(
        parser_id=parser_id,
        parser_name=parser_name,
        bridge_logs_url=bridge_logs_url,
        log_file=log_file,
        **kwargs
    )
    
    return UnifiedLogger(config)
