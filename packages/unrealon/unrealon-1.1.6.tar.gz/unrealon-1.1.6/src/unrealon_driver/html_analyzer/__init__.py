"""
HTML Analyzer module for unrealon_driver.

Provides intelligent HTML processing, cleaning, and analysis with WebSocket communication.
"""

from .manager import HTMLAnalyzer, create_html_analyzer
from .config import HTMLAnalyzerConfig, HTMLCleaningConfig
from .cleaner import HTMLCleaner, HTMLCleaningStats
from .websocket_analyzer import WebSocketHTMLAnalyzer
from .models import HTMLAnalysisResult, HTMLParseResult, HTMLAnalyzerStats, HTMLAnalysisRequest, HTMLParseRequest, HTMLAnalyzerError, HTMLCleaningError, HTMLAnalysisError, WebSocketAnalysisError

__all__ = [
    "HTMLAnalyzer",
    "HTMLAnalyzerConfig",
    "HTMLCleaningConfig",
    "HTMLCleaningStats",
    "HTMLCleaner",
    "WebSocketHTMLAnalyzer",
    "create_html_analyzer",
    # Models
    "HTMLAnalysisResult",
    "HTMLParseResult",
    "HTMLAnalyzerStats",
    "HTMLAnalysisRequest",
    "HTMLParseRequest",
    # Exceptions
    "HTMLAnalyzerError",
    "HTMLCleaningError",
    "HTMLAnalysisError",
    "WebSocketAnalysisError",
]
