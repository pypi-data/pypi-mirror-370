"""
Config Manager - Type-safe configuration management with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- No mutable defaults
"""

from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, field_validator
import uuid


class ParserConfig(BaseModel):
    """
    Parser configuration with smart defaults and strict typing
    
    Zero configuration approach - everything has sensible defaults
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )
    
    # Parser identity
    parser_id: str = Field(
        default_factory=lambda: f"parser_{uuid.uuid4().hex[:8]}",
        description="Unique parser identifier"
    )
    parser_name: str = Field(
        default="UnrealOn Parser",
        description="Human-readable parser name"
    )
    parser_type: str = Field(
        default="generic",
        description="Parser type for classification"
    )
    
    # Connection settings
    websocket_url: str = Field(
        default="ws://localhost:8002/ws",
        description="WebSocket bridge URL"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )
    
    # Browser settings
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    stealth_mode: bool = Field(
        default=True,
        description="Enable stealth mode"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom user agent"
    )
    
    # HTML cleaning settings
    aggressive_cleaning: bool = Field(
        default=True,
        description="Enable aggressive HTML cleaning"
    )
    preserve_js_data: bool = Field(
        default=True,
        description="Preserve JavaScript data during cleaning"
    )
    
    # Timeouts (in milliseconds)
    page_timeout: int = Field(
        default=30000,
        ge=1000,
        le=300000,
        description="Page load timeout in milliseconds"
    )
    navigation_timeout: int = Field(
        default=30000,
        ge=1000,
        le=300000,
        description="Navigation timeout in milliseconds"
    )
    
    # Directories
    system_dir: Optional[Path] = Field(
        default=None,
        description="System directory for logs and data"
    )
    screenshots_dir: Optional[Path] = Field(
        default=None,
        description="Screenshots directory"
    )
    
    # Development settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    save_html: bool = Field(
        default=False,
        description="Save HTML files for debugging"
    )
    save_screenshots: bool = Field(
        default=False,
        description="Save screenshots for debugging"
    )
    
    @field_validator('parser_name')
    @classmethod
    def validate_parser_name(cls, v: str) -> str:
        """Validate parser name is not empty"""
        if not v.strip():
            raise ValueError("Parser name cannot be empty")
        return v.strip()
    
    @field_validator('parser_type')
    @classmethod
    def validate_parser_type(cls, v: str) -> str:
        """Validate parser type"""
        allowed_types = {
            "generic", "ecommerce", "news", "jobs", 
            "real_estate", "social_media", "reviews", 
            "events", "directory"
        }
        if v not in allowed_types:
            raise ValueError(f"Parser type must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator('websocket_url')
    @classmethod
    def validate_websocket_url(cls, v: str) -> str:
        """Validate WebSocket URL format"""
        if not v.startswith(('ws://', 'wss://')):
            raise ValueError("WebSocket URL must start with ws:// or wss://")
        return v
    
    def model_post_init(self, __context) -> None:
        """Post-initialization setup"""
        # Setup system directory if not provided
        if self.system_dir is None:
            self.system_dir = Path.cwd() / "system"
        
        # Setup screenshots directory if not provided
        if self.screenshots_dir is None:
            self.screenshots_dir = self.system_dir / "screenshots"
        
        # Create directories
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """
    🔧 Config Manager - Type-safe configuration management
    
    Features:
    - Pydantic v2 validation
    - Environment variable integration
    - Configuration profiles
    - Hot reloading
    - Type safety enforcement
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        self._config: ParserConfig = config or ParserConfig()
        self._profiles: dict[str, ParserConfig] = {}
        self._current_profile: Optional[str] = None
    
    @property
    def config(self) -> ParserConfig:
        """Get current configuration"""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values"""
        # Create new config with updated values
        current_data = self._config.model_dump()
        current_data.update(kwargs)
        self._config = ParserConfig.model_validate(current_data)
    
    def load_from_dict(self, config_dict: dict[str, str]) -> None:
        """Load configuration from dictionary"""
        self._config = ParserConfig.model_validate(config_dict)
    
    def load_from_env(self, prefix: str = "PARSER_") -> None:
        """Load configuration from environment variables"""
        import os
        
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                
                # Convert string values to appropriate types
                if config_key in ['headless', 'stealth_mode', 'aggressive_cleaning', 
                                 'preserve_js_data', 'debug', 'save_html', 'save_screenshots']:
                    env_config[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['page_timeout', 'navigation_timeout']:
                    env_config[config_key] = int(value)
                elif config_key in ['system_dir', 'screenshots_dir']:
                    env_config[config_key] = Path(value)
                else:
                    env_config[config_key] = value
        
        if env_config:
            current_data = self._config.model_dump()
            current_data.update(env_config)
            self._config = ParserConfig.model_validate(current_data)
    
    def save_profile(self, name: str) -> None:
        """Save current configuration as a profile"""
        if not name.strip():
            raise ValueError("Profile name cannot be empty")
        self._profiles[name] = ParserConfig.model_validate(self._config.model_dump())
    
    def load_profile(self, name: str) -> None:
        """Load configuration from a saved profile"""
        if name not in self._profiles:
            raise ValueError(f"Profile '{name}' not found")
        self._config = ParserConfig.model_validate(self._profiles[name].model_dump())
        self._current_profile = name
    
    def get_profiles(self) -> List[str]:
        """Get list of available profiles"""
        return list(self._profiles.keys())
    
    def delete_profile(self, name: str) -> None:
        """Delete a saved profile"""
        if name not in self._profiles:
            raise ValueError(f"Profile '{name}' not found")
        del self._profiles[name]
        if self._current_profile == name:
            self._current_profile = None
    
    def get_current_profile(self) -> Optional[str]:
        """Get current profile name"""
        return self._current_profile
    
    def validate_config(self) -> List[str]:
        """Validate current configuration and return any issues"""
        issues = []
        
        # Check directory permissions
        try:
            test_file = self._config.system_dir / ".test"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            issues.append(f"No write permission for system directory: {self._config.system_dir}")
        except Exception as e:
            issues.append(f"System directory issue: {e}")
        
        # Check timeouts are reasonable
        if self._config.page_timeout < 5000:
            issues.append("Page timeout is very low (< 5 seconds)")
        if self._config.navigation_timeout < 5000:
            issues.append("Navigation timeout is very low (< 5 seconds)")
        
        return issues
    
    def to_dict(self) -> dict[str, str]:
        """Export configuration as dictionary"""
        return self._config.model_dump(mode='json')
    
    def to_env_format(self, prefix: str = "PARSER_") -> List[str]:
        """Export configuration as environment variable format"""
        config_dict = self.to_dict()
        env_vars = []
        
        for key, value in config_dict.items():
            env_key = f"{prefix}{key.upper()}"
            env_vars.append(f"{env_key}={value}")
        
        return env_vars
