"""
🚀 UnrealOn Driver v4.0 - Modern Parser Framework

Revolutionary parser framework with specialized managers and zero configuration.
Built on unrealon-rpc bridge with full Pydantic v2 compliance.

Key Features:
- 🎯 Zero Configuration: Everything works out of the box
- 🏗️ Manager Architecture: Specialized managers for different concerns
- 🌐 Smart Browser: Intelligent automation with stealth
- 🧹 HTML Cleaning: Optimized for LLM analysis
- 🔌 Bridge Integration: Built on unrealon-rpc bridge
- 📊 Built-in Monitoring: Enterprise observability
- 🛡️ Type Safety: Full Pydantic v2 compliance
"""

from importlib.metadata import version

try:
    __version__ = version("unrealon")
except Exception:
    __version__ = "1.1.1"

from .parser import (
    ParserManager,
    ParserManagerConfig,
    ParserStats,
    get_parser_manager,
    quick_parse,
    ConfigManager,
    ParserConfig,
    ResultManager,
    ParseResult,
    ParseMetrics,
    ErrorManager,
    RetryConfig,
    ErrorInfo,
    LoggingManager,
    LoggingConfig,
    LogLevel,
    HTMLManager,
    HTMLCleaningConfig,
    BrowserManager,
    BrowserConfig,
)
from .exceptions import ParserError, BrowserError

__all__ = [
    # Main Parser Manager
    "ParserManager",
    "ParserManagerConfig",
    "ParserStats",
    "get_parser_manager",
    "quick_parse",
    # Individual Managers
    "ConfigManager",
    "ParserConfig",
    "ResultManager",
    "ParseResult",
    "ParseMetrics",
    "ErrorManager",
    "RetryConfig",
    "ErrorInfo",
    "LoggingManager",
    "LoggingConfig",
    "LogLevel",
    "HTMLManager",
    "HTMLCleaningConfig",
    "BrowserManager",
    "BrowserConfig",
    # Exceptions
    "ParserError",
    "BrowserError",
    # Version
    "__version__",
]
# Convenience aliases for backward compatibility
Parser = ParserManager
DriverLogger = LoggingManager
get_driver_logger = LoggingManager
