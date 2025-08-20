"""
Stealth Manager - Anti-detection system for browser automation
Layer 1: Advanced stealth capabilities inspired by unrealparser
"""

import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import Page, BrowserContext

# CRITICAL REQUIREMENTS COMPLIANCE - NO INLINE IMPORTS!
from playwright_stealth import stealth_async, StealthConfig


class StealthManager:
    """
    Advanced anti-detection system for browser automation

    Layer 1: Stealth capabilities
    - Playwright-stealth integration
    - WebDriver property removal
    - Bot detection testing
    - Stealth arguments optimization
    """

    def __init__(self):
        """Initialize stealth manager"""
        self.stealth_applied = False
        self.test_results: Optional[Dict[str, Any]] = None

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

    async def apply_stealth(self, page: Page) -> bool:
        """
        Apply stealth measures to page
        Combines multiple anti-detection techniques
        """
        try:
            print("🥷 Applying stealth measures...")

            # 1. Apply playwright-stealth if available
            stealth_applied = await self._apply_playwright_stealth(page)

            # 2. Remove webdriver property
            await self._remove_webdriver_property(page)

            # 3. Apply additional stealth scripts
            await self._apply_custom_stealth_scripts(page)

            # 4. Set realistic properties
            await self._set_realistic_properties(page)

            self.stealth_applied = True
            print("✅ Stealth measures applied successfully")

            return True

        except Exception as e:
            print(f"❌ Failed to apply stealth measures: {e}")
            self.stealth_applied = False
            return False

    async def _apply_playwright_stealth(self, page: Page) -> bool:
        """Apply playwright-stealth with custom config"""
        try:
            # 🔥 WEBDRIVER ONLY CONFIG: Only remove webdriver, nothing else!
            config = StealthConfig(
                webdriver=True,  # ONLY webdriver removal
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
                outerdimensions=False,  # DISABLE
                hairline=False,  # DISABLE
            )

            await stealth_async(page, config)
            print("   ✅ Playwright-stealth applied with CUSTOM config")
            return True
        except Exception as e:
            print(f"   ❌ playwright-stealth failed: {e}")
            return False

    async def _remove_webdriver_property(self, page: Page) -> None:
        """Remove navigator.webdriver property - HANDLED BY PLAYWRIGHT-STEALTH"""
        # 🔥 REDUNDANT: playwright-stealth already does this with webdriver=True
        print("   ✅ WebDriver property removal handled by playwright-stealth")

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

        print("   ✅ Custom stealth scripts applied")

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
        print("   ✅ Realistic properties set")

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
            print("🧪 Testing stealth on bot.sannysoft.com...")

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

            print("✅ Stealth test completed")
            print(f"   Detection score: {test_results.get('detection_score', 'Unknown')}")
            print(
                f"   Tests passed: {test_results.get('tests_passed', 0)}/{test_results.get('total_tests', 0)}"
            )

            return {
                "success": True,
                "results": test_results,
                "error": None,
                "skipped": False,
            }

        except Exception as e:
            print(f"❌ Stealth test failed: {e}")
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
            "playwright_stealth_available": self._check_playwright_stealth_available(),
        }

    def _check_playwright_stealth_available(self) -> bool:
        """Check if playwright-stealth is available"""
        try:
            import playwright_stealth

            return True
        except ImportError:
            return False

    def print_stealth_status(self) -> None:
        """Print current stealth status"""
        status = self.get_stealth_status()

        print("\n🥷 Stealth Status:")
        print(f"   Applied: {status['stealth_applied']}")
        print(f"   Playwright-stealth: {status['playwright_stealth_available']}")

        if status["test_results"]:
            results = status["test_results"]
            print(f"   Last test score: {results.get('detection_score', 'Unknown')}")
            print(
                f"   Tests passed: {results.get('tests_passed', 0)}/{results.get('total_tests', 0)}"
            )

    async def apply_stealth_to_context(self, context: BrowserContext) -> bool:
        """Apply stealth measures to entire browser context"""
        try:
            print("🥷 Applying stealth to browser context...")

            # SIMPLE OLD STYLE SCRIPT - exactly like working unrealparser!
            stealth_script = """
            if (navigator.webdriver !== undefined) {
                delete Object.getPrototypeOf(navigator).webdriver;
            }
            """

            await context.add_init_script(stealth_script)
            print("   ✅ Context stealth script applied")

            return True

        except Exception as e:
            print(f"   ❌ Failed to apply context stealth: {e}")
            return False

    def apply_webdriver_removal(self, context) -> bool:
        """
        Remove navigator.webdriver property from context - OLD STYLE method like unrealparser

        Args:
            context: Playwright browser context

        Returns:
            True if successful, False otherwise
        """
        try:
            # Надёжно удаляем navigator.webdriver до создания страницы - EXACTLY like old unrealparser
            context.add_init_script(
                """
                if (navigator.webdriver !== undefined) {
                  delete Object.getPrototypeOf(navigator).webdriver;
                }
            """
            )
            print("✅ Webdriver removal script applied (OLD STYLE)")
            return True
        except Exception as e:
            print(f"❌ Error applying webdriver removal: {e}")
            return False
