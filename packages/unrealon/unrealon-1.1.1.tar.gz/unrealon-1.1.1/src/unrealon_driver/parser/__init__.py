"""
Parser management system with specialized managers

Strict Pydantic v2 compliance and type safety
"""

from .parser_manager import ParserManager, ParserManagerConfig, ParserStats, get_parser_manager, quick_parse
from .daemon_manager import DaemonManager, DaemonStatus
from .cli_manager import CLIManager
from .managers import (
    ConfigManager, ParserConfig,
    ResultManager, ParseResult, ParseMetrics, OperationStatus,
    ErrorManager, RetryConfig, ErrorInfo, ErrorSeverity,
    LoggingManager, LoggingConfig, LogLevel, LogContext,
    HTMLManager, HTMLCleaningConfig, HTMLCleaningStats,
    BrowserManager, BrowserConfig, BrowserStats
)

__all__ = [
    # Main Parser Manager
    "ParserManager",
    "ParserManagerConfig", 
    "ParserStats",
    "get_parser_manager",
    "quick_parse",
    
    # Daemon Manager
    "DaemonManager",
    "DaemonStatus",
    
    # CLI Manager
    "CLIManager",
    
    # Individual Managers
    "ConfigManager",
    "ParserConfig",
    "ResultManager",
    "ParseResult", 
    "ParseMetrics",
    "OperationStatus",
    "ErrorManager",
    "RetryConfig",
    "ErrorInfo",
    "ErrorSeverity",
    "LoggingManager",
    "LoggingConfig",
    "LogLevel",
    "LogContext",
    "HTMLManager",
    "HTMLCleaningConfig",
    "HTMLCleaningStats",
    "BrowserManager",
    "BrowserConfig",
    "BrowserStats"
]
