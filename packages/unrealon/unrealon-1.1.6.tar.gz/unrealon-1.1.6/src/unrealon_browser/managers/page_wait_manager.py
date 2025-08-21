"""
Page Wait Manager - Convenient methods for different page loading scenarios
"""
import asyncio
from typing import Optional
from playwright.async_api import Page

from .logger_bridge import BrowserLoggerBridge as LoggingBridge


class PageWaitManager:
    """Manager for different page waiting strategies"""
    
    def __init__(self, page: Optional[Page], logger_bridge: LoggingBridge):
        self._page = page
        self.logger_bridge = logger_bridge
    
    def update_page(self, page: Optional[Page]):
        """Update the page reference"""
        self._page = page
    
    # Quick wait methods with fallback
    async def wait_fast_with_fallback(self) -> bool:
        """Fast wait - networkidle 5s, fallback to domcontentloaded 3s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("🚀 Fast wait with fallback (networkidle 5s → domcontentloaded 3s)")
        
        # Try networkidle first
        if await self._wait_for_state("networkidle", 5000):
            return True
            
        # Fallback to domcontentloaded
        self.logger_bridge.log_info("⏳ Networkidle timeout, trying domcontentloaded...")
        return await self._wait_for_state("domcontentloaded", 3000)
    
    async def wait_safe_with_fallback(self) -> bool:
        """Safe wait - networkidle 10s, fallback to domcontentloaded 5s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("🛡️ Safe wait with fallback (networkidle 10s → domcontentloaded 5s)")
        
        # Try networkidle first
        if await self._wait_for_state("networkidle", 10000):
            return True
            
        # Fallback to domcontentloaded
        self.logger_bridge.log_info("⏳ Networkidle timeout, trying domcontentloaded...")
        return await self._wait_for_state("domcontentloaded", 5000)
    
    # Generic methods
    async def wait_fast(self) -> bool:
        """Fast wait - domcontentloaded 3s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("⚡ Fast wait (domcontentloaded 3s)")
        return await self._wait_for_state("domcontentloaded", 3000)
    
    async def wait_standard(self) -> bool:
        """Standard wait - networkidle 10s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("⏳ Standard wait (networkidle 10s)")
        return await self._wait_for_state("networkidle", 10000)
    
    async def wait_full_load(self) -> bool:
        """Full page load including images - load 30s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("🖼️ Full load wait (load 30s)")
        return await self._wait_for_state("load", 30000)
    
    async def wait_minimal(self) -> bool:
        """Minimal wait - domcontentloaded 1s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("⚡ Minimal wait (domcontentloaded 1s)")
        return await self._wait_for_state("domcontentloaded", 1000)
    
    # Specialized methods
    async def wait_spa(self) -> bool:
        """Single Page Application wait - networkidle 15s"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info("⚛️ SPA wait (networkidle 15s)")
        return await self._wait_for_state("networkidle", 15000)
    
    # Custom methods
    async def wait_custom(self, wait_type: str = "networkidle", timeout: int = 10000) -> bool:
        """Custom wait with specified parameters"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info(f"🔧 Custom wait ({wait_type} {timeout}ms)")
        return await self._wait_for_state(wait_type, timeout)
    
    async def wait_with_fallback(self, 
                                primary_type: str = "networkidle", 
                                primary_timeout: int = 10000,
                                fallback_type: str = "domcontentloaded", 
                                fallback_timeout: int = 5000) -> bool:
        """Wait with custom fallback strategy"""
        if not self._page:
            return False
            
        self.logger_bridge.log_info(f"🔄 Fallback wait ({primary_type} {primary_timeout}ms → {fallback_type} {fallback_timeout}ms)")
        
        # Try primary first
        if await self._wait_for_state(primary_type, primary_timeout):
            return True
            
        # Fallback
        self.logger_bridge.log_info(f"⏳ {primary_type} timeout, trying {fallback_type}...")
        return await self._wait_for_state(fallback_type, fallback_timeout)
    
    # Helper methods
    async def _wait_for_state(self, wait_type: str, timeout: int) -> bool:
        """Internal method to wait for specific state"""
        if not self._page:
            return False
            
        try:
            if wait_type == "networkidle":
                await self._page.wait_for_load_state("networkidle", timeout=timeout)
            elif wait_type == "domcontentloaded":
                await self._page.wait_for_load_state("domcontentloaded", timeout=timeout)
            elif wait_type == "load":
                await self._page.wait_for_load_state("load", timeout=timeout)
            else:
                # Default to networkidle
                await self._page.wait_for_load_state("networkidle", timeout=timeout)
            
            self.logger_bridge.log_info(f"✅ Page ready ({wait_type})")
            return True
            
        except Exception as e:
            self.logger_bridge.log_warning(f"⚠️ Page ready timeout ({wait_type}): {e}")
            return False
    
    # Utility methods
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for specific selector to appear"""
        if not self._page:
            return False
            
        try:
            self.logger_bridge.log_info(f"🎯 Waiting for selector: {selector}")
            await self._page.wait_for_selector(selector, timeout=timeout)
            self.logger_bridge.log_info(f"✅ Selector found: {selector}")
            return True
        except Exception as e:
            self.logger_bridge.log_warning(f"⚠️ Selector timeout: {selector} - {e}")
            return False
    
    async def wait_for_text(self, text: str, timeout: int = 10000) -> bool:
        """Wait for specific text to appear on page"""
        if not self._page:
            return False
            
        try:
            self.logger_bridge.log_info(f"📝 Waiting for text: {text}")
            await self._page.wait_for_function(
                f"document.body.innerText.includes('{text}')",
                timeout=timeout
            )
            self.logger_bridge.log_info(f"✅ Text found: {text}")
            return True
        except Exception as e:
            self.logger_bridge.log_warning(f"⚠️ Text timeout: {text} - {e}")
            return False
    
    async def wait_for_url_change(self, timeout: int = 10000) -> bool:
        """Wait for URL to change"""
        if not self._page:
            return False
            
        try:
            current_url = self._page.url
            self.logger_bridge.log_info(f"🔗 Waiting for URL change from: {current_url}")
            
            await self._page.wait_for_function(
                f"window.location.href !== '{current_url}'",
                timeout=timeout
            )
            
            new_url = self._page.url
            self.logger_bridge.log_info(f"✅ URL changed to: {new_url}")
            return True
        except Exception as e:
            self.logger_bridge.log_warning(f"⚠️ URL change timeout: {e}")
            return False
