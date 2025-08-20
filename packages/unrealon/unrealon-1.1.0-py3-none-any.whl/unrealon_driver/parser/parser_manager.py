"""
Parser Manager - Unified parser management system with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- Custom exception hierarchy
- No try blocks in imports
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Union, Any
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, field_validator

from unrealon_bridge import ParserBridgeClient
from unrealon_rpc.logging import get_logger

from .managers import (
    ConfigManager, ParserConfig,
    ResultManager, ParseResult, ParseMetrics,
    ErrorManager, RetryConfig, ErrorInfo,
    LoggingManager, LoggingConfig, LogLevel,
    HTMLManager, HTMLCleaningConfig,
    BrowserManager, BrowserConfig
)


class ParserManagerConfig(BaseModel):
    """Complete parser manager configuration"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Core configuration
    parser_config: ParserConfig = Field(
        default_factory=ParserConfig,
        description="Core parser configuration"
    )
    
    # Manager configurations
    logging_config: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration"
    )
    html_config: HTMLCleaningConfig = Field(
        default_factory=HTMLCleaningConfig,
        description="HTML cleaning configuration"
    )
    browser_config: BrowserConfig = Field(
        default_factory=BrowserConfig,
        description="Browser configuration"
    )
    retry_config: RetryConfig = Field(
        default_factory=RetryConfig,
        description="Retry configuration"
    )
    
    # Bridge settings
    bridge_enabled: bool = Field(
        default=True,
        description="Enable bridge connection"
    )
    auto_register: bool = Field(
        default=True,
        description="Auto-register parser with bridge"
    )
    
    def model_post_init(self, __context) -> None:
        """Sync configurations across managers"""
        # Sync parser name across all configs
        parser_name = self.parser_config.parser_name
        if hasattr(self.logging_config, 'parser_name'):
            self.logging_config.parser_name = parser_name
        
        # Sync system directories
        system_dir = self.parser_config.system_dir
        if system_dir:
            self.logging_config.log_dir = system_dir / "logs"
            self.browser_config.screenshots_dir = system_dir / "screenshots"
            self.browser_config.cookies_file = system_dir / "cookies.json"


class ParserStats(BaseModel):
    """Comprehensive parser statistics"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
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
        self.internal_logger = get_logger()
        
        # Initialize managers
        self.config_manager = ConfigManager(self.config.parser_config)
        self.result_manager = ResultManager(self.config.parser_config.parser_id)
        self.error_manager = ErrorManager(self.internal_logger)
        self.logging_manager = LoggingManager(self.config.logging_config)
        self.html_manager = HTMLManager(self.config.html_config)
        self.browser_manager = BrowserManager(self.config.browser_config)
        
        # Bridge client
        self.bridge_client: Optional[ParserBridgeClient] = None
        
        # State
        self._is_initialized = False
        self._session_id: Optional[str] = None
        self._stats = ParserStats(
            parser_id=self.config.parser_config.parser_id,
            parser_name=self.config.parser_config.parser_name
        )
        
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
            self.logging_manager.info("🚀 Initializing parser manager...")
            
            # Initialize bridge client
            if self.config.bridge_enabled:
                await self._initialize_bridge()
            
            # Initialize browser
            await self.browser_manager.initialize()
            
            # Update logging manager with bridge client
            if self.bridge_client:
                self.logging_manager.update_bridge_client(self.bridge_client)
            
            # Register parser if enabled
            if self.config.auto_register and self.bridge_client:
                await self._register_parser()
            
            self._is_initialized = True
            self.logging_manager.info("✅ Parser manager initialized successfully")
            
        except Exception as e:
            self.error_manager.record_error(e, "initialization")
            raise InitializationError(
                message=f"Failed to initialize parser manager: {e}",
                operation="initialization"
            ) from e
    
    async def cleanup(self) -> None:
        """Clean up all resources"""
        self.logging_manager.info("🧹 Cleaning up parser manager...")
        
        cleanup_errors = []
        
        # End session if active
        if self._session_id and self.bridge_client:
            try:
                await self.bridge_client.end_session()
            except Exception as e:
                cleanup_errors.append(f"end_session: {e}")
        
        # Cleanup browser
        try:
            await self.browser_manager.cleanup()
        except Exception as e:
            cleanup_errors.append(f"browser_cleanup: {e}")
        
        # Disconnect bridge
        if self.bridge_client:
            try:
                await self.bridge_client.disconnect()
            except Exception as e:
                cleanup_errors.append(f"bridge_disconnect: {e}")
        
        # Update final stats
        self._update_session_stats()
        
        # Log cleanup errors but don't raise
        if cleanup_errors:
            self.logging_manager.warning(f"Cleanup errors: {'; '.join(cleanup_errors)}")
        
        self.logging_manager.info("✅ Parser manager cleanup completed")
    
    # ==========================================
    # CORE PARSING METHODS
    # ==========================================
    
    async def get_html(self, url: str) -> str:
        """Get HTML content from URL with error handling"""
        if not self._is_initialized:
            await self.initialize()
        
        @self.error_manager.with_retry("get_html", self.config.retry_config)
        async def _get_html_with_retry():
            self.logging_manager.url_access(url, "fetching")
            html = await self.browser_manager.get_html(url)
            self._stats.pages_processed += 1
            return html
        
        try:
            return await _get_html_with_retry()
        except Exception as e:
            self._stats.total_errors += 1
            raise OperationError(
                message=f"Failed to get HTML from {url}: {e}",
                operation="get_html",
                details={"url": url}
            ) from e
    
    async def clean_html(self, html: str, **kwargs) -> str:
        """Clean HTML content for LLM analysis"""
        try:
            self.logging_manager.info(f"🧹 Cleaning HTML: {len(html)} characters")
            
            cleaned_html = await self.html_manager.clean_html(html, **kwargs)
            
            # Update stats
            self._stats.html_cleaned_count += 1
            stats = self.html_manager.get_cleaning_stats(html, cleaned_html)
            self._stats.total_html_reduction += stats.size_reduction_percent
            
            self.logging_manager.info(
                f"✅ HTML cleaned: {len(html)} → {len(cleaned_html)} chars "
                f"({stats.size_reduction_percent:.1f}% reduction)"
            )
            
            return cleaned_html
            
        except Exception as e:
            self._stats.total_errors += 1
            raise OperationError(
                message=f"Failed to clean HTML: {e}",
                operation="clean_html"
            ) from e
    
    async def analyze_html(
        self,
        html: str,
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, str]:
        """Analyze HTML content via bridge"""
        if not self.bridge_client:
            raise OperationError(
                message="Bridge client not available for HTML analysis",
                operation="analyze_html"
            )
        
        try:
            self.logging_manager.info("🤖 Analyzing HTML with LLM...")
            
            result = await self.bridge_client.parse_html(
                html_content=html,
                instructions=instructions,
                parse_type="general",
                timeout=kwargs.get("timeout", 60),
                metadata=kwargs.get("metadata", {})
            )
            
            return {
                "success": str(result.success),
                "parsed_data": str(result.parsed_data),
                "markdown": result.markdown or "",
                "error_message": result.error_message or ""
            }
            
        except Exception as e:
            self._stats.total_errors += 1
            raise OperationError(
                message=f"Failed to analyze HTML: {e}",
                operation="analyze_html"
            ) from e
    
    async def parse_url(
        self,
        url: str,
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, str]:
        """Complete parsing workflow: fetch → clean → analyze"""
        operation = self.result_manager.start_operation()
        
        try:
            self.logging_manager.start_operation("parse_url")
            
            # Fetch HTML
            html = await self.get_html(url)
            
            # Clean HTML
            cleaned_html = await self.clean_html(html, **kwargs)
            
            # Analyze HTML
            analysis_result = await self.analyze_html(cleaned_html, instructions, **kwargs)
            
            # Complete operation
            self.result_manager.complete_operation(
                data=[],  # Analysis result is returned directly
                source_urls=[url],
                success=analysis_result.get("success", "false") == "true"
            )
            
            self._stats.operations_completed += 1
            self.logging_manager.end_operation("parse_url", operation.duration_seconds)
            
            return analysis_result
            
        except Exception as e:
            self.result_manager.complete_operation(
                data=[],
                source_urls=[url],
                success=False,
                error_message=str(e)
            )
            
            self._stats.operations_failed += 1
            self.logging_manager.fail_operation("parse_url", str(e))
            raise
    
    # ==========================================
    # SESSION MANAGEMENT
    # ==========================================
    
    async def start_session(self, session_type: str = "parsing") -> str:
        """Start a new parsing session"""
        if not self.bridge_client:
            raise OperationError(
                message="Bridge client not available for session management",
                operation="start_session"
            )
        
        try:
            session_id = await self.bridge_client.start_session(
                session_type=session_type,
                metadata={
                    "parser_name": self.config.parser_config.parser_name,
                    "parser_type": self.config.parser_config.parser_type
                }
            )
            
            self._session_id = session_id
            self._stats.session_id = session_id
            self.logging_manager.set_session(session_id)
            
            self.logging_manager.info(f"📋 Session started: {session_id}")
            return session_id
            
        except Exception as e:
            raise OperationError(
                message=f"Failed to start session: {e}",
                operation="start_session"
            ) from e
    
    async def end_session(self) -> None:
        """End current parsing session"""
        if not self._session_id or not self.bridge_client:
            return
        
        try:
            await self.bridge_client.end_session()
            self.logging_manager.info(f"📋 Session ended: {self._session_id}")
            self._session_id = None
            self._stats.session_id = None
            
        except Exception as e:
            self.logging_manager.warning(f"Failed to end session: {e}")
    
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
            "browser_manager": self.browser_manager.get_stats().model_dump(mode='json'),
            "logging_manager": self.logging_manager.get_log_stats()
        }
    
    async def health_check(self) -> dict[str, str]:
        """Comprehensive health check"""
        health = {
            "status": "healthy",
            "parser_id": self.config.parser_config.parser_id,
            "parser_name": self.config.parser_config.parser_name,
            "initialized": str(self._is_initialized),
            "session_active": str(self._session_id is not None)
        }
        
        # Check browser health
        try:
            browser_health = await self.browser_manager.health_check()
            health["browser_status"] = browser_health.get("status", "unknown")
        except Exception as e:
            health["browser_status"] = f"error: {e}"
        
        # Check bridge health
        if self.bridge_client:
            health["bridge_connected"] = "true"
        else:
            health["bridge_connected"] = "false"
        
        return health
    
    # ==========================================
    # INTERNAL METHODS
    # ==========================================
    
    async def _initialize_bridge(self) -> None:
        """Initialize bridge client"""
        self.bridge_client = ParserBridgeClient(
            websocket_url=self.config.parser_config.websocket_url,
            parser_type=self.config.parser_config.parser_type,
            api_key=self.config.parser_config.api_key
        )
        
        await self.bridge_client.bridge_client.connect()
        self._stats.bridge_connected = True
        self.logging_manager.info("🔗 Bridge client connected")
    
    async def _register_parser(self) -> None:
        """Register parser with bridge"""
        if not self.bridge_client:
            return
        
        parser_info = await self.bridge_client.register_parser(
            metadata={
                "driver_version": "4.0.0",
                "capabilities": "scraping,html_cleaning,llm_integration",
                "managers": "config,result,error,logging,html,browser"
            }
        )
        
        # Update parser ID
        self.config.parser_config.parser_id = parser_info.parser_id
        self._stats.parser_id = parser_info.parser_id
        
        self.logging_manager.info(f"📝 Parser registered: {parser_info.parser_id}")
    
    def _setup_retry_configs(self) -> None:
        """Setup retry configurations for different operations"""
        # Navigation retry config
        nav_config = RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            retry_on_exceptions=["NavigationError", "TimeoutError", "ConnectionError"]
        )
        self.error_manager.register_retry_config("get_html", nav_config)
        
        # Bridge communication retry config
        bridge_config = RetryConfig(
            max_attempts=2,
            base_delay=1.0,
            retry_on_exceptions=["ConnectionError", "TimeoutError"]
        )
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
    
    def __repr__(self) -> str:
        return f"<ParserManager(id='{self.config.parser_config.parser_id}', name='{self.config.parser_config.parser_name}')>"


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_parser_manager(
    parser_name: str,
    parser_type: str = "generic",
    **kwargs
) -> ParserManager:
    """
    Get a parser manager instance with minimal configuration
    
    Args:
        parser_name: Name of the parser
        parser_type: Type of parser (generic, ecommerce, news, etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Configured ParserManager instance
    """
    parser_config = ParserConfig(
        parser_name=parser_name,
        parser_type=parser_type,
        **{k: v for k, v in kwargs.items() if k in ParserConfig.model_fields}
    )
    
    # Create logging config with parser name
    logging_config = LoggingConfig(parser_name=parser_name)
    
    config = ParserManagerConfig(
        parser_config=parser_config,
        logging_config=logging_config,
        **{k: v for k, v in kwargs.items() if k in ParserManagerConfig.model_fields and k not in ['parser_config', 'logging_config']}
    )
    
    return ParserManager(config)


async def quick_parse(
    url: str,
    parser_name: str = "QuickParser",
    instructions: Optional[str] = None,
    **kwargs
) -> dict[str, str]:
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
