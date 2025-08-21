"""
Smart HTML Cleaner - Intelligent HTML cleaning for LLM optimization.

Intelligent HTML cleaning that removes noise but preserves useful data.
Optimizes HTML for LLM token efficiency while keeping valuable content.
"""

import json
import re
import asyncio
import concurrent.futures
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field, ConfigDict

from bs4 import BeautifulSoup, Comment
from unrealon_driver.smart_logging import create_smart_logger

from .config import HTMLCleaningConfig


class HTMLCleaningStats(BaseModel):
    """HTML cleaning statistics"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    original_size_bytes: int = Field(ge=0)
    cleaned_size_bytes: int = Field(ge=0)
    size_reduction_bytes: int = Field(ge=0)
    size_reduction_percent: float = Field(ge=0.0, le=100.0)
    estimated_original_tokens: int = Field(ge=0)
    estimated_cleaned_tokens: int = Field(ge=0)
    estimated_token_savings: int = Field(ge=0)
    estimated_token_savings_percent: float = Field(ge=0.0, le=100.0)


class ExtractedJSData(BaseModel):
    """Extracted JavaScript data structure"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    ssr_data: Dict[str, Any] = Field(default_factory=dict)
    structured_data: List[Dict[str, Any]] = Field(default_factory=list)
    analytics_data: Dict[str, Any] = Field(default_factory=dict)
    product_data: Dict[str, Any] = Field(default_factory=dict)
    raw_extracts: List[Dict[str, Any]] = Field(default_factory=list)


class HTMLCleaningError(Exception):
    """Raised when HTML cleaning fails"""

    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class HTMLCleaner:
    """
    🧹 Smart HTML Cleaner - Intelligent HTML cleaning for LLM optimization

    Features:
    - Removes noise (scripts, styles, comments)
    - Preserves useful JavaScript data (JSON objects, SSR data)
    - Cleans whitespace and formatting
    - Maintains semantic structure
    - Extracts and preserves Next.js/Nuxt.js SSR data
    - Optimizes for LLM token efficiency
    """

    def __init__(self, parser_id: str, config: Optional[HTMLCleaningConfig] = None):
        self.config = config or HTMLCleaningConfig()

        # Initialize smart logger
        self.parser_id = parser_id
        self.logger = create_smart_logger(parser_id=self.parser_id)

        # Tags to completely remove
        self.noise_tags = {"script", "style", "meta", "link", "base", "title", "head", "noscript", "iframe", "embed", "object", "svg", "canvas", "audio", "video", "source", "track", "area", "map", "param"}

        # Add conditional tags based on config
        if not self.config.preserve_forms:
            self.noise_tags.update({"form", "input", "button", "select", "textarea", "fieldset", "legend"})

        # Universal noise selectors to remove (for any site)
        self.universal_noise_selectors = [
            '[id*="nav"]',
            '[class*="nav"]',  # Navigation
            '[id*="menu"]',
            '[class*="menu"]',  # Menus
            '[id*="sidebar"]',
            '[class*="sidebar"]',  # Sidebars
            '[id*="footer"]',
            '[class*="footer"]',  # Footers
            '[id*="header"]',
            '[class*="header"]',  # Headers
            '[class*="ads"]',
            '[class*="advertisement"]',  # Ads
            '[class*="sponsored"]',
            '[class*="promo"]',  # Sponsored content
            '[class*="popup"]',
            '[class*="modal"]',  # Popups/modals
            '[class*="overlay"]',
            '[class*="tooltip"]',  # Overlays
            '[class*="cookie"]',
            '[class*="gdpr"]',  # Cookie notices
            '[class*="newsletter"]',
            '[class*="subscription"]',  # Email signup
            '[class*="social"]',
            '[class*="share"]',  # Social media
            '[class*="comment"]',
            '[class*="discussion"]',  # Comments
            '[class*="tracking"]',
            '[class*="analytics"]',  # Tracking
        ]

        # Attributes to keep (semantic ones)
        self.keep_attributes = {"id", "class", "data-testid", "data-test", "data-cy", "aria-label", "aria-labelledby", "aria-describedby", "role", "alt", "title", "href", "src", "action", "name", "value", "placeholder", "type"}

        # Compile regex patterns for performance
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance"""
        # URL patterns to remove or shorten (for tracking/analytics)
        self.tracking_url_patterns = [
            r'https://aax-[^\s"]{200,}',  # Amazon tracking URLs over 200 chars
            r'https://[^\s"]*tracking[^\s"]{100,}',  # General tracking URLs
            r'https://[^\s"]*analytics[^\s"]{100,}',  # Analytics URLs
            r'https://[^\s"]*gtm[^\s"]{100,}',  # Google Tag Manager URLs
        ]

        # Base64 patterns to remove or replace
        self.base64_patterns = [
            r"data:image/[^;]+;base64,[A-Za-z0-9+/=]{50,}",  # Base64 images over 50 chars
            r"data:application/[^;]+;base64,[A-Za-z0-9+/=]{100,}",  # Base64 applications
            r"data:text/[^;]+;base64,[A-Za-z0-9+/=]{100,}",  # Base64 text
        ]

        # Patterns to detect valuable JavaScript data
        self.useful_js_patterns = [
            # Next.js/Nuxt.js SSR data
            r"__NEXT_DATA__\s*=\s*(\{.+?\});?",
            r"__NUXT__\s*=\s*(\{.+?\});?",
            r"window\.__INITIAL_STATE__\s*=\s*(\{.+?\});?",
            # React/Vue hydration data
            r"window\.__REACT_QUERY_STATE__\s*=\s*(\{.+?\});?",
            r"window\.__VUE_SSR_CONTEXT__\s*=\s*(\{.+?\});?",
            # E-commerce data
            r"window\.productData\s*=\s*(\{.+?\});?",
            r"window\.cartData\s*=\s*(\{.+?\});?",
            r"dataLayer\s*=\s*(\[.+?\]);?",
            # Analytics and tracking (structured data)
            r'gtag\s*\(\s*[\'"]config[\'"],\s*[\'"][^\'\"]+[\'"],\s*(\{.+?\})\s*\);?',
            # JSON-LD structured data (often in script tags)
            r'"@context"\s*:\s*"https?://schema\.org"[^}]*\}',
            # Generic JSON objects (be more selective)
            r"(?:window\.|var\s+|let\s+|const\s+)\w+\s*=\s*(\{.+?\});?",
        ]

        # Compiled regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.DOTALL | re.IGNORECASE) for pattern in self.useful_js_patterns]

    # ==========================================
    # MAIN CLEANING METHODS
    # ==========================================

    async def clean_html(self, html_content: str, preserve_js_data: bool = True, aggressive_cleaning: bool = False) -> Tuple[str, Dict[str, Any]]:
        """
        Clean HTML content while preserving valuable data

        Args:
            html_content: Raw HTML content
            preserve_js_data: Whether to extract and preserve JS data
            aggressive_cleaning: Whether to apply more aggressive cleaning

        Returns:
            Tuple of (cleaned_html, extracted_data)
        """
        if not html_content or not html_content.strip():
            return "", {}

        try:
            self.logger.info(f"🧹 Cleaning HTML: {len(html_content)} characters")

            # Check size limits
            if len(html_content) > self.config.max_html_size:
                self.logger.warning(f"⚠️ HTML size ({len(html_content)}) exceeds limit ({self.config.max_html_size}), truncating")
                html_content = html_content[: self.config.max_html_size]

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            extracted_data = {}

            # Extract valuable JavaScript data before removing scripts
            if preserve_js_data:
                extracted_data = self._extract_js_data(soup)

            # Remove universal noise elements for aggressive cleaning
            if aggressive_cleaning:
                self._remove_universal_noise(soup)
                self._truncate_long_urls(soup)  # Do this before tracking URL cleaning
                self._clean_tracking_urls(soup)
                self._clean_base64_data(soup)
                self._remove_long_attributes(soup)
                self._remove_html_comments(soup)
                self._clean_whitespace(soup)

            # Remove noise elements
            self._remove_noise_elements(soup)

            # Clean attributes
            self._clean_attributes(soup, aggressive_cleaning)

            # Remove comments
            self._remove_comments(soup)

            # Clean text and whitespace
            cleaned_html = self._clean_text_and_whitespace(soup)

            # Final cleanup
            cleaned_html = self._final_cleanup(cleaned_html)

            # Log results
            original_size = len(html_content)
            cleaned_size = len(cleaned_html)
            reduction = ((original_size - cleaned_size) / original_size * 100) if original_size > 0 else 0

            self.logger.info(f"✅ HTML cleaned: {original_size} → {cleaned_size} chars " f"({reduction:.1f}% reduction)")

            return cleaned_html, extracted_data

        except Exception as e:
            self.logger.error(f"❌ HTML cleaning failed: {e}")
            raise HTMLCleaningError(message=f"Failed to clean HTML: {e}", operation="clean_html", details={"html_size": str(len(html_content))}) from e

    def clean_html_sync(self, html_content: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Synchronous HTML cleaning

        Args:
            html_content: Raw HTML content
            **kwargs: Cleaning options

        Returns:
            Tuple of (cleaned_html, extracted_data)
        """
        # Handle running event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a new thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.clean_html(html_content, **kwargs))
                return future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            return asyncio.run(self.clean_html(html_content, **kwargs))

    # ==========================================
    # CLEANING IMPLEMENTATION
    # ==========================================

    def _standard_cleaning(self, soup: BeautifulSoup) -> None:
        """Apply standard cleaning"""
        # Remove noise elements
        self._remove_noise_elements(soup)

        # Clean attributes
        self._clean_attributes(soup)

        # Remove comments
        if self.config.remove_comments:
            self._remove_comments(soup)

        # Normalize whitespace
        if self.config.normalize_whitespace:
            self._normalize_whitespace(soup)

    def _aggressive_cleaning(self, soup: BeautifulSoup) -> None:
        """Apply aggressive cleaning"""
        # Standard cleaning first
        self._standard_cleaning(soup)

        # Remove noise selectors
        self._remove_noise_selectors(soup)

        # Clean tracking URLs
        if self.config.remove_tracking:
            self._clean_tracking_urls(soup)

        # Clean base64 data
        self._clean_base64_data(soup)

        # Truncate long URLs
        self._truncate_long_urls(soup)

        # Remove long attributes
        self._remove_long_attributes(soup)

        # Truncate long text
        self._truncate_long_text(soup)

    def _remove_noise_elements(self, soup: BeautifulSoup) -> None:
        """Remove noise HTML elements"""
        # Define noise tags
        noise_tags = {"meta", "link", "base", "title", "head", "noscript", "iframe", "embed", "object", "svg", "canvas", "audio", "video", "source", "track", "area", "map", "param"}

        # Add conditional tags
        if self.config.remove_scripts:
            noise_tags.add("script")
        if self.config.remove_styles:
            noise_tags.add("style")
        if not self.config.preserve_forms:
            noise_tags.update({"form", "input", "button", "select", "textarea", "fieldset", "legend"})

        # Remove noise tags
        for tag_name in noise_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove empty elements
        if self.config.remove_empty_elements:
            for tag in soup.find_all(["div", "span", "p"]):
                if not tag.get_text(strip=True) and not tag.find_all():
                    tag.decompose()

    def _remove_noise_selectors(self, soup: BeautifulSoup) -> None:
        """Remove elements matching noise selectors"""
        for selector in self.config.noise_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    element.decompose()
            except Exception:
                # Skip invalid selectors
                continue

    def _clean_attributes(self, soup: BeautifulSoup) -> None:
        """Clean HTML attributes"""
        # Attributes to remove
        noise_attributes = {
            "style",
            "onclick",
            "onload",
            "onchange",
            "onmouseover",
            "onmouseout",
            "onfocus",
            "onblur",
            "onsubmit",
            "onreset",
            "onerror",
            "onabort",
            "autocomplete",
            "autofocus",
            "checked",
            "defer",
            "disabled",
            "hidden",
            "loop",
            "multiple",
            "muted",
            "open",
            "readonly",
            "required",
            "tabindex",
            "translate",
            "draggable",
            "contenteditable",
        }

        # Attributes to keep
        keep_attributes = {"id", "class", "href", "src", "alt", "title", "data-testid", "data-test", "data-cy", "aria-label", "aria-labelledby", "aria-describedby", "role"}

        for tag in soup.find_all(True):
            if hasattr(tag, "attrs"):
                # Remove unwanted attributes
                attrs_to_remove = set(tag.attrs.keys()) - keep_attributes
                for attr in attrs_to_remove:
                    if attr in noise_attributes:
                        del tag.attrs[attr]

    def _clean_tracking_urls(self, soup: BeautifulSoup) -> None:
        """Remove or replace tracking URLs"""
        # Clean href attributes
        for tag in soup.find_all(["a"], href=True):
            href = tag.get("href", "")
            if href:
                for pattern in self.tracking_url_patterns:
                    if pattern.match(href):
                        tag["href"] = "#tracking-url-removed"
                        break

        # Clean src attributes
        for tag in soup.find_all(["img"], src=True):
            src = tag.get("src", "")
            if src:
                for pattern in self.tracking_url_patterns:
                    if pattern.match(src):
                        tag["src"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        break

    def _clean_base64_data(self, soup: BeautifulSoup) -> None:
        """Remove large base64 encoded data"""
        for tag in soup.find_all(["img"], src=True):
            src = tag.get("src", "")
            if src:
                for pattern in self.base64_patterns:
                    if pattern.search(src):
                        tag["src"] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        break

    def _truncate_long_urls(self, soup: BeautifulSoup) -> None:
        """Truncate URLs longer than max_url_length"""
        max_length = self.config.max_url_length

        for tag in soup.find_all(["a"], href=True):
            href = tag.get("href", "")
            if isinstance(href, str) and len(href) > max_length:
                tag["href"] = href[:max_length] + "...truncated"

        for tag in soup.find_all(["img"], src=True):
            src = tag.get("src", "")
            if isinstance(src, str) and len(src) > max_length and not src.startswith("data:"):
                tag["src"] = src[:max_length] + "...truncated"

    def _remove_long_attributes(self, soup: BeautifulSoup) -> None:
        """Remove attributes with extremely long values"""
        for tag in soup.find_all():
            attrs_to_remove = []
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and len(value) > 800:
                    attrs_to_remove.append(attr)
                elif any(tracking in attr.lower() for tracking in ["tracking", "analytics", "gtm", "pixel"]):
                    attrs_to_remove.append(attr)

            for attr in attrs_to_remove:
                del tag.attrs[attr]

    def _truncate_long_text(self, soup: BeautifulSoup) -> None:
        """Truncate text content longer than max_text_length"""
        max_length = self.config.max_text_length

        for element in soup.find_all(text=True):
            if element.parent.name not in ["script", "style"]:
                text_content = str(element).strip()
                if text_content and len(text_content) > max_length:
                    truncated_text = text_content[:max_length] + "..."
                    element.replace_with(truncated_text)

    def _remove_comments(self, soup: BeautifulSoup) -> None:
        """Remove HTML comments"""
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

    def _normalize_whitespace(self, soup: BeautifulSoup) -> None:
        """Normalize whitespace in text content"""
        for element in soup.find_all(text=True):
            if element.parent.name not in ["script", "style"]:
                # Replace multiple spaces with single space
                cleaned_text = re.sub(r" {3,}", "  ", str(element))
                # Replace multiple newlines with maximum 2
                cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
                # Replace multiple tabs with single space
                cleaned_text = re.sub(r"\t+", " ", cleaned_text)
                element.replace_with(cleaned_text)

    def _final_cleanup(self, html: str) -> str:
        """Final cleanup and optimization"""
        # Remove empty attributes
        html = re.sub(r'\s+\w+=""', "", html)

        # Remove extra spaces in attributes
        html = re.sub(r'(\w+)=\s*"([^"]*)"', r'\1="\2"', html)

        # Normalize quotes
        html = re.sub(r"(\w+)='([^']*)'", r'\1="\2"', html)

        # Remove trailing spaces before closing tags
        html = re.sub(r"\s+(/?>)", r"\1", html)

        # Advanced whitespace cleanup
        html = self._advanced_whitespace_cleanup(html)

        return html.strip()

    def _advanced_whitespace_cleanup(self, html: str) -> str:
        """Advanced whitespace cleanup"""
        # Remove excessive spaces
        html = re.sub(r" {3,}", "  ", html)

        # Remove excessive newlines
        html = re.sub(r"\n{3,}", "\n\n", html)

        # Clean space between tags
        html = re.sub(r">\s{2,}<", "> <", html)

        return html

    # ==========================================
    # JAVASCRIPT DATA EXTRACTION
    # ==========================================

    def _extract_js_data(self, soup: BeautifulSoup) -> ExtractedJSData:
        """Extract valuable JavaScript data"""
        extracted_data = ExtractedJSData()

        # Find all script tags
        script_tags = soup.find_all("script")

        for script in script_tags:
            if not script.string:
                continue

            script_content = script.string.strip()

            # Skip empty scripts
            if len(script_content) < 10:
                continue

            # Check for JSON-LD structured data
            if script.get("type") == "application/ld+json":
                try:
                    json_data = json.loads(script_content)
                    # Convert to string dict for Pydantic compliance
                    str_data = {str(k): str(v) for k, v in json_data.items() if isinstance(k, (str, int, float))}
                    extracted_data.structured_data.append(str_data)
                    continue
                except json.JSONDecodeError:
                    pass

            # Extract data using patterns
            self._extract_with_patterns(script_content, extracted_data)

        return extracted_data

    def _extract_with_patterns(self, script_content: str, extracted_data: ExtractedJSData) -> None:
        """Extract data using compiled regex patterns"""
        for pattern in self.js_data_patterns:
            matches = pattern.finditer(script_content)
            for match in matches:
                self._try_parse_json(match.group(1), extracted_data)

    def _try_parse_json(self, json_str: str, extracted_data: ExtractedJSData) -> None:
        """Try to parse JSON string and add to extracted data"""
        try:
            json_data = json.loads(json_str)

            if isinstance(json_data, dict):
                # Convert to string dict for Pydantic compliance
                str_data = {}
                for k, v in json_data.items():
                    if isinstance(k, (str, int, float)) and isinstance(v, (str, int, float, bool)):
                        str_data[str(k)] = str(v)

                if str_data:
                    extracted_data.ssr_data.update(str_data)

        except json.JSONDecodeError:
            # Skip invalid JSON
            pass

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def get_cleaning_stats(self, original_html: str, cleaned_html: str) -> HTMLCleaningStats:
        """Get statistics about the cleaning process"""
        original_size = len(original_html)
        cleaned_size = len(cleaned_html)

        # Estimate token reduction (rough approximation)
        original_tokens = original_size // 4  # Rough estimate: 4 chars per token
        cleaned_tokens = cleaned_size // 4

        size_reduction = original_size - cleaned_size
        size_reduction_percent = (size_reduction / original_size * 100) if original_size > 0 else 0.0
        token_savings = original_tokens - cleaned_tokens
        token_savings_percent = (token_savings / original_tokens * 100) if original_tokens > 0 else 0.0

        return HTMLCleaningStats(
            original_size_bytes=original_size,
            cleaned_size_bytes=cleaned_size,
            size_reduction_bytes=size_reduction,
            size_reduction_percent=size_reduction_percent,
            estimated_original_tokens=original_tokens,
            estimated_cleaned_tokens=cleaned_tokens,
            estimated_token_savings=token_savings,
            estimated_token_savings_percent=token_savings_percent,
        )

    def update_config(self, **kwargs) -> None:
        """Update configuration with new values"""
        current_data = self.config.model_dump()
        current_data.update(kwargs)
        self.config = HTMLCleaningConfig.model_validate(current_data)

        # Recompile patterns if needed
        self._compile_patterns()


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================


def create_html_cleaner(parser_id: str, config: Optional[HTMLCleaningConfig] = None) -> HTMLCleaner:
    """
    Create an HTML cleaner instance

    Args:
        config: Optional HTML cleaning configuration
        parser_id: Parser identifier for logging

    Returns:
        Configured HTMLCleaner instance
    """
    return HTMLCleaner(parser_id=parser_id, config=config)


async def quick_clean_html(html: str, parser_id: str, **kwargs) -> str:
    """
    Quick HTML cleaning convenience function

    Args:
        html: Raw HTML content
        parser_id: Parser identifier for logging
        **kwargs: Cleaning options

    Returns:
        Cleaned HTML
    """
    config_data = {k: v for k, v in kwargs.items() if k in HTMLCleaningConfig.model_fields}
    config = HTMLCleaningConfig.model_validate(config_data) if config_data else None

    cleaner = create_html_cleaner(parser_id, config)
    return await cleaner.clean_html(html, **kwargs)


def quick_clean_html_sync(html: str, parser_id: str, **kwargs) -> str:
    """
    Quick synchronous HTML cleaning convenience function

    Args:
        html: Raw HTML content
        parser_id: Parser identifier for logging
        **kwargs: Cleaning options

    Returns:
        Cleaned HTML
    """
    config_data = {k: v for k, v in kwargs.items() if k in HTMLCleaningConfig.model_fields}
    config = HTMLCleaningConfig.model_validate(config_data) if config_data else None

    cleaner = create_html_cleaner(parser_id, config)
    return cleaner.clean_html_sync(html, **kwargs)
