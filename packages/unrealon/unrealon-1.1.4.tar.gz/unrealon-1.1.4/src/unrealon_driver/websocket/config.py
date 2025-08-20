"""
Global WebSocket Configuration for UnrealOn Driver

Provides automatic WebSocket URL detection and configuration management.
No need to specify URLs in parser config files - everything is handled automatically.

Strict compliance with CRITICAL_REQUIREMENTS.md:
- Pydantic v2 models everywhere
- No Dict[str, Any] usage
- Complete type annotations
- Proper error handling
"""

import os
import socket
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class Environment(str, Enum):
    """Environment types for automatic URL detection"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    LOCAL = "local"


class EnvironmentInfo(BaseModel):
    """Environment detection information with full typing"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    detected_environment: Environment
    websocket_url: str = Field(..., description="Detected WebSocket URL")
    localhost_available: bool = Field(..., description="Whether localhost service is available")
    environment_variables: Dict[str, Optional[str]] = Field(
        default_factory=dict, 
        description="Relevant environment variables"
    )


class GlobalWebSocketConfig(BaseModel):
    """Global WebSocket configuration with automatic URL detection"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Production WebSocket URL
    production_websocket_url: str = Field(
        default="wss://ws.unrealon.com/ws",
        description="Production WebSocket URL"
    )
    
    # Development WebSocket URL
    development_websocket_url: str = Field(
        default="ws://localhost:8002/ws",
        description="Development WebSocket URL"
    )
    
    # Default environment
    default_environment: Environment = Field(
        default=Environment.PRODUCTION,
        description="Default environment when detection fails"
    )
    
    @field_validator('production_websocket_url', 'development_websocket_url')
    @classmethod
    def validate_websocket_url(cls, v: str) -> str:
        """Validate WebSocket URL format"""
        if not v.startswith(('ws://', 'wss://')):
            raise ValueError("WebSocket URL must start with ws:// or wss://")
        return v
    
    def get_websocket_url(self, environment: Optional[Environment] = None) -> str:
        """Get WebSocket URL for specified environment"""
        env = environment or self._detect_environment()
        
        if env == Environment.PRODUCTION:
            return self.production_websocket_url
        else:
            # Development and Local both use localhost
            return self.development_websocket_url
    
    def _detect_environment(self) -> Environment:
        """Automatically detect environment based on various indicators"""
        
        # Check explicit environment variable
        env_var = os.getenv("UNREALON_ENV", "").lower()
        if env_var == Environment.PRODUCTION.value:
            return Environment.PRODUCTION
        elif env_var == Environment.DEVELOPMENT.value:
            return Environment.DEVELOPMENT
        elif env_var == Environment.LOCAL.value:
            return Environment.LOCAL
        
        # Check if we're in development mode
        if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
            return Environment.DEVELOPMENT
        
        # Check if localhost services are available
        if self._is_localhost_available():
            return Environment.DEVELOPMENT
        
        # Check common development indicators
        development_indicators = [
            os.getenv("NODE_ENV") == "development",
            os.getenv("DJANGO_DEBUG", "").lower() in ("true", "1"),
            os.getenv("FLASK_ENV") == "development",
            os.path.exists(".env"),
            os.path.exists("docker-compose.yml"),
            os.path.exists("pyproject.toml") and os.getcwd().endswith("unrealon-rpc")
        ]
        
        if any(development_indicators):
            return Environment.DEVELOPMENT
        
        # Default to production for safety
        return Environment.PRODUCTION
    
    def _is_localhost_available(self) -> bool:
        """Check if localhost WebSocket service is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', 8002))
                return result == 0
        except OSError:
            return False
        except Exception:
            return False
    
    def get_environment_info(self) -> EnvironmentInfo:
        """Get current environment information for debugging"""
        current_env = self._detect_environment()
        
        env_vars = {
            "UNREALON_ENV": os.getenv("UNREALON_ENV"),
            "DEBUG": os.getenv("DEBUG"),
            "NODE_ENV": os.getenv("NODE_ENV"),
            "DJANGO_DEBUG": os.getenv("DJANGO_DEBUG"),
        }
        
        return EnvironmentInfo(
            detected_environment=current_env,
            websocket_url=self.get_websocket_url(current_env),
            localhost_available=self._is_localhost_available(),
            environment_variables=env_vars
        )


# Global configuration instance
global_websocket_config = GlobalWebSocketConfig()


def get_websocket_url(environment: Optional[Environment] = None) -> str:
    """Get WebSocket URL for current or specified environment"""
    return global_websocket_config.get_websocket_url(environment)





def get_environment() -> Environment:
    """Get current detected environment"""
    return global_websocket_config._detect_environment()


def set_environment(environment: Environment) -> None:
    """Override environment detection (for testing)"""
    os.environ["UNREALON_ENV"] = environment.value


def get_debug_info() -> EnvironmentInfo:
    """Get debug information about current configuration"""
    return global_websocket_config.get_environment_info()


# Convenience functions for common use cases
def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment() == Environment.DEVELOPMENT


def is_local() -> bool:
    """Check if running in local environment"""
    return get_environment() == Environment.LOCAL
