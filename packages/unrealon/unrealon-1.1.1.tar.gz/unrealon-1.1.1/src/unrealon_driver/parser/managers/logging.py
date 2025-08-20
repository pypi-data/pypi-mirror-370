"""
Logging Manager - Universal logging for parser developers with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- Custom exception hierarchy
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from unrealon_rpc.logging import get_logger


class LogLevel(str, Enum):
    """Log levels for driver logger"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseModel):
    """Logging configuration with strict typing"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    parser_name: str = Field(
        ...,
        min_length=1,
        description="Name of the parser"
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "logs",
        description="Directory for log files"
    )
    console_enabled: bool = Field(
        default=True,
        description="Enable console output"
    )
    file_enabled: bool = Field(
        default=True,
        description="Enable file logging"
    )
    bridge_enabled: bool = Field(
        default=True,
        description="Enable bridge logging"
    )
    console_level: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="Minimum level for console output"
    )
    file_level: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="Minimum level for file logging"
    )
    bridge_level: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="Minimum level for bridge logging"
    )
    
    @field_validator('parser_name')
    @classmethod
    def validate_parser_name(cls, v: str) -> str:
        """Validate parser name is not empty"""
        if not v.strip():
            raise ValueError("Parser name cannot be empty")
        return v.strip()
    
    def model_post_init(self, __context) -> None:
        """Create log directory if it doesn't exist"""
        self.log_dir.mkdir(parents=True, exist_ok=True)


class LogContext(BaseModel):
    """Log context information"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    session_id: Optional[str] = Field(default=None)
    command_id: Optional[str] = Field(default=None)
    operation: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    additional_data: dict[str, str] = Field(default_factory=dict)


class LogEntry(BaseModel):
    """Log entry with structured data"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    level: LogLevel = Field(...)
    message: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    parser_name: str = Field(..., min_length=1)
    context: LogContext = Field(default_factory=LogContext)


class LoggingManagerError(Exception):
    """Base exception for logging manager"""
    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class BridgeLoggingError(LoggingManagerError):
    """Raised when bridge logging fails"""
    pass


class FileLoggingError(LoggingManagerError):
    """Raised when file logging fails"""
    pass


class LoggingManager:
    """
    📝 Logging Manager - Universal logging for parser developers
    
    Features:
    - Rich console output with colors and formatting
    - File logging to developer-specified directory
    - Bridge logging (sends all logs to Django via bridge)
    - Easy-to-use API with multiple log levels
    - Configurable output formats and destinations
    - Type-safe logging with Pydantic v2
    """
    
    def __init__(
        self,
        config: LoggingConfig,
        bridge_client: Optional[Any] = None
    ):
        self.config = config
        self.bridge_client = bridge_client
        self._context = LogContext()
        
        # Setup console
        if self.config.console_enabled:
            self.console = Console()
        else:
            self.console = None
        
        # Setup file logger
        self.file_logger: Optional[logging.Logger] = None
        if self.config.file_enabled:
            self._setup_file_logger()
        
        # Fallback logger for internal logging
        self.internal_logger = get_logger()
    
    def _setup_file_logger(self) -> None:
        """Setup file logger"""
        log_file = self._get_log_file_path()
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file logger
        logger_name = f"driver_{self.config.parser_name}"
        self.file_logger = logging.getLogger(logger_name)
        self.file_logger.setLevel(getattr(logging, self.config.file_level.value))
        
        # Remove existing handlers
        for handler in self.file_logger.handlers[:]:
            self.file_logger.removeHandler(handler)
        
        # Add file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.config.file_level.value))
        
        # Format for file logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.file_logger.addHandler(file_handler)
        self.file_logger.propagate = False
    
    # ==========================================
    # CONTEXT MANAGEMENT
    # ==========================================
    
    def set_session(self, session_id: str) -> None:
        """Set current session ID for context"""
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")
        self._context.session_id = session_id
    
    def set_command(self, command_id: str) -> None:
        """Set current command ID for context"""
        if not command_id.strip():
            raise ValueError("Command ID cannot be empty")
        self._context.command_id = command_id
    
    def set_operation(self, operation: str) -> None:
        """Set current operation for context"""
        if not operation.strip():
            raise ValueError("Operation cannot be empty")
        self._context.operation = operation
    
    def set_url(self, url: str) -> None:
        """Set current URL for context"""
        if not url.strip():
            raise ValueError("URL cannot be empty")
        self._context.url = url
    
    def add_context_data(self, key: str, value: str) -> None:
        """Add additional context data"""
        if not key.strip():
            raise ValueError("Context key cannot be empty")
        self._context.additional_data[key] = str(value)
    
    def clear_context(self) -> None:
        """Clear all context"""
        self._context = LogContext()
    
    # ==========================================
    # SYNCHRONOUS LOGGING METHODS
    # ==========================================
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    # Aliases
    warn = warning
    
    # ==========================================
    # ASYNCHRONOUS LOGGING METHODS
    # ==========================================
    
    async def debug_async(self, message: str, **kwargs) -> None:
        """Log debug message (async)"""
        await self._log_async(LogLevel.DEBUG, message, **kwargs)
    
    async def info_async(self, message: str, **kwargs) -> None:
        """Log info message (async)"""
        await self._log_async(LogLevel.INFO, message, **kwargs)
    
    async def warning_async(self, message: str, **kwargs) -> None:
        """Log warning message (async)"""
        await self._log_async(LogLevel.WARNING, message, **kwargs)
    
    async def error_async(self, message: str, **kwargs) -> None:
        """Log error message (async)"""
        await self._log_async(LogLevel.ERROR, message, **kwargs)
    
    async def critical_async(self, message: str, **kwargs) -> None:
        """Log critical message (async)"""
        await self._log_async(LogLevel.CRITICAL, message, **kwargs)
    
    # Aliases
    warn_async = warning_async
    
    # ==========================================
    # SPECIALIZED LOGGING METHODS
    # ==========================================
    
    def start_operation(self, operation: str, **kwargs) -> None:
        """Log start of operation"""
        self.set_operation(operation)
        self.info(f"🚀 Starting {operation}", **kwargs)
    
    def end_operation(self, operation: str, duration: Optional[float] = None, **kwargs) -> None:
        """Log end of operation"""
        if duration is not None:
            self.info(f"✅ Completed {operation} in {duration:.2f}s", duration=str(duration), **kwargs)
        else:
            self.info(f"✅ Completed {operation}", **kwargs)
    
    def fail_operation(self, operation: str, error: str, **kwargs) -> None:
        """Log failed operation"""
        self.error(f"❌ Failed {operation}: {error}", error=error, **kwargs)
    
    def progress(self, message: str, current: int, total: int, **kwargs) -> None:
        """Log progress information"""
        if total <= 0:
            raise ValueError("Total must be positive")
        if current < 0:
            raise ValueError("Current must be non-negative")
        
        percentage = (current / total * 100)
        self.info(
            f"📊 {message} ({current}/{total} - {percentage:.1f}%)",
            current=str(current),
            total=str(total),
            percentage=f"{percentage:.1f}",
            **kwargs
        )
    
    def url_access(self, url: str, status: str = "accessing", **kwargs) -> None:
        """Log URL access"""
        self.set_url(url)
        self.info(f"🌐 {status.title()} URL: {url}", status=status, **kwargs)
    
    def data_extracted(self, data_type: str, count: int, **kwargs) -> None:
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
    # INTERNAL LOGGING IMPLEMENTATION
    # ==========================================
    
    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal synchronous logging"""
        # Create log entry
        context = self._create_context(**kwargs)
        log_entry = LogEntry(
            level=level,
            message=message,
            parser_name=self.config.parser_name,
            context=context
        )
        
        # Console output
        if self.config.console_enabled and self._should_log_to_console(level):
            self._log_to_console(log_entry)
        
        # File output
        if self.config.file_enabled and self._should_log_to_file(level):
            self._log_to_file(log_entry)
        
        # Bridge output (async in background)
        if self.config.bridge_enabled and self.bridge_client and self._should_log_to_bridge(level):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._log_to_bridge_async(log_entry))
            except RuntimeError:
                # No event loop, skip bridge logging
                pass
    
    async def _log_async(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal asynchronous logging"""
        # Create log entry
        context = self._create_context(**kwargs)
        log_entry = LogEntry(
            level=level,
            message=message,
            parser_name=self.config.parser_name,
            context=context
        )
        
        # Console output
        if self.config.console_enabled and self._should_log_to_console(level):
            self._log_to_console(log_entry)
        
        # File output
        if self.config.file_enabled and self._should_log_to_file(level):
            self._log_to_file(log_entry)
        
        # Bridge output
        if self.config.bridge_enabled and self.bridge_client and self._should_log_to_bridge(level):
            await self._log_to_bridge_async(log_entry)
    
    def _create_context(self, **kwargs) -> LogContext:
        """Create log context from current context and kwargs"""
        context_data = self._context.additional_data.copy()
        
        # Add kwargs as string values
        for key, value in kwargs.items():
            if key not in ['session_id', 'command_id', 'operation', 'url']:
                context_data[key] = str(value)
        
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
        """Check if should log to bridge"""
        level_value = getattr(logging, level.value)
        bridge_level_value = getattr(logging, self.config.bridge_level.value)
        return level_value >= bridge_level_value
    
    def _log_to_console(self, log_entry: LogEntry) -> None:
        """Log to console with rich formatting"""
        if not self.console:
            # Fallback to print if rich not available
            time_str = log_entry.timestamp.strftime('%H:%M:%S')
            print(f"[{time_str}] {log_entry.level.value} - {log_entry.parser_name} - {log_entry.message}")
            return
        
        # Rich console output
        time_str = log_entry.timestamp.strftime('%H:%M:%S')
        
        # Color based on level
        level_colors = {
            LogLevel.DEBUG: "dim white",
            LogLevel.INFO: "bright_blue",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red"
        }
        
        level_color = level_colors.get(log_entry.level, "white")
        
        # Format message
        formatted_message = Text()
        formatted_message.append(f"[{time_str}] ", style="dim")
        formatted_message.append(f"{log_entry.level.value}", style=level_color)
        formatted_message.append(f" - {log_entry.parser_name} - ", style="dim")
        formatted_message.append(log_entry.message, style="white")
        
        # Add context if available
        context_parts = []
        if log_entry.context.additional_data:
            for key, value in log_entry.context.additional_data.items():
                context_parts.append(f"{key}={value}")
        
        if context_parts:
            formatted_message.append(f" ({', '.join(context_parts)})", style="dim")
        
        self.console.print(formatted_message)
    
    def _log_to_file(self, log_entry: LogEntry) -> None:
        """Log to file"""
        if not self.file_logger:
            return
        
        try:
            # Create log message with context
            extra_info = ""
            if log_entry.context.additional_data:
                context_parts = [f"{k}={v}" for k, v in log_entry.context.additional_data.items()]
                extra_info = f" - {', '.join(context_parts)}"
            
            full_message = f"{log_entry.message}{extra_info}"
            
            # Log to file
            log_level = getattr(logging, log_entry.level.value)
            self.file_logger.log(log_level, full_message)
            
        except Exception as e:
            raise FileLoggingError(
                message=f"Failed to write to log file: {e}",
                operation="file_logging",
                details={"log_file": str(self._get_log_file_path())}
            ) from e
    
    async def _log_to_bridge_async(self, log_entry: LogEntry) -> None:
        """Log to bridge asynchronously"""
        if not self.bridge_client:
            return
        
        try:
            # Send to bridge
            await self.bridge_client.send_log(
                level=log_entry.level.value,
                message=log_entry.message,
                session_id=log_entry.context.session_id,
                command_id=log_entry.context.command_id,
                operation=log_entry.context.operation,
                url=log_entry.context.url,
                data=log_entry.context.additional_data if log_entry.context.additional_data else None,
                error_details=log_entry.context.additional_data.get('error') if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL] else None
            )
            
        except Exception as e:
            # Log bridge error to internal logger but don't raise
            self.internal_logger.warning(f"Failed to send log to bridge: {e}")
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _get_log_file_path(self) -> Path:
        """Get path to log file"""
        safe_name = self.config.parser_name.lower().replace(' ', '_')
        return self.config.log_dir / f"{safe_name}.log"
    
    def get_log_file_path(self) -> Path:
        """Get path to log file (public method)"""
        return self._get_log_file_path()
    
    def clear_log_file(self) -> None:
        """Clear log file"""
        log_file = self._get_log_file_path()
        try:
            if log_file.exists():
                log_file.write_text("")
                self.info("Log file cleared")
        except Exception as e:
            raise FileLoggingError(
                message=f"Failed to clear log file: {e}",
                operation="clear_log_file",
                details={"log_file": str(log_file)}
            ) from e
    
    def get_log_stats(self) -> dict[str, str]:
        """Get logging statistics"""
        log_file = self._get_log_file_path()
        
        return {
            "parser_name": self.config.parser_name,
            "log_dir": str(self.config.log_dir),
            "log_file": str(log_file),
            "log_file_exists": str(log_file.exists()),
            "log_file_size": str(log_file.stat().st_size if log_file.exists() else 0),
            "console_enabled": str(self.config.console_enabled),
            "file_enabled": str(self.config.file_enabled),
            "bridge_enabled": str(self.config.bridge_enabled),
            "session_id": self._context.session_id or "",
            "command_id": self._context.command_id or ""
        }
    
    def update_bridge_client(self, bridge_client: Any) -> None:
        """Update bridge client"""
        self.bridge_client = bridge_client
    
    def __repr__(self) -> str:
        return f"<LoggingManager(parser='{self.config.parser_name}', log_dir='{self.config.log_dir}')>"


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_logging_manager(
    parser_name: str,
    log_dir: Optional[Union[str, Path]] = None,
    bridge_client: Optional[Any] = None,
    **kwargs
) -> LoggingManager:
    """
    Get a logging manager instance
    
    Args:
        parser_name: Name of the parser
        log_dir: Directory for log files
        bridge_client: Bridge client for sending logs
        **kwargs: Additional logger configuration
        
    Returns:
        Configured LoggingManager instance
    """
    config_data = {
        "parser_name": parser_name,
        **kwargs
    }
    
    if log_dir is not None:
        config_data["log_dir"] = Path(log_dir)
    
    config = LoggingConfig.model_validate(config_data)
    return LoggingManager(config=config, bridge_client=bridge_client)
