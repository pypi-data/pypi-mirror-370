"""
Browser DTOs - Enumerations

All enum types for browser automation.
"""

from enum import Enum


class BrowserType(str, Enum):
    """Supported browser types."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class BrowserMode(str, Enum):
    """Browser execution modes."""

    HEADLESS = "headless"
    HEADED = "headed"
    AUTO = "auto"


class CaptchaType(str, Enum):
    """Captcha types for detection."""

    RECAPTCHA = "recaptcha"
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE = "cloudflare"
    VERIFICATION = "verification"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class CaptchaStatus(str, Enum):
    """Captcha handling status."""

    NOT_DETECTED = "not_detected"
    DETECTED = "detected"
    MANUAL_SOLVING = "manual_solving"
    SOLVED = "solved"
    TIMEOUT = "timeout"


class ProfileType(str, Enum):
    """Browser profile types."""

    TEMPORARY = "temporary"
    PERSISTENT = "persistent"
    STEALTH = "stealth"
    PROXY_BOUND = "proxy_bound"


class BrowserSessionStatus(str, Enum):
    """Browser session status."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    CAPTCHA_REQUIRED = "captcha_required"
    ERROR = "error"
    CLOSED = "closed"
