"""
Parser Manager - Unified parser management system with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- Custom exception hierarchy
- No try blocks in imports
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from .managers import ConfigManager, ParserConfig, ResultManager, ErrorManager, RetryConfig

# from unrealon_browser import BrowserManager, BrowserConfig  # Temporary comment to avoid circular import

# Import UnifiedLogger and HTML Analyzer
from unrealon_driver.smart_logging import create_unified_logger, LogLevel
from unrealon_driver.html_analyzer import create_html_analyzer, HTMLCleaningConfig, HTMLParseResult
from unrealon_driver.websocket import websocket_manager, WebSocketConfig
from unrealon_browser.core import BrowserManager
from unrealon_browser.dto.models.config import BrowserConfig


class ParserManagerConfig(BaseModel):
    """Complete parser manager configuration"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Core configuration
    parser_config: ParserConfig = Field(default_factory=ParserConfig, description="Core parser configuration")

    # Logging configuration (simplified)
    console_enabled: bool = Field(default=True, description="Enable console logging")
    file_enabled: bool = Field(default=True, description="Enable file logging")
    console_level: LogLevel = Field(default=LogLevel.INFO, description="Console log level")
    file_level: LogLevel = Field(default=LogLevel.DEBUG, description="File log level")
    html_config: HTMLCleaningConfig = Field(default_factory=HTMLCleaningConfig, description="HTML cleaning configuration")
    retry_config: RetryConfig = Field(default_factory=RetryConfig, description="Retry configuration")

    # Bridge settings
    bridge_enabled: bool = Field(default=True, description="Enable bridge connection")
    auto_register: bool = Field(default=True, description="Auto-register parser with bridge")

    # SmartLogger settings
    bridge_logs_url: Optional[str] = Field(default=None, description="Bridge logs WebSocket URL (ws://localhost:8001/logs)")
    log_batch_interval: float = Field(default=5.0, description="Log batch interval in seconds")
    daemon_mode: Optional[bool] = Field(default=None, description="Daemon mode for logging (None = auto-detect)")


class ParserStats(BaseModel):
    """Comprehensive parser statistics"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    parser_id: str = Field(...)
    parser_name: str = Field(...)
    session_id: Optional[str] = Field(default=None)

    # Timing
    session_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_duration: float = Field(default=0.0, ge=0.0)

    # Operations
    operations_completed: int = Field(default=0, ge=0)
    operations_failed: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)

    # Content processing
    pages_processed: int = Field(default=0, ge=0)
    html_cleaned_count: int = Field(default=0, ge=0)
    total_html_reduction: float = Field(default=0.0, ge=0.0)

    # Errors
    total_errors: int = Field(default=0, ge=0)
    retries_attempted: int = Field(default=0, ge=0)

    # Bridge
    bridge_connected: bool = Field(default=False)
    bridge_messages_sent: int = Field(default=0, ge=0)


class ParserManagerError(Exception):
    """Base exception for parser manager"""

    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class InitializationError(ParserManagerError):
    """Raised when parser manager initialization fails"""

    pass


class OperationError(ParserManagerError):
    """Raised when parser operation fails"""

    pass


class ParserManager:
    """
    🚀 Parser Manager - Unified parser management system

    Features:
    - Unified Configuration: Single config for all managers
    - Automatic Lifecycle: Handles initialization, execution, cleanup
    - Error Recovery: Smart retry logic with exponential backoff
    - Performance Monitoring: Comprehensive statistics and metrics
    - Bridge Integration: Seamless communication with Django
    - Type Safety: Full Pydantic v2 compliance

    Usage:
        config = ParserManagerConfig(
            parser_config=ParserConfig(parser_name="MyParser"),
            bridge_enabled=True
        )

        async with ParserManager(config) as parser:
            # Navigate and extract
            html = await parser.get_html("https://example.com")
            cleaned_html = await parser.clean_html(html)
            result = await parser.analyze_html(cleaned_html)

            # Results are automatically tracked
            stats = parser.get_stats()
    """

    def __init__(self, config: ParserManagerConfig):
        self.config = config

        # Initialize managers
        self.config_manager = ConfigManager(self.config.parser_config)
        self.result_manager = ResultManager(self.config.parser_config.parser_id)
        self.error_manager = ErrorManager()
        # Initialize HTML Analyzer (WebSocket URL auto-detected)
        self.html_analyzer = create_html_analyzer(parser_id=self.config.parser_config.parser_id, api_key=self.config.parser_config.api_key, cleaning_config=self.config.html_config)
        # Create default browser config
        browser_config = BrowserConfig(parser_name=self.config.parser_config.parser_name)
        self.browser_manager = BrowserManager(browser_config, parser_id=self.config.parser_config.parser_id)

        # Initialize WebSocket connection config
        if self.config.bridge_logs_url:
            self._websocket_config = WebSocketConfig(url=self.config.bridge_logs_url, api_key=self.config.parser_config.api_key, parser_id=self.config.parser_config.parser_id)
        else:
            self._websocket_config = None

        # Initialize UnifiedLogger
        log_file = None
        if self.config.parser_config.system_dir:
            log_file = self.config.parser_config.system_dir / "logs" / f"{self.config.parser_config.parser_name}.log"

        self.logger = create_unified_logger(
            parser_id=self.config.parser_config.parser_id,
            parser_name=self.config.parser_config.parser_name,
            bridge_logs_url=self.config.bridge_logs_url,
            log_file=log_file,
            console_enabled=self.config.console_enabled,
            file_enabled=self.config.file_enabled,
            console_level=self.config.console_level,
            file_level=self.config.file_level,
            batch_interval=self.config.log_batch_interval,
            daemon_mode=self.config.daemon_mode,
        )

        # State
        self._is_initialized = False
        self._session_id: Optional[str] = None
        self._stats = ParserStats(parser_id=self.config.parser_config.parser_id, parser_name=self.config.parser_config.parser_name)

        # Register retry configurations
        self._setup_retry_configs()

    # ==========================================
    # LIFECYCLE MANAGEMENT
    # ==========================================

    async def initialize(self) -> None:
        """Initialize all managers and establish connections"""
        if self._is_initialized:
            return

        try:
            self.logger.info("🚀 Initializing parser manager...")

            # Initialize WebSocket connection
            if self._websocket_config:
                await websocket_manager.initialize(self._websocket_config)
                if websocket_manager.connected:
                    self.logger.info("🔌 WebSocket connected")
                else:
                    self.logger.warning("🔌 WebSocket connection failed")

            # Initialize browser
            await self.browser_manager.initialize_async()

            self._is_initialized = True
            self.logger.info("✅ Parser manager initialized successfully")

        except Exception as e:
            self.error_manager.record_error(e, "initialization")
            raise InitializationError(message=f"Failed to initialize parser manager: {e}", operation="initialization") from e

    async def cleanup(self) -> None:
        """Clean up all resources"""
        self.logger.info("🧹 Cleaning up parser manager...")

        cleanup_errors = []

        # End session if active
        if self._session_id:
            await self.end_session()

        # Cleanup browser
        try:
            await self.browser_manager.close_async()
        except Exception as e:
            cleanup_errors.append(f"browser_cleanup: {e}")

        # Disconnect WebSocket
        try:
            await websocket_manager.disconnect()
        except Exception as e:
            cleanup_errors.append(f"websocket_disconnect: {e}")

        # Update final stats
        self._update_session_stats()

        # Cleanup UnifiedLogger
        try:
            await self.logger.close()
        except Exception as e:
            cleanup_errors.append(f"logger_cleanup: {e}")

        # Log cleanup errors but don't raise
        if cleanup_errors:
            self.logger.warning(f"Cleanup errors: {'; '.join(cleanup_errors)}")

        self.logger.info("✅ Parser manager cleanup completed")

    # ==========================================
    # CORE PARSING METHODS
    # ==========================================

    async def get_html(self, url: str) -> str:
        """Get HTML content from URL with error handling"""
        if not self._is_initialized:
            await self.initialize()

        @self.error_manager.with_retry("get_html", self.config.retry_config)
        async def _get_html_with_retry():
            self.logger.url_access(url, "fetching")
            html = await self.browser_manager.get_html(url)
            self._stats.pages_processed += 1
            return html

        try:
            return await _get_html_with_retry()
        except Exception as e:
            self._stats.total_errors += 1
            raise OperationError(message=f"Failed to get HTML from {url}: {e}", operation="get_html", details={"url": url}) from e

    async def parse_url(self, url: str, instructions: Optional[str] = None, **kwargs) -> HTMLParseResult:
        """Complete parsing workflow: fetch → clean → analyze via HTML Analyzer"""
        operation = self.result_manager.start_operation()

        try:
            self.logger.start_operation("parse_url")

            # Fetch HTML
            html = await self.get_html(url)

            # Delegate complete HTML processing to HTML Analyzer
            analysis_result = await self.html_analyzer.parse_html(html=html, url=url, instructions=instructions, session_id=self._session_id, **kwargs)

            # Update stats from HTML Analyzer
            html_stats = self.html_analyzer.get_stats()
            self._stats.html_cleaned_count += html_stats.cleaned_count
            self._stats.total_html_reduction += html_stats.total_reduction

            # Complete operation
            success = analysis_result.success == "true"
            self.result_manager.complete_operation(data=[], source_urls=[url], success=success)

            if success:
                self._stats.operations_completed += 1
            else:
                self._stats.operations_failed += 1

            self.logger.end_operation("parse_url", operation.duration_seconds)

            return analysis_result

        except Exception as e:
            self.result_manager.complete_operation(data=[], source_urls=[url], success=False, error_message=str(e))

            self._stats.operations_failed += 1
            self.logger.error(f"❌ Failed parse_url: {str(e)}")
            raise

    # ==========================================
    # SESSION MANAGEMENT (Simplified - Local Only)
    # ==========================================

    async def start_session(self, session_type: str = "parsing") -> str:
        """Start a new parsing session (local only)"""
        import uuid

        session_id = f"{session_type}_{uuid.uuid4().hex[:8]}"
        self._session_id = session_id
        self._stats.session_id = session_id
        self.logger.set_session(session_id)

        self.logger.info(f"📋 Local session started: {session_id}")
        return session_id

    async def end_session(self) -> None:
        """End current parsing session"""
        if not self._session_id:
            return

        self.logger.info(f"📋 Local session ended: {self._session_id}")
        self._session_id = None
        self._stats.session_id = None

    # ==========================================
    # STATISTICS AND MONITORING
    # ==========================================

    def get_stats(self) -> ParserStats:
        """Get comprehensive parser statistics"""
        self._update_session_stats()
        return ParserStats.model_validate(self._stats.model_dump())

    def get_manager_stats(self) -> dict[str, dict[str, str]]:
        """Get statistics from all managers"""
        return {
            "result_manager": self.result_manager.get_stats(),
            "error_manager": self.error_manager.get_error_stats(),
            "browser_manager": self.browser_manager.get_stats().model_dump(mode="json"),
            # Logging stats removed - using UnifiedLogger now
        }

    async def health_check(self) -> dict[str, str]:
        """Comprehensive health check"""
        health = {"status": "healthy", "parser_id": self.config.parser_config.parser_id, "parser_name": self.config.parser_config.parser_name, "initialized": str(self._is_initialized), "session_active": str(self._session_id is not None)}

        # Check browser health
        try:
            browser_health = await self.browser_manager.health_check()
            health["browser_status"] = browser_health.get("status", "unknown")
        except Exception as e:
            health["browser_status"] = f"error: {e}"

        # Check WebSocket connection health
        health["websocket_connected"] = str(websocket_manager.connected)

        return health

    # ==========================================
    # INTERNAL METHODS
    # ==========================================

    def _setup_retry_configs(self) -> None:
        """Setup retry configurations for different operations"""
        # Navigation retry config
        nav_config = RetryConfig(max_attempts=3, base_delay=2.0, retry_on_exceptions=["NavigationError", "TimeoutError", "ConnectionError"])
        self.error_manager.register_retry_config("get_html", nav_config)

        # Bridge communication retry config
        bridge_config = RetryConfig(max_attempts=2, base_delay=1.0, retry_on_exceptions=["ConnectionError", "TimeoutError"])
        self.error_manager.register_retry_config("analyze_html", bridge_config)

    def _update_session_stats(self) -> None:
        """Update session statistics"""
        self._stats.session_duration = (datetime.now(timezone.utc) - self._stats.session_start).total_seconds()

        total_operations = self._stats.operations_completed + self._stats.operations_failed
        if total_operations > 0:
            self._stats.success_rate = (self._stats.operations_completed / total_operations) * 100.0

    # ==========================================
    # CONTEXT MANAGER SUPPORT
    # ==========================================

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        return False

    # ==========================================
    # LOGGING CONVENIENCE
    # ==========================================

    def set_session_id(self, session_id: str):
        """Set session ID for both internal tracking and logger"""
        self._session_id = session_id
        self.logger.set_session(session_id)

    async def flush_logs(self):
        """Force flush all accumulated logs"""
        await self.logger.flush()

    def __repr__(self) -> str:
        return f"<ParserManager(id='{self.config.parser_config.parser_id}', name='{self.config.parser_config.parser_name}')>"


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================


def get_parser_manager(parser_name: str, parser_type: str = "generic", **kwargs) -> ParserManager:
    """
    Get a parser manager instance with minimal configuration

    Args:
        parser_name: Name of the parser
        parser_type: Type of parser (generic, ecommerce, news, etc.)
        **kwargs: Additional configuration options

    Returns:
        Configured ParserManager instance
    """
    parser_config = ParserConfig(parser_name=parser_name, parser_type=parser_type, **{k: v for k, v in kwargs.items() if k in ParserConfig.model_fields})

    config = ParserManagerConfig(parser_config=parser_config, **{k: v for k, v in kwargs.items() if k in ParserManagerConfig.model_fields and k not in ["parser_config"]})

    return ParserManager(config)


async def quick_parse(url: str, parser_name: str = "QuickParser", instructions: Optional[str] = None, **kwargs) -> HTMLParseResult:
    """
    Quick parsing convenience function

    Args:
        url: URL to parse
        parser_name: Name for the parser
        instructions: Optional parsing instructions
        **kwargs: Additional configuration

    Returns:
        Parsing result
    """
    async with get_parser_manager(parser_name, **kwargs) as parser:
        return await parser.parse_url(url, instructions, **kwargs)
