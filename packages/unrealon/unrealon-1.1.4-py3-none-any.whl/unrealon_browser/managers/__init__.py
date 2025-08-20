"""
Browser Managers Package - Specialized management components
"""

from .stealth import StealthManager
from .profile import ProfileManager
from .logger_bridge import BrowserLoggerBridge, create_browser_logger_bridge
from .cookies import CookieManager
from .captcha import CaptchaDetector

__all__ = [
    "StealthManager",
    "ProfileManager",
    "BrowserLoggerBridge",
    "create_browser_logger_bridge",
    "CookieManager",
    "CaptchaDetector",
]