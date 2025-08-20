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

# Import from unrealon_driver
from unrealon_driver.parser.managers.logging import LoggingManager, LoggingConfig, LogLevel, get_logging_manager


class BrowserLoggerBridge:
    """
    Bridge between unrealon_browser and unrealon_driver loggers

    Provides unified logging interface for browser operations using
    the driver's LoggingManager for consistent logging across the ecosystem.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        bridge_client: Optional[Any] = None,
        enable_console: bool = True,
    ):
        """Initialize logger bridge"""
        self.session_id = session_id or str(uuid.uuid4())

        # Create logging manager from driver
        self.logger = get_logging_manager(parser_name="unrealon_browser", bridge_client=bridge_client, console_enabled=enable_console, file_enabled=True, bridge_enabled=bridge_client is not None)

        # Set session context
        self.logger.set_session(self.session_id)

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

    def _log_debug(self, message: str, **context: Any) -> None:
        """Debug level logging using driver logger"""
        self._events_logged += 1
        self.logger.debug(message, **context)

    def _log_info(self, message: str, **context: Any) -> None:
        """Info level logging using driver logger"""
        self._events_logged += 1
        self.logger.info(message, **context)

    def _log_warning(self, message: str, **context: Any) -> None:
        """Warning level logging using driver logger"""
        self._events_logged += 1
        self.logger.warning(message, **context)

    def _log_error(self, message: str, **context: Any) -> None:
        """Error level logging using driver logger"""
        self._events_logged += 1
        self.logger.error(message, **context)

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
            "logger_stats": self.logger.get_log_stats(),
        }

    def print_statistics(self) -> None:
        """Print logging statistics"""
        stats = self.get_statistics()

        print("\n📊 Browser Logger Bridge Statistics:")
        print(f"   Total events logged: {stats['total_events_logged']}")
        print(f"   Session ID: {stats['session_id']}")

        print("   Browser events:")
        for event, count in stats["browser_events"].items():
            print(f"     {event}: {count}")

        print("   Logger stats:")
        for key, value in stats["logger_stats"].items():
            print(f"     {key}: {value}")


# Factory function for easy integration
def create_browser_logger_bridge(
    session_id: Optional[str] = None,
    bridge_client: Optional[Any] = None,
    enable_console: bool = True,
) -> BrowserLoggerBridge:
    """
    Create browser logger bridge with driver integration

    This function creates a logger bridge that uses the driver's LoggingManager
    for consistent logging across the ecosystem.
    """
    return BrowserLoggerBridge(
        session_id=session_id,
        bridge_client=bridge_client,
        enable_console=enable_console,
    )
