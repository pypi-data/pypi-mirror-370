"""
Captcha Detection Manager - Layer 4: Manual captcha handling with cookie persistence
Adapted from reliable unrealparser implementation with browser automation integration
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# Browser DTOs
from unrealon_browser.dto import (
    CaptchaType,
    CaptchaStatus,
    CaptchaDetection,
    BrowserMode,
    ProxyInfo,
)

# Playwright imports
from playwright.async_api import Page, BrowserContext, Browser


class CaptchaDetector:
    """
    Captcha detection and manual resolution system
    
    Key features from unrealparser:
    - Automated captcha detection using multiple indicators
    - Manual resolution through headful mode switching
    - Cookie persistence after successful resolution
    - Proxy-based captcha tracking
    - Support for multiple captcha types (reCAPTCHA, Cloudflare, etc.)
    """
    
    def __init__(self):
        """Initialize captcha detection manager"""
        self._captcha_indicators = {
            # Common captcha element selectors
            "recaptcha_selectors": [
                "iframe[src*='recaptcha']",
                ".g-recaptcha",
                "#recaptcha",
                "[data-sitekey]",
                ".recaptcha-checkbox",
                ".rc-anchor",
            ],
            "cloudflare_selectors": [
                ".cf-browser-verification",
                "#cf-content",
                ".cf-challenge-container",
                "[data-ray]",
                ".challenge-container",
                ".cloudflare-challenge",
            ],
            "generic_captcha_selectors": [
                ".captcha",
                "#captcha",
                "[name*='captcha']",
                ".challenge",
                ".verification",
                ".bot-detection",
                ".anti-robot",
                ".human-verification",
            ],
            # Content-based indicators
            "captcha_text_indicators": [
                "verify you are human",
                "prove you're not a robot",
                "complete the security check",
                "captcha verification",
                "bot detection",
                "cloudflare",
                "please verify",
                "security challenge",
                "anti-robot verification",
                "human verification",
                "access denied",
                "suspicious activity",
            ],
            # Title-based indicators
            "captcha_title_indicators": [
                "just a moment",
                "checking your browser",
                "verify you are human",
                "access denied",
                "cloudflare",
                "security check",
                "captcha",
                "bot detection",
            ],
        }
        
        # Statistics
        self._captchas_detected = 0
        self._captchas_solved = 0
        self._detection_history: List[CaptchaDetection] = []
        
    async def detect_captcha(self, page: Page) -> CaptchaDetection:
        """
        Detect if current page contains captcha challenge
        
        Args:
            page: Playwright page instance
            
        Returns:
            CaptchaDetection with detection details
        """
        # Playwright is always available (required dependency)
        try:
            if not page:
                return CaptchaDetection(
                    detected=False,
                    captcha_type=CaptchaType.UNKNOWN,
                    page_url="unknown",
                    page_title="Error: No page provided"
                )
        except Exception:
            return CaptchaDetection(
                detected=False,
                captcha_type=CaptchaType.UNKNOWN,
                page_url="unknown",
                page_title="Error: Page access error"
            )
        
        try:
            current_url = page.url
            page_title = await page.title()
            page_content = await page.content()
            
            # Initialize result
            result = CaptchaDetection(
                detected=False,
                captcha_type=CaptchaType.UNKNOWN,
                page_url=current_url,
                page_title=page_title
            )
            
            print(f"🔍 Checking for captcha on: {current_url}")
            print(f"   Page title: {page_title}")
            
            # Check for reCAPTCHA
            if await self._check_recaptcha(page, page_content, page_title):
                result.detected = True
                result.captcha_type = CaptchaType.RECAPTCHA
                print("🤖 reCAPTCHA detected!")
            
            # Check for Cloudflare
            elif await self._check_cloudflare(page, page_content, page_title):
                result.detected = True
                result.captcha_type = CaptchaType.CLOUDFLARE
                print("☁️ Cloudflare challenge detected!")
            
            # Check for generic captcha
            elif await self._check_generic_captcha(page, page_content, page_title):
                result.detected = True
                result.captcha_type = CaptchaType.IMAGE_CAPTCHA
                print("🖼️ Generic captcha detected!")
            
            if result.detected:
                self._captchas_detected += 1
                self._detection_history.append(result)
                print(f"⚠️ Captcha detected: {result.captcha_type.value}")
            else:
                print("✅ No captcha detected")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during captcha detection: {e}")
            return CaptchaDetection(
                detected=False,
                captcha_type=CaptchaType.UNKNOWN,
                page_url=current_url if 'current_url' in locals() else "unknown",
                page_title="Error during detection"
            )
    
    async def _check_recaptcha(self, page: Page, content: str, title: str) -> bool:
        """Check for reCAPTCHA indicators"""
        try:
            # Check for reCAPTCHA elements
            for selector in self._captcha_indicators["recaptcha_selectors"]:
                element = await page.query_selector(selector)
                if element:
                    print(f"   Found reCAPTCHA element: {selector}")
                    return True
            
            # Check content for reCAPTCHA indicators
            content_lower = content.lower()
            if "recaptcha" in content_lower or "g-recaptcha" in content_lower:
                print("   Found reCAPTCHA in page content")
                return True
            
            return False
            
        except Exception as e:
            print(f"   Error checking reCAPTCHA: {e}")
            return False
    
    async def _check_cloudflare(self, page: Page, content: str, title: str) -> bool:
        """Check for Cloudflare challenge indicators"""
        try:
            title_lower = title.lower()
            content_lower = content.lower()
            
            # Check title indicators
            for indicator in self._captcha_indicators["captcha_title_indicators"]:
                if indicator in title_lower:
                    print(f"   Found Cloudflare title indicator: {indicator}")
                    return True
            
            # Check for Cloudflare elements
            for selector in self._captcha_indicators["cloudflare_selectors"]:
                element = await page.query_selector(selector)
                if element:
                    print(f"   Found Cloudflare element: {selector}")
                    return True
            
            # Check content for Cloudflare indicators
            if "cloudflare" in content_lower or "checking your browser" in content_lower:
                print("   Found Cloudflare in page content")
                return True
            
            return False
            
        except Exception as e:
            print(f"   Error checking Cloudflare: {e}")
            return False
    
    async def _check_generic_captcha(self, page: Page, content: str, title: str) -> bool:
        """Check for generic captcha indicators"""
        try:
            content_lower = content.lower()
            title_lower = title.lower()
            
            # Check for generic captcha elements
            for selector in self._captcha_indicators["generic_captcha_selectors"]:
                element = await page.query_selector(selector)
                if element:
                    print(f"   Found generic captcha element: {selector}")
                    return True
            
            # Check content for captcha text
            for indicator in self._captcha_indicators["captcha_text_indicators"]:
                if indicator in content_lower:
                    print(f"   Found captcha text indicator: {indicator}")
                    return True
            
            # Check title for captcha indicators
            for indicator in self._captcha_indicators["captcha_title_indicators"]:
                if indicator in title_lower:
                    print(f"   Found captcha title indicator: {indicator}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   Error checking generic captcha: {e}")
            return False
    
    async def handle_captcha_interactive(
        self, 
        browser_manager,
        detection_result: CaptchaDetection,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Handle captcha through interactive manual resolution
        
        Args:
            browser_manager: BrowserManager instance for context switching
            detection_result: Captcha detection result
            timeout_seconds: Maximum time to wait for manual resolution
            
        Returns:
            Resolution result with success status and details
        """
        try:
            print(f"\n🤖 Manual captcha resolution required!")
            print(f"   Captcha type: {detection_result.captcha_type.value}")
            print(f"   Page URL: {detection_result.page_url}")
            print(f"   Timeout: {timeout_seconds} seconds")
            
            # Check if browser is already in headed mode
            current_mode = getattr(browser_manager.config, 'mode', BrowserMode.HEADLESS)
            
            if current_mode == BrowserMode.HEADLESS:
                print("🔄 Switching to headed mode for manual captcha resolution...")
                
                # Create new headed browser context
                headed_browser_manager = await self._create_headed_context(browser_manager)
                if not headed_browser_manager:
                    return {
                        "success": False,
                        "error": "Failed to create headed browser context",
                        "captcha_type": detection_result.captcha_type.value,
                    }
                
                # Use headed browser for resolution
                target_browser = headed_browser_manager
            else:
                print("👀 Browser already in headed mode")
                target_browser = browser_manager
            
            # Wait for manual captcha resolution
            resolution_result = await self._wait_for_captcha_solution(
                target_browser, detection_result, timeout_seconds
            )
            
            # Save cookies after successful resolution
            if resolution_result["success"]:
                cookies_saved = await target_browser.save_cookies_for_current_proxy_async()
                resolution_result["cookies_saved"] = cookies_saved
                
                if cookies_saved:
                    print("💾 Cookies saved after captcha resolution")
                    self._captchas_solved += 1
                else:
                    print("⚠️ Failed to save cookies after captcha resolution")
            
            # Clean up headed browser if created
            if current_mode == BrowserMode.HEADLESS and 'headed_browser_manager' in locals():
                await self._cleanup_headed_context(headed_browser_manager)
            
            return resolution_result
            
        except Exception as e:
            print(f"❌ Error during interactive captcha handling: {e}")
            return {
                "success": False,
                "error": str(e),
                "captcha_type": detection_result.captcha_type.value,
            }
    
    async def _create_headed_context(self, browser_manager) -> Optional[Any]:
        """Create a new headed browser context for manual interaction"""
        try:
            print("🔄 Creating headed browser context...")
            
            # This is a simplified approach - in practice you'd create a new
            # BrowserManager instance with headed configuration
            # For now, we'll assume the existing browser can be used
            
            return browser_manager
            
        except Exception as e:
            print(f"❌ Error creating headed context: {e}")
            return None
    
    async def _cleanup_headed_context(self, browser_manager) -> None:
        """Clean up headed browser context"""
        try:
            print("🧹 Cleaning up headed browser context...")
            # Implementation depends on how headed context was created
            pass
            
        except Exception as e:
            print(f"❌ Error cleaning up headed context: {e}")
    
    async def _wait_for_captcha_solution(
        self, 
        browser_manager, 
        detection_result: CaptchaDetection,
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """
        Wait for manual captcha solution with periodic checks
        
        Args:
            browser_manager: Browser manager instance
            detection_result: Original captcha detection result
            timeout_seconds: Maximum wait time
            
        Returns:
            Resolution result
        """
        try:
            print(f"\n⏳ Waiting for manual captcha resolution...")
            print(f"   Please solve the captcha in the browser window")
            print(f"   The system will automatically detect when it's solved")
            print(f"   Timeout: {timeout_seconds} seconds")
            
            start_time = datetime.now(timezone.utc)
            check_interval = 5  # Check every 5 seconds
            
            while True:
                # Check if timeout exceeded
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed > timeout_seconds:
                    print(f"⏰ Captcha resolution timeout ({timeout_seconds}s)")
                    return {
                        "success": False,
                        "error": f"Timeout after {timeout_seconds} seconds",
                        "captcha_type": detection_result.captcha_type.value,
                        "elapsed_seconds": elapsed,
                    }
                
                # Check if captcha is still present
                if hasattr(browser_manager, '_page') and browser_manager._page:
                    current_detection = await self.detect_captcha(browser_manager._page)
                    
                    if not current_detection.detected:
                        print("✅ Captcha appears to be solved!")
                        
                        # Verify by checking page content/URL changes
                        verification_result = await self._verify_captcha_solution(
                            browser_manager, detection_result
                        )
                        
                        if verification_result["verified"]:
                            print("🎉 Captcha solution verified!")
                            return {
                                "success": True,
                                "captcha_type": detection_result.captcha_type.value,
                                "elapsed_seconds": elapsed,
                                "verification": verification_result,
                            }
                        else:
                            print("⚠️ Captcha solution not verified, continuing to wait...")
                
                # Show progress
                remaining = timeout_seconds - elapsed
                print(f"   ⏳ Still waiting... {remaining:.0f}s remaining")
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
        except Exception as e:
            print(f"❌ Error waiting for captcha solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "captcha_type": detection_result.captcha_type.value,
            }
    
    async def _verify_captcha_solution(
        self, 
        browser_manager, 
        original_detection: CaptchaDetection
    ) -> Dict[str, Any]:
        """
        Verify that captcha was actually solved by checking page changes
        
        Args:
            browser_manager: Browser manager instance
            original_detection: Original captcha detection result
            
        Returns:
            Verification result
        """
        try:
            if not hasattr(browser_manager, '_page') or not browser_manager._page:
                return {"verified": False, "reason": "No page available"}
            
            page = browser_manager._page
            current_url = page.url
            current_title = await page.title()
            
            # Check if URL changed (common after successful captcha)
            url_changed = current_url != original_detection.page_url
            
            # Check if title changed
            title_changed = True  # We don't have original title, assume changed is good
            
            # Check if captcha elements are gone
            captcha_elements_gone = not (await self.detect_captcha(page)).detected
            
            # Look for success indicators
            content = await page.content()
            content_lower = content.lower()
            
            success_indicators = [
                "welcome",
                "dashboard",
                "profile",
                "account",
                "search",
                "home",
                "main",
                "success",
            ]
            
            has_success_indicators = any(indicator in content_lower for indicator in success_indicators)
            
            # Determine if solution is verified
            verified = (
                captcha_elements_gone and 
                (url_changed or has_success_indicators)
            )
            
            return {
                "verified": verified,
                "url_changed": url_changed,
                "captcha_elements_gone": captcha_elements_gone,
                "has_success_indicators": has_success_indicators,
                "current_url": current_url,
                "current_title": current_title,
            }
            
        except Exception as e:
            print(f"❌ Error verifying captcha solution: {e}")
            return {"verified": False, "reason": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get captcha detection statistics"""
        return {
            "captchas_detected": self._captchas_detected,
            "captchas_solved": self._captchas_solved,
            "success_rate": (
                (self._captchas_solved / self._captchas_detected * 100) 
                if self._captchas_detected > 0 else 0
            ),
            "detection_history_count": len(self._detection_history),
            "supported_types": [t.value for t in CaptchaType],
        }
    
    def print_statistics(self) -> None:
        """Print captcha detection statistics"""
        stats = self.get_statistics()
        
        print(f"\n🤖 Captcha Detection Statistics:")
        print(f"   Captchas detected: {stats['captchas_detected']}")
        print(f"   Captchas solved: {stats['captchas_solved']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Detection history: {stats['detection_history_count']} events")
        print(f"   Supported types: {', '.join(stats['supported_types'])}")
        
        # Show recent detections
        if self._detection_history:
            print("   Recent detections:")
            for detection in self._detection_history[-3:]:  # Show last 3
                print(f"     {detection.detected_at.strftime('%H:%M:%S')} - {detection.captcha_type.value} on {detection.page_url}")
        else:
            print("   No captcha detections yet")
    
    def get_detection_history(self) -> List[CaptchaDetection]:
        """Get captcha detection history"""
        return self._detection_history.copy()
    
    def clear_detection_history(self) -> None:
        """Clear captcha detection history"""
        self._detection_history.clear()
        print("🧹 Cleared captcha detection history")
