"""
UnrealOn Browser - Independent Browser Automation Module
Enterprise-grade browser automation with stealth capabilities and proxy integration.

Based on proven patterns from unrealparser with modular architecture.
"""

from importlib.metadata import version

try:
    __version__ = version("unrealon")
except Exception:
    __version__ = "0.1.0"

# Core browser management
from .core import BrowserManager

# Specialized managers
from .managers import (
    StealthManager,
    ProfileManager,
    CookieManager,
    CaptchaDetector,
)

# Note: CLI interfaces are available as standalone modules
# Import them directly: from unrealon_browser.cli import BrowserCLI, CookiesCLI

# API client
try:
    from .api import BrowserApiClient
except ImportError:
    BrowserApiClient = None


# Data models
from .dto import (
    BrowserConfig,
    BrowserType,
    BrowserMode,
    BrowserSessionStatus,
    BrowserSession,
    ProxyInfo,
    CaptchaType,
    CaptchaStatus,
    CaptchaDetectionResult,
)

__all__ = [
    # Core
    "BrowserManager",
    # Managers
    "StealthManager",
    "ProfileManager",
    "CookieManager",
    "CaptchaDetector",
    # API
    "BrowserApiClient",
    # DTOs (CLI available as: from unrealon_browser.cli import BrowserCLI, CookiesCLI)
    "BrowserConfig",
    "BrowserType",
    "BrowserMode",
    "BrowserSessionStatus",
    "BrowserSession",
    "ProxyInfo",
    "CaptchaType",
    "CaptchaStatus",
    "CaptchaDetectionResult",
]
