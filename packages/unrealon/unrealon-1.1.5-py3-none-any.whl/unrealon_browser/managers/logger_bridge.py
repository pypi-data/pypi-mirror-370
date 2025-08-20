"""
Logger Bridge - Integration bridge between unrealon_browser and unrealon_driver loggers
Layer 2.5: Logging Integration - Connects independent browser module with driver enterprise loggers
"""

from typing import Optional, Any, Dict
from datetime import datetime, timezone
import uuid

# Browser DTOs
from unrealon_browser.dto import (
    BrowserSessionStatus,
    BrowserSession,
    CaptchaDetectionResult,
)

# Smart logging with fallback to avoid circular imports
import logging

# Try to import smart logging, fallback to standard logging
try:
    from unrealon_driver.smart_logging import create_unified_logger
    from unrealon_driver.smart_logging.unified_logger import UnifiedLoggerConfig
    SMART_LOGGING_AVAILABLE = True
except ImportError:
    SMART_LOGGING_AVAILABLE = False


class BrowserLoggerBridge:
    """
    Bridge between unrealon_browser and unrealon_driver loggers

    Provides unified logging interface for browser operations using
    the driver's LoggingManager for consistent logging across the ecosystem.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        parser_id: Optional[str] = None,
        bridge_logs_url: Optional[str] = None,
        enable_console: bool = True,
    ):
        """Initialize logger bridge"""
        self.session_id = session_id or str(uuid.uuid4())
        self.parser_id = parser_id or f"browser_{uuid.uuid4().hex[:8]}"

        # Initialize logger based on availability
        if SMART_LOGGING_AVAILABLE:
            # Use smart logging if available
            self.logger = create_unified_logger(
                parser_id=self.parser_id,
                parser_name="unrealon_browser",
                bridge_logs_url=bridge_logs_url,
                console_enabled=enable_console,
            )
            # Set session context
            self.logger.set_session(self.session_id)
            self._use_smart_logging = True
        else:
            # Fallback to standard Python logging
            self.logger = logging.getLogger(f"unrealon_browser.{self.parser_id}")
            self.logger.setLevel(logging.DEBUG)
            
            # Add console handler if needed
            if enable_console and not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            
            self._use_smart_logging = False

        # Statistics
        self._events_logged = 0
        self._browser_events = {
            "browser_initialized": 0,
            "navigation_success": 0,
            "navigation_failed": 0,
            "stealth_applied": 0,
            "captcha_detected": 0,
            "captcha_solved": 0,
            "profile_created": 0,
            "cookies_saved": 0,
        }

        self._log_debug(f"BrowserLoggerBridge initialized for session {self.session_id}")

    def _log(self, level: str, message: str, **context: Any) -> None:
        """Universal logging method"""
        self._events_logged += 1
        
        if self._use_smart_logging:
            # Use smart logging with context
            getattr(self.logger, level)(message, **context)
        else:
            # Use standard logging with formatted context
            context_str = f" {context}" if context else ""
            getattr(self.logger, level)(f"{message}{context_str}")

    def _log_debug(self, message: str, **context: Any) -> None:
        """Debug level logging"""
        self._log("debug", message, **context)
        
    def log_debug(self, message: str, **context: Any) -> None:
        """Public debug level logging"""
        self._log_debug(message, **context)

    def _log_info(self, message: str, **context: Any) -> None:
        """Info level logging"""
        self._log("info", message, **context)
        
    def log_info(self, message: str, **context: Any) -> None:
        """Public info level logging"""
        self._log_info(message, **context)

    def _log_warning(self, message: str, **context: Any) -> None:
        """Warning level logging"""
        self._log("warning", message, **context)
        
    def log_warning(self, message: str, **context: Any) -> None:
        """Public warning level logging"""
        self._log_warning(message, **context)

    def _log_error(self, message: str, **context: Any) -> None:
        """Error level logging"""
        self._log("error", message, **context)
        
    def log_error(self, message: str, **context: Any) -> None:
        """Public error level logging"""
        self._log_error(message, **context)

    # Browser-specific logging methods
    def log_browser_initialized(self, metadata: BrowserSession) -> None:
        """Log browser initialization"""
        self._browser_events["browser_initialized"] += 1
        self._log_info(
            f"Browser session initialized: {metadata.session_id}",
            session_id=metadata.session_id,
            parser_name=metadata.parser_name,
            browser_type=metadata.browser_type or "unknown",
            stealth_level="unknown",
            proxy_host=getattr(metadata.proxy, "host", None) if metadata.proxy else None,
            proxy_port=getattr(metadata.proxy, "port", None) if metadata.proxy else None,
        )

    def log_navigation_success(self, url: str, title: str, duration_ms: float) -> None:
        """Log successful navigation"""
        self._browser_events["navigation_success"] += 1
        self._log_info(
            f"Navigation successful: {title}",
            url=url,
            title=title,
            duration_ms=duration_ms,
            navigation_type="browser_navigation",
        )

    def log_navigation_failed(self, url: str, error: str, duration_ms: float) -> None:
        """Log failed navigation"""
        self._browser_events["navigation_failed"] += 1
        self._log_error(
            f"Navigation failed: {url}",
            url=url,
            error_message=error,
            duration_ms=duration_ms,
            navigation_type="browser_navigation",
        )

    def log_stealth_applied(self, stealth_level: str, success: bool) -> None:
        """Log stealth application - 🔥 STEALTH ALWAYS ON!"""
        self._browser_events["stealth_applied"] += 1

        if success:
            self._log_info(
                f"Stealth measures applied: {stealth_level}",
                stealth_level=stealth_level,
                stealth_success=True,
            )
        else:
            self._log_warning(
                f"Stealth application failed: {stealth_level}",
                stealth_level=stealth_level,
                stealth_success=False,
            )

    def log_captcha_detected(self, result: CaptchaDetectionResult) -> None:
        """Log captcha detection"""
        self._browser_events["captcha_detected"] += 1
        self._log_warning(
            f"Captcha detected: {result.captcha_type.value}",
            captcha_type=result.captcha_type.value,
            page_url=result.page_url,
            proxy_host=result.proxy_host,
            proxy_port=result.proxy_port,
            detected_at=result.detected_at.isoformat(),
        )

    def log_captcha_solved(self, proxy_host: str, proxy_port: int, manual: bool = True) -> None:
        """Log captcha resolution"""
        self._browser_events["captcha_solved"] += 1
        self._log_info(
            f"Captcha solved for proxy {proxy_host}:{proxy_port}",
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            resolution_method="manual" if manual else "automatic",
            cookies_will_be_saved=True,
        )

    def log_profile_created(self, profile_name: str, proxy_info: Optional[Dict[str, Any]] = None) -> None:
        """Log profile creation"""
        self._browser_events["profile_created"] += 1
        context = {"profile_name": profile_name}
        if proxy_info:
            context.update(proxy_info)

        self._log_info(f"Browser profile created: {profile_name}", **context)

    def log_cookies_saved(self, proxy_host: str, proxy_port: int, cookies_count: int, parser_name: str) -> None:
        """Log cookie saving"""
        self._browser_events["cookies_saved"] += 1
        self._log_info(
            f"Cookies saved for {proxy_host}:{proxy_port}",
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            cookies_count=cookies_count,
            parser_name=parser_name,
            storage_type="proxy_bound",
        )

    def log_performance_metric(self, metric_name: str, value: float, unit: str, threshold: Optional[float] = None) -> None:
        """Log performance metrics"""
        exceeded = threshold is not None and value > threshold
        level = "WARNING" if exceeded else "DEBUG"
        message = f"Performance: {metric_name} = {value} {unit}"
        if threshold:
            message += f" (threshold: {threshold})"

        if exceeded:
            self._log_warning(message, metric=metric_name, value=value, unit=unit, threshold=threshold)
        else:
            self._log_debug(message, metric=metric_name, value=value, unit=unit, threshold=threshold)

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            "total_events_logged": self._events_logged,
            "browser_events": self._browser_events.copy(),
            "session_id": self.session_id,
            "parser_id": self.parser_id,
            "logger_stats": {"events_logged": self._events_logged},
        }

    def print_statistics(self) -> None:
        """Print logging statistics"""
        stats = self.get_statistics()

        self._log_info("\n📊 Browser Logger Bridge Statistics:")
        self._log_info(f"   Total events logged: {stats['total_events_logged']}")
        self._log_info(f"   Session ID: {stats['session_id']}")

        self._log_info("   Browser events:")
        for event, count in stats["browser_events"].items():
            self._log_info(f"     {event}: {count}")

        self._log_info("   Logger stats:")
        for key, value in stats["logger_stats"].items():
            self._log_info(f"     {key}: {value}")


# Factory function for easy integration
def create_browser_logger_bridge(
    session_id: Optional[str] = None,
    parser_id: Optional[str] = None,
    bridge_logs_url: Optional[str] = None,
    enable_console: bool = True,
) -> BrowserLoggerBridge:
    """
    Create browser logger bridge with smart logging integration

    This function creates a logger bridge that uses the driver's UnifiedLogger
    for consistent logging across the ecosystem with Rich console, WebSocket batching,
    and structured logging.
    """
    return BrowserLoggerBridge(
        session_id=session_id,
        parser_id=parser_id,
        bridge_logs_url=bridge_logs_url,
        enable_console=enable_console,
    )
