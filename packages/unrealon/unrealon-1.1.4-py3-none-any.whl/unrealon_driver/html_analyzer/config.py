"""
Configuration models for HTML Analyzer.
"""

from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

from unrealon_driver.websocket import get_websocket_url


class HTMLCleaningConfig(BaseModel):
    """HTML cleaning configuration with strict typing"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Cleaning modes
    aggressive_cleaning: bool = Field(default=True, description="Enable aggressive cleaning")
    preserve_js_data: bool = Field(default=True, description="Preserve JavaScript data during cleaning")

    # Content preservation
    preserve_images: bool = Field(default=False, description="Preserve image tags")
    preserve_links: bool = Field(default=True, description="Preserve link tags")
    preserve_forms: bool = Field(default=False, description="Preserve form elements")

    # Size limits
    max_html_size: int = Field(default=1000000, ge=1000, le=10000000, description="Maximum HTML size in characters")
    max_text_length: int = Field(default=300, ge=50, le=1000, description="Maximum text content length per element")
    max_url_length: int = Field(default=500, ge=100, le=2000, description="Maximum URL length")

    # Noise removal
    remove_comments: bool = Field(default=True, description="Remove HTML comments")
    remove_scripts: bool = Field(default=True, description="Remove script tags")
    remove_styles: bool = Field(default=True, description="Remove style tags")
    remove_tracking: bool = Field(default=True, description="Remove tracking URLs and attributes")

    # Whitespace handling
    normalize_whitespace: bool = Field(default=True, description="Normalize whitespace")
    remove_empty_elements: bool = Field(default=True, description="Remove empty elements")

    # Custom selectors
    noise_selectors: List[str] = Field(
        default_factory=lambda: ['[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]', '[class*="footer"]', '[class*="header"]', '[class*="ads"]', '[class*="popup"]', '[class*="modal"]', '[class*="cookie"]'], description="CSS selectors for noise elements to remove"
    )


class HTMLAnalyzerConfig(BaseModel):
    """Configuration for HTML Analyzer"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Parser identity
    parser_id: str = Field(..., min_length=1)

    # Cleaning configuration
    cleaning_config: HTMLCleaningConfig = Field(default_factory=HTMLCleaningConfig)

    # WebSocket configuration (auto-detected)
    websocket_url: Optional[str] = Field(default_factory=lambda: get_websocket_url(), description="WebSocket URL for analysis requests (auto-detected based on environment)")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")

    # Analysis settings
    default_timeout: float = Field(default=60.0, gt=0.0, description="Default analysis timeout")
    enable_websocket_analysis: bool = Field(default=True, description="Enable WebSocket-based analysis")
