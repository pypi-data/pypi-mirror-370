"""
Bridge configuration module.

Provides Pydantic2 configuration management for the bridge server.
"""

from .bridge_config import BridgeConfig, load_bridge_config, save_bridge_config, create_sample_config

__all__ = [
    "BridgeConfig",
    "load_bridge_config", 
    "save_bridge_config",
    "create_sample_config"
]
