"""
Stealth Manager - Anti-detection system for browser automation
Layer 1: Advanced stealth capabilities inspired by unrealparser
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import Page, BrowserContext

# CRITICAL REQUIREMENTS COMPLIANCE - NO INLINE IMPORTS!
from playwright_stealth import stealth, Stealth

logger = logging.getLogger(__name__)


class StealthManager:
    """
    Advanced anti-detection system for browser automation

    Layer 1: Stealth capabilities
    - Playwright-stealth integration
    - WebDriver property removal
    - Bot detection testing
    - Stealth arguments optimization
    """

    def __init__(self, logger_bridge=None):
        """Initialize stealth manager"""
        self.stealth_applied = False
        self.test_results: Optional[Dict[str, Any]] = None
        self.logger_bridge = logger_bridge

    def get_stealth_args(self) -> List[str]:
        """
        Get browser launch arguments for stealth mode
        Based on unrealparser's proven stealth arguments
        """
        return [
            # Minimal stealth arguments from working unrealparser code
            "--disable-blink-features=AutomationControlled",  # Remove navigator.webdriver
            "--no-sandbox",  # Required for container environments
            "--disable-dev-shm-usage",  # Fix memory issues in containers
            # Additional safe arguments for better stealth
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
        ]

    # private warpper for logger with if self.logger_bridge
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

    async def apply_stealth(self, page: Page) -> bool:
        """
        Apply stealth measures to page
        Combines multiple anti-detection techniques
        """
        try:
            self._logger("🥷 Applying stealth measures...", "info")

            # 1. Apply playwright-stealth if available
            stealth_applied = await self._apply_playwright_stealth(page)

            # 2. Remove webdriver property
            await self._remove_webdriver_property(page)

            # 3. Apply additional stealth scripts
            await self._apply_custom_stealth_scripts(page)

            # 4. Set realistic properties
            await self._set_realistic_properties(page)

            self.stealth_applied = True
            self._logger("✅ Stealth measures applied successfully", "info")

            return True

        except Exception as e:
            self._logger(f"❌ Failed to apply stealth measures: {e}", "error")
            self.stealth_applied = False
            return False

    async def _apply_playwright_stealth(self, page: Page) -> bool:
        """Apply playwright-stealth with custom config"""
        try:
            # 🔥 WEBDRIVER ONLY CONFIG: Only remove webdriver, nothing else!
            stealth_config = Stealth(
                navigator_webdriver=True,  # ONLY webdriver removal
                chrome_runtime=False,  # DISABLE - we do it ourselves
                navigator_languages=False,  # DISABLE - we do it ourselves
                navigator_permissions=False,  # DISABLE - we do it ourselves
                navigator_plugins=False,  # DISABLE - we do it ourselves
                webgl_vendor=False,  # DISABLE - we do it ourselves
                chrome_app=False,  # DISABLE
                chrome_csi=False,  # DISABLE
                chrome_load_times=False,  # DISABLE
                iframe_content_window=False,  # DISABLE
                media_codecs=False,  # DISABLE
                navigator_user_agent=False,  # DISABLE
                navigator_vendor=False,  # DISABLE
                navigator_platform=False,  # DISABLE
                hairline=False,  # DISABLE
                sec_ch_ua=False,  # DISABLE
                navigator_hardware_concurrency=False,  # DISABLE
            )

            await stealth(page, config=stealth_config)
            self._logger("✅ Playwright-stealth applied with CUSTOM config", "info")
            return True
        except Exception as e:
            self._logger(f"❌ playwright-stealth failed: {e}", "error")
            return False

    async def _remove_webdriver_property(self, page: Page) -> None:
        """Remove navigator.webdriver property - HANDLED BY PLAYWRIGHT-STEALTH"""
        # 🔥 REDUNDANT: playwright-stealth already does this with webdriver=True
        self._logger("✅ WebDriver property removal handled by playwright-stealth", "info")

    async def _apply_custom_stealth_scripts(self, page: Page) -> None:
        """Apply custom stealth scripts"""
        # Create proper chrome object (bot.sannysoft.com expects this!)
        chrome_runtime_script = """
        // Create realistic window.chrome object
        if (!window.chrome) {
            window.chrome = {
                app: {
                    isInstalled: false,
                },
                runtime: {
                    onConnect: {
                        addListener: function() {},
                        hasListener: function() { return false; },
                        removeListener: function() {},
                    },
                    onMessage: {
                        addListener: function() {},
                        hasListener: function() { return false; },
                        removeListener: function() {},
                    },
                    connect: function() { return {}; },
                    sendMessage: function() {},
                },
                storage: {
                    local: {
                        get: function() {},
                        set: function() {},
                        remove: function() {},
                        clear: function() {},
                    },
                    sync: {
                        get: function() {},
                        set: function() {},
                        remove: function() {},
                        clear: function() {},
                    },
                },
                tabs: {
                    create: function() {},
                    query: function() {},
                    update: function() {},
                },
            };
        }
        """
        await page.add_init_script(chrome_runtime_script)

        # Override permissions
        permissions_script = """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        await page.add_init_script(permissions_script)

        self._logger("✅ Custom stealth scripts applied", "info")

    async def _set_realistic_properties(self, page: Page) -> None:
        """Set realistic browser properties"""
        realistic_script = """
        // Set realistic hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 4,
        });
        
        // Set realistic deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
        });
        
        // Set realistic connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
            }),
        });
        """
        await page.add_init_script(realistic_script)
        self._logger("✅ Realistic properties set", "info")

    async def test_stealth_on_sannysoft(self, browser_manager) -> Dict[str, Any]:
        """
        Test stealth effectiveness on bot.sannysoft.com
        Based on unrealparser's stealth testing approach
        """
        if not browser_manager or not browser_manager.page:
            return {
                "success": False,
                "error": "Browser manager or page not available",
                "skipped": True,
            }

        try:
            self._logger("🧪 Testing stealth on bot.sannysoft.com...", "info")

            # Navigate to test page
            test_url = "https://bot.sannysoft.com/"
            result = await browser_manager.navigate_async(test_url, wait_for="body")

            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to load test page: {result['error']}",
                    "skipped": False,
                }

            # Wait for page to fully load
            await asyncio.sleep(3)

            # Extract test results
            page_content = await browser_manager.get_page_content_async()
            if not page_content:
                return {
                    "success": False,
                    "error": "Failed to get page content",
                    "skipped": False,
                }

            # Parse results using simple text analysis
            test_results = await self._parse_sannysoft_results(page_content)

            # Store results
            self.test_results = test_results

            self._logger("✅ Stealth test completed", "info")
            self._logger(f"   Detection score: {test_results.get('detection_score', 'Unknown')}", "info")
            self._logger(f"Tests passed: {test_results.get('tests_passed', 0)}/{test_results.get('total_tests', 0)}")

            return {
                "success": True,
                "results": test_results,
                "error": None,
                "skipped": False,
            }

        except Exception as e:
            self._logger(f"❌ Stealth test failed: {e}", "error")
            return {
                "success": False,
                "error": str(e),
                "skipped": False,
            }

    async def _parse_sannysoft_results(self, content: str) -> Dict[str, Any]:
        """Parse sannysoft test results from page content"""
        results = {
            "webdriver_detected": "webdriver" in content.lower(),
            "chrome_detected": "chrome" in content.lower(),
            "permissions_detected": "permissions" in content.lower(),
            "plugins_detected": "plugins" in content.lower(),
            "languages_detected": "languages" in content.lower(),
            "total_tests": 0,
            "tests_passed": 0,
            "detection_score": "Unknown",
        }

        # Count basic detection indicators
        detection_indicators = [
            results["webdriver_detected"],
            results["chrome_detected"],
            results["permissions_detected"],
            results["plugins_detected"],
            results["languages_detected"],
        ]

        results["total_tests"] = len(detection_indicators)
        results["tests_passed"] = len([x for x in detection_indicators if not x])

        # Calculate detection score
        if results["total_tests"] > 0:
            pass_rate = results["tests_passed"] / results["total_tests"]
            if pass_rate >= 0.8:
                results["detection_score"] = "Excellent"
            elif pass_rate >= 0.6:
                results["detection_score"] = "Good"
            elif pass_rate >= 0.4:
                results["detection_score"] = "Fair"
            else:
                results["detection_score"] = "Poor"

        return results

    def get_stealth_status(self) -> Dict[str, Any]:
        """Get current stealth status and test results"""
        return {
            "stealth_applied": self.stealth_applied,
            "test_results": self.test_results,
        }

    def print_stealth_status(self) -> None:
        """Print current stealth status"""
        status = self.get_stealth_status()

        self._logger("\n🥷 Stealth Status:", "info")
        self._logger(f"Applied: {status['stealth_applied']}", "info")

        if status["test_results"]:
            results = status["test_results"]
            self._logger(f"   Last test score: {results.get('detection_score', 'Unknown')}", "info")
            self._logger(f"Tests passed: {results.get('tests_passed', 0)}/{results.get('total_tests', 0)}")

    async def apply_stealth_to_context(self, context: BrowserContext) -> bool:
        """Apply stealth measures to entire browser context"""
        try:
            self._logger("🥷 Applying stealth to browser context...", "info")

            # SIMPLE OLD STYLE SCRIPT - exactly like working unrealparser!
            stealth_script = """
            if (navigator.webdriver !== undefined) {
                delete Object.getPrototypeOf(navigator).webdriver;
            }
            """

            await context.add_init_script(stealth_script)
            self._logger("✅ Context stealth script applied", "info")

            return True

        except Exception as e:
            self._logger(f"❌ Failed to apply context stealth: {e}", "error")
            return False

    async def apply_webdriver_removal(self, context) -> bool:
        """
        Remove navigator.webdriver property from context - OLD STYLE method like unrealparser

        Args:
            context: Playwright browser context

        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove navigator.webdriver property before page creation - EXACTLY like old unrealparser
            await context.add_init_script(
                """
                if (navigator.webdriver !== undefined) {
                  delete Object.getPrototypeOf(navigator).webdriver;
                }
            """
            )
            self._logger("✅ Webdriver removal script applied (OLD STYLE)", "info")
            return True
        except Exception as e:
            self._logger(f"❌ Error applying webdriver removal: {e}", "error")
            return False
