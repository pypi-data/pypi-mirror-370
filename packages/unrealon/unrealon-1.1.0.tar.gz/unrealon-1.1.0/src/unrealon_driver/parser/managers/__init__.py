"""
Parser Managers - Specialized management components

All managers follow strict Pydantic v2 compliance and CRITICAL_REQUIREMENTS.md
"""

from .config import ConfigManager, ParserConfig
from .result import ResultManager, ParseResult, ParseMetrics, OperationStatus
from .error import ErrorManager, RetryConfig, ErrorInfo, ErrorSeverity
from .logging import LoggingManager, LoggingConfig, LogLevel, LogContext
from .html import HTMLManager, HTMLCleaningConfig, HTMLCleaningStats
from .browser import BrowserManager, BrowserConfig, BrowserStats

__all__ = [
    # Config Manager
    "ConfigManager",
    "ParserConfig",
    
    # Result Manager
    "ResultManager",
    "ParseResult",
    "ParseMetrics",
    "OperationStatus",
    
    # Error Manager
    "ErrorManager",
    "RetryConfig",
    "ErrorInfo",
    "ErrorSeverity",
    
    # Logging Manager
    "LoggingManager",
    "LoggingConfig",
    "LogLevel",
    "LogContext",
    
    # HTML Manager
    "HTMLManager",
    "HTMLCleaningConfig",
    "HTMLCleaningStats",
    
    # Browser Manager
    "BrowserManager",
    "BrowserConfig",
    "BrowserStats"
]
