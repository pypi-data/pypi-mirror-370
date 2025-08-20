"""
Cookie Manager - Layer 3: Proxy-bound cookie management with persistent storage
Adapted from reliable unrealparser implementation with UnrealOn SDK integration
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import logging

# Browser DTOs
from unrealon_browser.dto import ProxyInfo, CookieMetadata
from pydantic import BaseModel

# Playwright imports
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)


class CookieSet(BaseModel):
    proxy_info: ProxyInfo
    cookies: Dict[str, str]
    metadata: CookieMetadata


class CookieStorage(BaseModel):
    cookies_array: List[CookieSet]


class CookieManager:
    """
    Cookie Manager with proxy-bound persistence

    Key features from unrealparser:
    - Cookies bound to specific proxy configurations
    - Persistent storage in JSON format
    - Automatic loading/saving based on proxy
    - Metadata tracking for debugging
    - Support for multiple parsers
    """

    def __init__(self, cookies_dir: str = "cookies", parser_name: str = "default_parser", logger_bridge=None):
        """Initialize cookie manager"""
        self.cookies_dir = Path(cookies_dir)
        self.parser_name = parser_name
        self.cookies_file = self.cookies_dir / f"{parser_name}_cookies.json"
        self.logger_bridge = logger_bridge

        # Create cookies directory if it doesn't exist
        self.cookies_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage for current session
        self._current_cookies: Dict[str, CookieSet] = {}

        # Statistics
        self._cookies_saved = 0
        self._cookies_loaded = 0
        self._proxies_with_cookies = 0

        # Load existing cookies
        self._load_cookies_from_file()

    def _logger(self, message: str, level: str = "info") -> None:
        if self.logger_bridge:
            if level == "info":
                self.logger_bridge.log_info(message)
            elif level == "error":
                self.logger_bridge.log_error(message)
            elif level == "warning":
                self.logger_bridge.log_warning(message)
            else:
                self.logger_bridge.log_info(message)
        else:
            if level == "info":
                logger.info(message)
            elif level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)
            else:
                logger.info(message)

    def _generate_proxy_key(self, proxy_info: ProxyInfo) -> str:
        """Generate unique key for proxy configuration"""
        return f"{proxy_info.host}:{proxy_info.port}"

    def _load_cookies_from_file(self) -> None:
        """Load cookies from persistent storage"""
        try:
            if self.cookies_file.exists():
                with open(self.cookies_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parse storage format
                storage = CookieStorage(**data)

                # Convert to in-memory format
                for cookie_set in storage.cookies_array:
                    proxy_key = self._generate_proxy_key(cookie_set.proxy_info)
                    self._current_cookies[proxy_key] = cookie_set

                self._proxies_with_cookies = len(self._current_cookies)
                self._logger(f"🍪 Loaded cookies for {self._proxies_with_cookies} proxies", "info")
            else:
                self._logger(f"🍪 No existing cookies file found, starting fresh", "info")

        except Exception as e:
            self._logger(f"❌ Error loading cookies: {e}", "error")
            self._current_cookies = {}

    def _save_cookies_to_file(self) -> None:
        """Save cookies to persistent storage"""
        try:
            # Convert in-memory format to storage format
            cookies_array = list(self._current_cookies.values())
            storage = CookieStorage(cookies_array=cookies_array)

            # Save to file
            with open(self.cookies_file, "w", encoding="utf-8") as f:
                json.dump(storage.model_dump(), f, indent=2, ensure_ascii=False, default=str)

            self._logger(f"💾 Saved cookies for {len(cookies_array)} proxies to {self.cookies_file}", "info")

        except Exception as e:
            self._logger(f"❌ Error saving cookies: {e}", "error")

    async def load_cookies_for_proxy(self, page: Page, proxy_info: ProxyInfo) -> bool:
        """
        Load cookies for specific proxy configuration

        Args:
            page: Playwright page instance
            proxy_info: Proxy configuration

        Returns:
            True if cookies were loaded, False otherwise
        """

        try:
            proxy_key = self._generate_proxy_key(proxy_info)

            if proxy_key not in self._current_cookies:
                self._logger(f"🍪 No cookies found for proxy {proxy_key}", "info")
                return False

            cookie_set = self._current_cookies[proxy_key]

            # Convert cookies to Playwright format
            playwright_cookies = []
            for name, value in cookie_set.cookies.items():
                playwright_cookies.append(
                    {
                        "name": name,
                        "value": value,
                        "domain": ".example.com",  # Will be updated based on actual usage
                        "path": "/",
                    }
                )

            # Set cookies in browser context
            context = page.context
            await context.add_cookies(playwright_cookies)

            self._cookies_loaded += 1
            self._logger(f"✅ Loaded {len(playwright_cookies)} cookies for proxy {proxy_key}", "info")

            return True

        except Exception as e:
            self._logger(f"❌ Error loading cookies for proxy {proxy_info.host}:{proxy_info.port}: {e}", "error")
            return False

    async def save_cookies_with_proxy(self, page: Page, proxy_info: ProxyInfo) -> bool:
        """
        Save cookies from current page session bound to proxy

        Args:
            page: Playwright page instance
            proxy_info: Proxy configuration

        Returns:
            True if cookies were saved, False otherwise
        """

        try:
            # Get cookies from browser context
            context = page.context
            playwright_cookies = await context.cookies()

            if not playwright_cookies:
                self._logger(f"🍪 No cookies to save for proxy {proxy_info.host}:{proxy_info.port}", "info")
                return False

            # Convert to our format
            cookies_dict = {}
            for cookie in playwright_cookies:
                cookies_dict[cookie["name"]] = cookie["value"]

            # Create metadata
            metadata = CookieMetadata(
                saved_at=datetime.now(timezone.utc),
                parser_name=self.parser_name,
                cookies_count=len(cookies_dict),
            )

            # Create cookie set
            cookie_set = CookieSet(
                proxy_info=proxy_info,
                cookies=cookies_dict,
                metadata=metadata,
            )

            # Store in memory
            proxy_key = self._generate_proxy_key(proxy_info)
            self._current_cookies[proxy_key] = cookie_set

            # Save to file
            self._save_cookies_to_file()

            self._cookies_saved += 1
            self._proxies_with_cookies = len(self._current_cookies)

            self._logger(f"💾 Saved {len(cookies_dict)} cookies for proxy {proxy_key}", "info")

            return True

        except Exception as e:
            self._logger(f"❌ Error saving cookies for proxy {proxy_info.host}:{proxy_info.port}: {e}", "error")
            return False

    def get_proxies_with_cookies(self) -> List[ProxyInfo]:
        """Get list of proxies that have saved cookies"""
        return [cookie_set.proxy_info for cookie_set in self._current_cookies.values()]

    def has_cookies_for_proxy(self, proxy_info: ProxyInfo) -> bool:
        """Check if cookies exist for specific proxy"""
        proxy_key = self._generate_proxy_key(proxy_info)
        return proxy_key in self._current_cookies

    def get_cookie_metadata_for_proxy(self, proxy_info: ProxyInfo) -> Optional[CookieMetadata]:
        """Get cookie metadata for specific proxy"""
        proxy_key = self._generate_proxy_key(proxy_info)

        if proxy_key in self._current_cookies:
            return self._current_cookies[proxy_key].metadata

        return None

    def clear_cookies_for_proxy(self, proxy_info: ProxyInfo) -> bool:
        """Clear cookies for specific proxy"""
        proxy_key = self._generate_proxy_key(proxy_info)

        if proxy_key in self._current_cookies:
            del self._current_cookies[proxy_key]
            self._save_cookies_to_file()
            self._proxies_with_cookies = len(self._current_cookies)
            self._logger(f"🗑️ Cleared cookies for proxy {proxy_key}", "info")
            return True

        return False

    def clear_all_cookies(self) -> None:
        """Clear all stored cookies"""
        self._current_cookies.clear()
        self._save_cookies_to_file()
        self._proxies_with_cookies = 0
        self._logger("🗑️ Cleared all cookies", "info")

    def cleanup_old_cookies(self, max_age_days: int = 30) -> int:
        """
        Remove cookies older than specified days

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of cookie sets removed
        """
        removed_count = 0
        current_time = datetime.now(timezone.utc)

        # Find old cookies
        old_proxy_keys = []
        for proxy_key, cookie_set in self._current_cookies.items():
            age_days = (current_time - cookie_set.metadata.saved_at).days
            if age_days > max_age_days:
                old_proxy_keys.append(proxy_key)

        # Remove old cookies
        for proxy_key in old_proxy_keys:
            del self._current_cookies[proxy_key]
            removed_count += 1

        if removed_count > 0:
            self._save_cookies_to_file()
            self._proxies_with_cookies = len(self._current_cookies)
            self._logger(f"🧹 Cleaned up {removed_count} old cookie sets (>{max_age_days} days)", "info")

        return removed_count

    async def test_cookies_with_proxy(self, page: Page, proxy_info: ProxyInfo, test_url: str = "https://httpbin.org/cookies") -> Dict[str, Any]:
        """
        Test cookie functionality with specific proxy

        Args:
            page: Playwright page instance
            proxy_info: Proxy configuration
            test_url: URL to test cookies

        Returns:
            Test results
        """

        try:
            # Load existing cookies
            cookies_loaded = await self.load_cookies_for_proxy(page, proxy_info)

            # Navigate to test URL
            await page.goto(test_url, wait_until="networkidle")

            # Get response data
            content = await page.content()

            # Save any new cookies
            cookies_saved = await self.save_cookies_with_proxy(page, proxy_info)

            return {
                "success": True,
                "proxy_key": self._generate_proxy_key(proxy_info),
                "cookies_loaded": cookies_loaded,
                "cookies_saved": cookies_saved,
                "test_url": test_url,
                "page_title": await page.title(),
                "has_cookies": self.has_cookies_for_proxy(proxy_info),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "proxy_key": self._generate_proxy_key(proxy_info),
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get cookie manager statistics"""
        return {
            "parser_name": self.parser_name,
            "cookies_dir": str(self.cookies_dir),
            "cookies_file": str(self.cookies_file),
            "proxies_with_cookies": self._proxies_with_cookies,
            "cookies_saved": self._cookies_saved,
            "cookies_loaded": self._cookies_loaded,
            "total_cookie_sets": len(self._current_cookies),
            "storage_file_exists": self.cookies_file.exists(),
            "storage_file_size_bytes": (self.cookies_file.stat().st_size if self.cookies_file.exists() else 0),
        }

    def print_statistics(self) -> None:
        """Print cookie manager statistics"""
        stats = self.get_statistics()

        print(f"\n🍪 Cookie Manager Statistics:")
        print(f"   Parser: {stats['parser_name']}")
        print(f"   Proxies with cookies: {stats['proxies_with_cookies']}")
        print(f"   Cookies saved: {stats['cookies_saved']}")
        print(f"   Cookies loaded: {stats['cookies_loaded']}")
        print(f"   Storage file: {stats['cookies_file']}")
        print(f"   Storage size: {stats['storage_file_size_bytes']} bytes")

        # Show proxy details
        if self._current_cookies:
            self._logger("   Cookie details:", "info")
            for proxy_key, cookie_set in self._current_cookies.items():
                metadata = cookie_set.metadata
                self._logger(f"     {proxy_key}: {metadata.cookies_count} cookies (saved {metadata.saved_at.strftime('%Y-%m-%d %H:%M')})", "info")
        else:
            self._logger("   No cookies stored", "info")

    def export_cookies_for_proxy(self, proxy_info: ProxyInfo) -> Optional[Dict[str, Any]]:
        """
        Export cookies for specific proxy in JSON format

        Args:
            proxy_info: Proxy configuration

        Returns:
            Cookie data or None if not found
        """
        proxy_key = self._generate_proxy_key(proxy_info)

        if proxy_key in self._current_cookies:
            cookie_set = self._current_cookies[proxy_key]
            return cookie_set.model_dump()

        return None

    def import_cookies_for_proxy(self, proxy_info: ProxyInfo, cookie_data: Dict[str, Any]) -> bool:
        """
        Import cookies for specific proxy from JSON data

        Args:
            proxy_info: Proxy configuration
            cookie_data: Cookie data in CookieSet format

        Returns:
            True if imported successfully
        """
        try:
            cookie_set = CookieSet(**cookie_data)
            proxy_key = self._generate_proxy_key(proxy_info)

            self._current_cookies[proxy_key] = cookie_set
            self._save_cookies_to_file()
            self._proxies_with_cookies = len(self._current_cookies)

            self._logger(f"📥 Imported cookies for proxy {proxy_key}", "info")
            return True

        except Exception as e:
            self._logger(f"❌ Error importing cookies: {e}", "error")
            return False
