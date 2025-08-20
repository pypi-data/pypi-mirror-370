"""
HTML Manager - Smart HTML processing and cleaning with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- Custom exception hierarchy
"""

import json
import re
from typing import Optional, List, Union
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, field_validator
import asyncio
import concurrent.futures

from bs4 import BeautifulSoup, Comment

from unrealon_rpc.logging import get_logger


class HTMLCleaningConfig(BaseModel):
    """HTML cleaning configuration with strict typing"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    # Cleaning modes
    aggressive_cleaning: bool = Field(
        default=True,
        description="Enable aggressive cleaning"
    )
    preserve_js_data: bool = Field(
        default=True,
        description="Preserve JavaScript data during cleaning"
    )
    
    # Content preservation
    preserve_images: bool = Field(
        default=False,
        description="Preserve image tags"
    )
    preserve_links: bool = Field(
        default=True,
        description="Preserve link tags"
    )
    preserve_forms: bool = Field(
        default=False,
        description="Preserve form elements"
    )
    
    # Size limits
    max_html_size: int = Field(
        default=1000000,
        ge=1000,
        le=10000000,
        description="Maximum HTML size in characters"
    )
    max_text_length: int = Field(
        default=300,
        ge=50,
        le=1000,
        description="Maximum text content length per element"
    )
    max_url_length: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Maximum URL length"
    )
    
    # Noise removal
    remove_comments: bool = Field(
        default=True,
        description="Remove HTML comments"
    )
    remove_scripts: bool = Field(
        default=True,
        description="Remove script tags"
    )
    remove_styles: bool = Field(
        default=True,
        description="Remove style tags"
    )
    remove_tracking: bool = Field(
        default=True,
        description="Remove tracking URLs and attributes"
    )
    
    # Whitespace handling
    normalize_whitespace: bool = Field(
        default=True,
        description="Normalize whitespace"
    )
    remove_empty_elements: bool = Field(
        default=True,
        description="Remove empty elements"
    )
    
    # Custom selectors
    noise_selectors: List[str] = Field(
        default_factory=lambda: [
            '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
            '[class*="footer"]', '[class*="header"]', '[class*="ads"]',
            '[class*="popup"]', '[class*="modal"]', '[class*="cookie"]'
        ],
        description="CSS selectors for noise elements to remove"
    )


class HTMLCleaningStats(BaseModel):
    """HTML cleaning statistics"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
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
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    ssr_data: dict[str, str] = Field(default_factory=dict)
    structured_data: List[dict[str, str]] = Field(default_factory=list)
    raw_extracts: List[dict[str, str]] = Field(default_factory=list)


class HTMLManagerError(Exception):
    """Base exception for HTML manager"""
    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class HTMLParsingError(HTMLManagerError):
    """Raised when HTML parsing fails"""
    pass


class HTMLCleaningError(HTMLManagerError):
    """Raised when HTML cleaning fails"""
    pass


class HTMLManager:
    """
    🧹 HTML Manager - Smart HTML processing and cleaning
    
    Features:
    - LLM Optimized: Removes noise, preserves valuable content
    - Token Efficient: Reduces HTML size for cost-effective LLM analysis
    - Smart Extraction: Preserves JavaScript data and structured content
    - Performance: Fast cleaning with configurable aggressiveness
    - Safe: Handles malformed HTML gracefully
    - Type Safety: Full Pydantic v2 compliance
    """
    
    def __init__(self, config: Optional[HTMLCleaningConfig] = None):
        self.config = config or HTMLCleaningConfig()
        self.logger = get_logger()
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance"""
        # Tracking URL patterns
        self.tracking_url_patterns = [
            re.compile(r'https://aax-[^\s"]{200,}', re.IGNORECASE),
            re.compile(r'https://[^\s"]*tracking[^\s"]{100,}', re.IGNORECASE),
            re.compile(r'https://[^\s"]*analytics[^\s"]{100,}', re.IGNORECASE),
            re.compile(r'https://[^\s"]*gtm[^\s"]{100,}', re.IGNORECASE),
        ]
        
        # Base64 patterns
        self.base64_patterns = [
            re.compile(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]{50,}'),
            re.compile(r'data:application/[^;]+;base64,[A-Za-z0-9+/=]{100,}'),
            re.compile(r'data:text/[^;]+;base64,[A-Za-z0-9+/=]{100,}'),
        ]
        
        # JavaScript data patterns
        self.js_data_patterns = [
            re.compile(r'__NEXT_DATA__\s*=\s*(\{.+?\});?', re.DOTALL | re.IGNORECASE),
            re.compile(r'__NUXT__\s*=\s*(\{.+?\});?', re.DOTALL | re.IGNORECASE),
            re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\});?', re.DOTALL | re.IGNORECASE),
            re.compile(r'dataLayer\s*=\s*(\[.+?\]);?', re.DOTALL | re.IGNORECASE),
        ]
    
    # ==========================================
    # MAIN CLEANING METHODS
    # ==========================================
    
    async def clean_html(
        self,
        html: str,
        aggressive: Optional[bool] = None,
        preserve_js_data: Optional[bool] = None
    ) -> str:
        """
        Clean HTML content for LLM analysis
        
        Args:
            html: Raw HTML content
            aggressive: Override aggressive cleaning setting
            preserve_js_data: Override JS data preservation setting
            
        Returns:
            Cleaned HTML optimized for LLM
        """
        if not html or not html.strip():
            return ""
        
        # Use config defaults or overrides
        aggressive_cleaning = aggressive if aggressive is not None else self.config.aggressive_cleaning
        preserve_js = preserve_js_data if preserve_js_data is not None else self.config.preserve_js_data
        
        try:
            self.logger.info(f"Cleaning HTML: {len(html)} characters")
            
            # Check size limits
            if len(html) > self.config.max_html_size:
                self.logger.warning(f"HTML size ({len(html)}) exceeds limit ({self.config.max_html_size})")
                html = html[:self.config.max_html_size]
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JavaScript data before cleaning
            extracted_data = ExtractedJSData()
            if preserve_js:
                extracted_data = self._extract_js_data(soup)
            
            # Apply cleaning steps
            if aggressive_cleaning:
                self._aggressive_cleaning(soup)
            else:
                self._standard_cleaning(soup)
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Final cleanup
            cleaned_html = self._final_cleanup(cleaned_html)
            
            # Log results
            original_size = len(html)
            cleaned_size = len(cleaned_html)
            reduction = ((original_size - cleaned_size) / original_size * 100) if original_size > 0 else 0
            
            self.logger.info(
                f"HTML cleaned: {original_size} → {cleaned_size} chars "
                f"({reduction:.1f}% reduction)"
            )
            
            return cleaned_html
            
        except Exception as e:
            self.logger.error(f"HTML cleaning failed: {e}")
            raise HTMLCleaningError(
                message=f"Failed to clean HTML: {e}",
                operation="clean_html",
                details={"html_size": str(len(html))}
            ) from e
    
    def clean_html_sync(self, html: str, **kwargs) -> str:
        """
        Synchronous HTML cleaning
        
        Args:
            html: Raw HTML content
            **kwargs: Cleaning options
            
        Returns:
            Cleaned HTML
        """
        # Handle running event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a new thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.clean_html(html, **kwargs))
                return future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            return asyncio.run(self.clean_html(html, **kwargs))
    
    async def parse_and_clean_html(
        self,
        html: str,
        schema: Optional[dict[str, str]] = None,
        instructions: Optional[str] = None,
        **kwargs
    ) -> dict[str, str]:
        """
        Parse and clean HTML with LLM analysis preparation
        
        Args:
            html: Raw HTML content
            schema: Optional data schema for extraction
            instructions: Optional parsing instructions
            **kwargs: Additional options
            
        Returns:
            Dictionary with cleaned HTML and metadata
        """
        try:
            # Clean HTML
            cleaned_html = await self.clean_html(html, **kwargs)
            
            # Get cleaning stats
            stats = self.get_cleaning_stats(html, cleaned_html)
            
            result = {
                "cleaned_html": cleaned_html,
                "original_size": str(stats.original_size_bytes),
                "cleaned_size": str(stats.cleaned_size_bytes),
                "reduction_percent": f"{stats.size_reduction_percent:.1f}",
                "estimated_token_savings": str(stats.estimated_token_savings)
            }
            
            if schema:
                result["schema"] = str(schema)
            if instructions:
                result["instructions"] = instructions
            
            return result
            
        except Exception as e:
            raise HTMLCleaningError(
                message=f"Failed to parse and clean HTML: {e}",
                operation="parse_and_clean_html"
            ) from e
    
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
        noise_tags = {
            'meta', 'link', 'base', 'title', 'head', 'noscript',
            'iframe', 'embed', 'object', 'svg', 'canvas',
            'audio', 'video', 'source', 'track', 'area', 'map', 'param'
        }
        
        # Add conditional tags
        if self.config.remove_scripts:
            noise_tags.add('script')
        if self.config.remove_styles:
            noise_tags.add('style')
        if not self.config.preserve_forms:
            noise_tags.update({'form', 'input', 'button', 'select', 'textarea', 'fieldset', 'legend'})
        
        # Remove noise tags
        for tag_name in noise_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Remove empty elements
        if self.config.remove_empty_elements:
            for tag in soup.find_all(['div', 'span', 'p']):
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
            'style', 'onclick', 'onload', 'onchange', 'onmouseover',
            'onmouseout', 'onfocus', 'onblur', 'onsubmit', 'onreset',
            'onerror', 'onabort', 'autocomplete', 'autofocus',
            'checked', 'defer', 'disabled', 'hidden', 'loop',
            'multiple', 'muted', 'open', 'readonly', 'required',
            'tabindex', 'translate', 'draggable', 'contenteditable'
        }
        
        # Attributes to keep
        keep_attributes = {
            'id', 'class', 'href', 'src', 'alt', 'title',
            'data-testid', 'data-test', 'data-cy',
            'aria-label', 'aria-labelledby', 'aria-describedby', 'role'
        }
        
        for tag in soup.find_all(True):
            if hasattr(tag, 'attrs'):
                # Remove unwanted attributes
                attrs_to_remove = set(tag.attrs.keys()) - keep_attributes
                for attr in attrs_to_remove:
                    if attr in noise_attributes:
                        del tag.attrs[attr]
    
    def _clean_tracking_urls(self, soup: BeautifulSoup) -> None:
        """Remove or replace tracking URLs"""
        # Clean href attributes
        for tag in soup.find_all(['a'], href=True):
            href = tag.get('href', '')
            if href:
                for pattern in self.tracking_url_patterns:
                    if pattern.match(href):
                        tag['href'] = '#tracking-url-removed'
                        break
        
        # Clean src attributes
        for tag in soup.find_all(['img'], src=True):
            src = tag.get('src', '')
            if src:
                for pattern in self.tracking_url_patterns:
                    if pattern.match(src):
                        tag['src'] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        break
    
    def _clean_base64_data(self, soup: BeautifulSoup) -> None:
        """Remove large base64 encoded data"""
        for tag in soup.find_all(['img'], src=True):
            src = tag.get('src', '')
            if src:
                for pattern in self.base64_patterns:
                    if pattern.search(src):
                        tag['src'] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        break
    
    def _truncate_long_urls(self, soup: BeautifulSoup) -> None:
        """Truncate URLs longer than max_url_length"""
        max_length = self.config.max_url_length
        
        for tag in soup.find_all(['a'], href=True):
            href = tag.get('href', '')
            if isinstance(href, str) and len(href) > max_length:
                tag['href'] = href[:max_length] + '...truncated'
        
        for tag in soup.find_all(['img'], src=True):
            src = tag.get('src', '')
            if isinstance(src, str) and len(src) > max_length and not src.startswith('data:'):
                tag['src'] = src[:max_length] + '...truncated'
    
    def _remove_long_attributes(self, soup: BeautifulSoup) -> None:
        """Remove attributes with extremely long values"""
        for tag in soup.find_all():
            attrs_to_remove = []
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and len(value) > 800:
                    attrs_to_remove.append(attr)
                elif any(tracking in attr.lower() for tracking in 
                        ['tracking', 'analytics', 'gtm', 'pixel']):
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del tag.attrs[attr]
    
    def _truncate_long_text(self, soup: BeautifulSoup) -> None:
        """Truncate text content longer than max_text_length"""
        max_length = self.config.max_text_length
        
        for element in soup.find_all(text=True):
            if element.parent.name not in ['script', 'style']:
                text_content = str(element).strip()
                if text_content and len(text_content) > max_length:
                    truncated_text = text_content[:max_length] + '...'
                    element.replace_with(truncated_text)
    
    def _remove_comments(self, soup: BeautifulSoup) -> None:
        """Remove HTML comments"""
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
    
    def _normalize_whitespace(self, soup: BeautifulSoup) -> None:
        """Normalize whitespace in text content"""
        for element in soup.find_all(text=True):
            if element.parent.name not in ['script', 'style']:
                # Replace multiple spaces with single space
                cleaned_text = re.sub(r' {3,}', '  ', str(element))
                # Replace multiple newlines with maximum 2
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
                # Replace multiple tabs with single space
                cleaned_text = re.sub(r'\t+', ' ', cleaned_text)
                element.replace_with(cleaned_text)
    
    def _final_cleanup(self, html: str) -> str:
        """Final cleanup and optimization"""
        # Remove empty attributes
        html = re.sub(r'\s+\w+=""', '', html)
        
        # Remove extra spaces in attributes
        html = re.sub(r'(\w+)=\s*"([^"]*)"', r'\1="\2"', html)
        
        # Normalize quotes
        html = re.sub(r"(\w+)='([^']*)'", r'\1="\2"', html)
        
        # Remove trailing spaces before closing tags
        html = re.sub(r'\s+(/?>)', r'\1', html)
        
        # Advanced whitespace cleanup
        html = self._advanced_whitespace_cleanup(html)
        
        return html.strip()
    
    def _advanced_whitespace_cleanup(self, html: str) -> str:
        """Advanced whitespace cleanup"""
        # Remove excessive spaces
        html = re.sub(r' {3,}', '  ', html)
        
        # Remove excessive newlines
        html = re.sub(r'\n{3,}', '\n\n', html)
        
        # Clean space between tags
        html = re.sub(r'>\s{2,}<', '> <', html)
        
        return html
    
    # ==========================================
    # JAVASCRIPT DATA EXTRACTION
    # ==========================================
    
    def _extract_js_data(self, soup: BeautifulSoup) -> ExtractedJSData:
        """Extract valuable JavaScript data"""
        extracted_data = ExtractedJSData()
        
        # Find all script tags
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
            
            script_content = script.string.strip()
            
            # Skip empty scripts
            if len(script_content) < 10:
                continue
            
            # Check for JSON-LD structured data
            if script.get('type') == 'application/ld+json':
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
            estimated_token_savings_percent=token_savings_percent
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

def get_html_manager(config: Optional[HTMLCleaningConfig] = None) -> HTMLManager:
    """
    Get an HTML manager instance
    
    Args:
        config: Optional HTML cleaning configuration
        
    Returns:
        Configured HTMLManager instance
    """
    return HTMLManager(config=config)


async def quick_clean_html(html: str, **kwargs) -> str:
    """
    Quick HTML cleaning convenience function
    
    Args:
        html: Raw HTML content
        **kwargs: Cleaning options
        
    Returns:
        Cleaned HTML
    """
    config_data = {k: v for k, v in kwargs.items() if k in HTMLCleaningConfig.model_fields}
    config = HTMLCleaningConfig.model_validate(config_data) if config_data else None
    
    manager = get_html_manager(config)
    return await manager.clean_html(html, **kwargs)


def quick_clean_html_sync(html: str, **kwargs) -> str:
    """
    Quick synchronous HTML cleaning convenience function
    
    Args:
        html: Raw HTML content
        **kwargs: Cleaning options
        
    Returns:
        Cleaned HTML
    """
    config_data = {k: v for k, v in kwargs.items() if k in HTMLCleaningConfig.model_fields}
    config = HTMLCleaningConfig.model_validate(config_data) if config_data else None
    
    manager = get_html_manager(config)
    return manager.clean_html_sync(html, **kwargs)
