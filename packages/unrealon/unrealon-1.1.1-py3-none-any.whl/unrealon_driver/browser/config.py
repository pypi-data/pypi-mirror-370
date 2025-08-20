"""
Browser configuration with Pydantic v2
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    """
    Browser configuration with smart defaults
    """
    
    # Browser type and mode
    browser_type: str = Field("chromium", description="Browser type (chromium, firefox, webkit)")
    headless: bool = Field(True, description="Run browser in headless mode")
    
    # Stealth and detection
    stealth_mode: bool = Field(True, description="Enable stealth mode")
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    viewport_width: int = Field(1920, description="Viewport width")
    viewport_height: int = Field(1080, description="Viewport height")
    
    # Timeouts
    page_timeout: int = Field(30000, description="Page load timeout in milliseconds")
    navigation_timeout: int = Field(30000, description="Navigation timeout in milliseconds")
    element_timeout: int = Field(10000, description="Element wait timeout in milliseconds")
    
    # Proxy settings
    proxy_url: Optional[str] = Field(None, description="Proxy URL")
    proxy_username: Optional[str] = Field(None, description="Proxy username")
    proxy_password: Optional[str] = Field(None, description="Proxy password")
    
    # Cookie and session management
    persist_cookies: bool = Field(True, description="Persist cookies between sessions")
    cookies_file: Optional[Path] = Field(None, description="Path to cookies file")
    
    # Screenshots and debugging
    screenshots_dir: Optional[Path] = Field(None, description="Screenshots directory")
    save_screenshots: bool = Field(False, description="Save screenshots for debugging")
    debug: bool = Field(False, description="Enable debug mode")
    
    # Performance settings
    disable_images: bool = Field(False, description="Disable image loading")
    disable_javascript: bool = Field(False, description="Disable JavaScript execution")
    disable_css: bool = Field(False, description="Disable CSS loading")
    
    # Browser arguments
    extra_args: List[str] = Field(default_factory=list, description="Additional browser arguments")
    
    # Additional settings
    extra_config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        extra = "forbid"
        
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization setup"""
        # Setup directories
        if not self.screenshots_dir:
            self.screenshots_dir = Path.cwd() / "system" / "screenshots"
            
        if not self.cookies_file:
            self.cookies_file = Path.cwd() / "system" / "cookies.json"
            
        # Create directories
        if self.screenshots_dir:
            self.screenshots_dir.mkdir(parents=True, exist_ok=True)
            
        if self.cookies_file:
            self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
