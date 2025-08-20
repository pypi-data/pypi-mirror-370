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

from unrealon import VersionInfo

__version__ = VersionInfo().version


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


)
from .exceptions import ParserError, BrowserError

__all__ = [
    "__version__",
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


    # Exceptions
    "ParserError",
    "BrowserError",
    # Version
    "__version__",
]
# Convenience aliases for backward compatibility
Parser = ParserManager
