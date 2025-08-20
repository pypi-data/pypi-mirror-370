"""
Bridge Server Configuration

Pydantic2-based configuration management for the bridge server.
Includes default test API keys for debugging.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RedisConfig(BaseModel):
    """Redis connection configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    max_connections: int = Field(default=10, description="Maximum Redis connections")
    connection_timeout: int = Field(default=5, description="Redis connection timeout in seconds")


class WebSocketConfig(BaseModel):
    """WebSocket server configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    host: str = Field(default="localhost", description="WebSocket server host")
    port: int = Field(default=8002, description="WebSocket server port")
    max_connections: int = Field(default=100, description="Maximum WebSocket connections")
    ping_interval: int = Field(default=20, description="WebSocket ping interval in seconds")
    ping_timeout: int = Field(default=10, description="WebSocket ping timeout in seconds")


class SecurityConfig(BaseModel):
    """Security and authentication configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Default test API keys for debugging
    test_api_keys: List[str] = Field(default=["amazon_parser_key_123", "test_parser_key_456", "debug_key_789", "development_key_000"], description="Test API keys for debugging (DO NOT USE IN PRODUCTION)")

    # Production API keys (loaded from environment or config)
    api_keys: List[str] = Field(default_factory=list, description="Production API keys")

    require_api_key: bool = Field(default=True, description="Whether API key is required for parser registration")

    allow_test_keys: bool = Field(default=True, description="Allow test API keys (disable in production)")


class RPCConfig(BaseModel):
    """RPC configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    channel: str = Field(default="amazon_parser_rpc", description="RPC channel name")
    timeout: int = Field(default=30, description="RPC call timeout in seconds")


class PubSubConfig(BaseModel):
    """PubSub configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    prefix: str = Field(default="amazon_parser", description="PubSub channel prefix")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log message format")
    enable_debug: bool = Field(default=False, description="Enable debug logging")


class BridgeConfig(BaseModel):
    """Main bridge server configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # Sub-configurations
    redis: RedisConfig = Field(default_factory=RedisConfig)
    websocket: WebSocketConfig = Field(default_factory=WebSocketConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    rpc: RPCConfig = Field(default_factory=RPCConfig)
    pubsub: PubSubConfig = Field(default_factory=PubSubConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Environment
    environment: str = Field(default="development", description="Environment (development, testing, production)")

    def get_all_api_keys(self) -> List[str]:
        """Get all valid API keys (test + production)."""
        all_keys = []

        # Add production keys
        all_keys.extend(self.security.api_keys)

        # Add test keys if allowed
        if self.security.allow_test_keys:
            all_keys.extend(self.security.test_api_keys)

        return all_keys

    def is_valid_api_key(self, api_key: str) -> bool:
        """Check if API key is valid."""
        if not self.security.require_api_key:
            return True

        return api_key in self.get_all_api_keys()

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() in ("development", "dev")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_envs = ["development", "dev", "testing", "test", "production", "prod"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()


# Global config cache
_config_cache: Optional[BridgeConfig] = None


def get_config_path() -> Path:
    """Get configuration file path."""
    # Check environment variable first
    config_path = os.getenv("BRIDGE_CONFIG_PATH")
    if config_path:
        return Path(config_path)

    # Default path
    return Path(__file__).parent / "bridge_config.yaml"


def load_bridge_config(config_path: Optional[Path] = None) -> BridgeConfig:
    """
    Load bridge configuration from YAML file.

    Args:
        config_path: Optional path to config file

    Returns:
        BridgeConfig instance
    """
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    if config_path is None:
        config_path = get_config_path()

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            _config_cache = BridgeConfig(**config_data)
    else:
        # Create default config
        _config_cache = BridgeConfig()
        save_bridge_config(_config_cache, config_path)

    return _config_cache


def save_bridge_config(config: BridgeConfig, config_path: Optional[Path] = None) -> Path:
    """
    Save bridge configuration to YAML file.

    Args:
        config: BridgeConfig instance
        config_path: Optional path to save config

    Returns:
        Path where config was saved
    """
    if config_path is None:
        config_path = get_config_path()

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, indent=2, allow_unicode=True)

    return config_path


def reload_config() -> BridgeConfig:
    """Reload configuration from file, clearing cache."""
    global _config_cache
    _config_cache = None
    return load_bridge_config()


def create_sample_config() -> BridgeConfig:
    """Create a sample configuration for testing."""
    return BridgeConfig(
        environment="development", websocket=WebSocketConfig(host="localhost", port=8002), security=SecurityConfig(test_api_keys=["amazon_parser_key_123", "test_parser_key_456", "debug_key_789"], allow_test_keys=True, require_api_key=True), logging=LoggingConfig(level="DEBUG", enable_debug=True)
    )
