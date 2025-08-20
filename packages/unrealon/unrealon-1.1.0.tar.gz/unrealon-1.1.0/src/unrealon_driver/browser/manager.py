"""
Modern Browser Manager built on Playwright
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None
    Page = None

from unrealon_rpc.logging import get_logger

from .config import BrowserConfig
from ..exceptions import BrowserError


class BrowserManager:
    """
    🌐 Modern Browser Manager v4.0
    
    Simplified browser automation built on Playwright with stealth capabilities.
    Designed for the new architecture where complex automation is simplified.
    
    Features:
    - 🎭 Stealth Mode: Anti-detection by default
    - 🍪 Cookie Persistence: Automatic cookie management
    - 📸 Screenshots: Debug-friendly screenshot capture
    - ⚡ Performance: Optimized for speed and reliability
    - 🔧 Zero Config: Works out of the box
    """
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize browser manager
        
        Args:
            config: Browser configuration
        """
        if async_playwright is None:
            raise BrowserError(
                "Playwright is not installed. Install it with: pip install playwright && playwright install"
            )
            
        self.config = config
        self.logger = get_logger()
        
        # Browser components
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # State
        self._is_initialized = False
        self._session_id = str(uuid.uuid4())
        
    # ==========================================
    # LIFECYCLE MANAGEMENT
    # ==========================================
    
    async def initialize(self) -> None:
        """Initialize browser components"""
        if self._is_initialized:
            return
            
        try:
            self.logger.info("Initializing browser manager...")
            
            # Start Playwright
            self._playwright = await async_playwright().start()
            
            # Launch browser
            browser_args = self._get_browser_args()
            
            if self.config.browser_type == "chromium":
                self._browser = await self._playwright.chromium.launch(**browser_args)
            elif self.config.browser_type == "firefox":
                self._browser = await self._playwright.firefox.launch(**browser_args)
            elif self.config.browser_type == "webkit":
                self._browser = await self._playwright.webkit.launch(**browser_args)
            else:
                raise BrowserError(f"Unsupported browser type: {self.config.browser_type}")
            
            # Create context
            context_args = self._get_context_args()
            self._context = await self._browser.new_context(**context_args)
            
            # Load cookies if available
            await self._load_cookies()
            
            # Create page
            self._page = await self._context.new_page()
            
            # Setup stealth mode
            if self.config.stealth_mode:
                await self._setup_stealth()
            
            # Set timeouts
            self._page.set_default_timeout(self.config.page_timeout)
            self._page.set_default_navigation_timeout(self.config.navigation_timeout)
            
            self._is_initialized = True
            self.logger.info(f"Browser initialized: {self.config.browser_type}")
            
        except Exception as e:
            await self.cleanup()
            raise BrowserError(f"Failed to initialize browser: {e}")
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        self.logger.info("Cleaning up browser resources...")
        
        try:
            # Save cookies
            if self._context and self.config.persist_cookies:
                await self._save_cookies()
            
            # Close page
            if self._page:
                await self._page.close()
                self._page = None
            
            # Close context
            if self._context:
                await self._context.close()
                self._context = None
            
            # Close browser
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            # Stop Playwright
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            self._is_initialized = False
            self.logger.info("Browser cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during browser cleanup: {e}")
    
    # ==========================================
    # HIGH-LEVEL METHODS
    # ==========================================
    
    async def get_html(self, url: str, wait_for: Optional[str] = None) -> str:
        """
        Get HTML content from URL
        
        Args:
            url: Target URL
            wait_for: Optional CSS selector to wait for
            
        Returns:
            HTML content as string
        """
        await self._ensure_initialized()
        
        try:
            self.logger.info(f"Navigating to: {url}")
            
            # Navigate to URL
            await self._page.goto(url, wait_until="domcontentloaded")
            
            # Wait for specific element if requested
            if wait_for:
                await self._page.wait_for_selector(wait_for, timeout=self.config.element_timeout)
            
            # Get HTML content
            html = await self._page.content()
            
            # Save screenshot if debugging
            if self.config.save_screenshots:
                await self._save_screenshot(f"get_html_{url.replace('/', '_')}")
            
            self.logger.info(f"Retrieved HTML content: {len(html)} characters")
            return html
            
        except Exception as e:
            if self.config.save_screenshots:
                await self._save_screenshot(f"error_{url.replace('/', '_')}")
            raise BrowserError(f"Failed to get HTML from {url}: {e}")
    
    async def extract_elements(
        self, 
        url: str, 
        selector: str, 
        attribute: Optional[str] = None
    ) -> List[str]:
        """
        Extract elements from URL using CSS selector
        
        Args:
            url: Target URL
            selector: CSS selector
            attribute: Optional attribute to extract (default: text content)
            
        Returns:
            List of extracted values
        """
        await self._ensure_initialized()
        
        try:
            self.logger.info(f"Extracting elements from: {url}")
            
            # Navigate to URL
            await self._page.goto(url, wait_until="domcontentloaded")
            
            # Wait for elements
            await self._page.wait_for_selector(selector, timeout=self.config.element_timeout)
            
            # Extract elements
            if attribute:
                elements = await self._page.eval_on_selector_all(
                    selector, 
                    f"elements => elements.map(el => el.getAttribute('{attribute}'))"
                )
            else:
                elements = await self._page.eval_on_selector_all(
                    selector, 
                    "elements => elements.map(el => el.textContent.trim())"
                )
            
            # Filter out empty values
            elements = [el for el in elements if el and el.strip()]
            
            self.logger.info(f"Extracted {len(elements)} elements")
            return elements
            
        except Exception as e:
            raise BrowserError(f"Failed to extract elements from {url}: {e}")
    
    async def screenshot(self, filename: Optional[str] = None) -> Path:
        """
        Take screenshot of current page
        
        Args:
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to screenshot file
        """
        await self._ensure_initialized()
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        if not filename.endswith('.png'):
            filename += '.png'
        
        screenshot_path = self.config.screenshots_dir / filename
        
        try:
            await self._page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            raise BrowserError(f"Failed to take screenshot: {e}")
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Browser health check"""
        return {
            "status": "healthy" if self._is_initialized else "not_initialized",
            "browser_type": self.config.browser_type,
            "session_id": self._session_id,
            "stealth_mode": self.config.stealth_mode,
            "headless": self.config.headless,
            "initialized": self._is_initialized
        }
    
    # ==========================================
    # PRIVATE METHODS
    # ==========================================
    
    async def _ensure_initialized(self) -> None:
        """Ensure browser is initialized"""
        if not self._is_initialized:
            await self.initialize()
    
    def _get_browser_args(self) -> Dict[str, Any]:
        """Get browser launch arguments"""
        args = {
            "headless": self.config.headless,
            "args": self.config.extra_args.copy()
        }
        
        # Add stealth arguments
        if self.config.stealth_mode:
            args["args"].extend([
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ])
        
        # Add performance arguments
        if self.config.disable_images:
            args["args"].append("--disable-images")
        
        return args
    
    def _get_context_args(self) -> Dict[str, Any]:
        """Get browser context arguments"""
        args = {
            "viewport": {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
        }
        
        # User agent
        if self.config.user_agent:
            args["user_agent"] = self.config.user_agent
        
        # Proxy
        if self.config.proxy_url:
            proxy_config = {"server": self.config.proxy_url}
            if self.config.proxy_username:
                proxy_config["username"] = self.config.proxy_username
            if self.config.proxy_password:
                proxy_config["password"] = self.config.proxy_password
            args["proxy"] = proxy_config
        
        # Disable resources
        if self.config.disable_javascript:
            args["java_script_enabled"] = False
        
        return args
    
    async def _setup_stealth(self) -> None:
        """Setup stealth mode"""
        # Add stealth scripts
        await self._page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
    
    async def _load_cookies(self) -> None:
        """Load cookies from file"""
        if not self.config.persist_cookies or not self.config.cookies_file:
            return
        
        try:
            if self.config.cookies_file.exists():
                with open(self.config.cookies_file, 'r') as f:
                    cookies = json.load(f)
                await self._context.add_cookies(cookies)
                self.logger.info(f"Loaded {len(cookies)} cookies")
        except Exception as e:
            self.logger.warning(f"Failed to load cookies: {e}")
    
    async def _save_cookies(self) -> None:
        """Save cookies to file"""
        if not self.config.persist_cookies or not self.config.cookies_file:
            return
        
        try:
            cookies = await self._context.cookies()
            with open(self.config.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            self.logger.info(f"Saved {len(cookies)} cookies")
        except Exception as e:
            self.logger.warning(f"Failed to save cookies: {e}")
    
    async def _save_screenshot(self, name: str) -> None:
        """Save debug screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            await self.screenshot(filename)
        except Exception as e:
            self.logger.warning(f"Failed to save debug screenshot: {e}")
    
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
