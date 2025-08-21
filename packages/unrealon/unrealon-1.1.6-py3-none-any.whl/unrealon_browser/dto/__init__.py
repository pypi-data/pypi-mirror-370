"""
Browser DTOs - Data Transfer Objects

Simplified data models for browser automation.
Based on proven unrealparser patterns with minimal complexity.
"""

# Enums
from .models.enums import (
    BrowserType,
    BrowserMode,
    # 🔥 StealthLevel removed - STEALTH ALWAYS ON!
    CaptchaType,
    CaptchaStatus,
    ProfileType,
    BrowserSessionStatus,
)

# Configuration models
from .models.config import BrowserConfig

# Statistics models
from .models.statistics import (
    BrowserManagerStatistics,
    BrowserStatistics,
)

# Core models
from .models.core import (
    ProxyInfo,
    PageResult,
    BrowserSession,
)

# Detection models
from .models.detection import (
    CaptchaDetection,
    CaptchaDetectionResult,
    CookieMetadata,
)


# Exports
__all__ = [
    # Enums
    "BrowserType",
    "BrowserMode",
    "CaptchaType",
    "CaptchaStatus",
    "ProfileType",
    "BrowserSessionStatus",
    # Configuration
    "BrowserConfig",
    # Statistics
    "BrowserManagerStatistics",
    "BrowserStatistics",
    # Dataclasses
    "ProxyInfo",
    "PageResult",
    "BrowserSession",
    # Detection models
    "CaptchaDetection",
    "CaptchaDetectionResult",
    "CookieMetadata",
]
