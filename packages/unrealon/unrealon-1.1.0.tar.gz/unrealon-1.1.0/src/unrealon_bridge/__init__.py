"""
Bridge Parsers - Parser-specific wrapper over generic bridge.

Extends the generic WebSocket bridge with parser orchestration capabilities:
- Parser registration and management
- Command execution and tracking  
- Proxy allocation and management
- Parser session logging
- Typed data models for all parser operations

This is a wrapper that adds parser domain knowledge to the generic bridge.
"""

from importlib.metadata import version

try:
    __version__ = version("unrealon")
except Exception:
    __version__ = "1.1.0"

from .models import (
    # Base models
    BaseParserModel,
    # Core models
    ParserInfo,
    ParserCommand,
    CommandResult,
    ProxyRequest,
    ProxyInfo,
    ParserSession,
    ParserEvent,
    ParserStats,
    ParserHealth,
    WebhookConfig,
    # RPC Response models
    BaseRPCResponse,
    ParserRegisterResponse,
    ParserStatusResponse,
    ParserListResponse,
    ParserHealthResponse,
    SessionStartResponse,
    SessionEndResponse,
    CommandExecuteResponse,
    CommandCreateResponse,
    CommandStatusResponse,
    ProxyAllocateResponse,
    ProxyReleaseResponse,
    ProxyCheckResponse,
    # RPC Request models
    BaseRPCRequest,
    ParserRegisterRequest,
    ParserStatusRequest,
    ParserListRequest,
    ParserHealthRequest,
    SessionStartRequest,
    SessionEndRequest,
    CommandExecuteRequest,
    CommandCreateRequest,
    CommandStatusRequest,
    ProxyAllocateRequest,
    ProxyReleaseRequest,
    ProxyCheckRequest,
)

from .client import ParserBridgeClient
from .server import ParserBridgeServer


__all__ = [
    # Base Models
    "BaseParserModel",
    # Core Models
    "ParserInfo",
    "ParserCommand",
    "CommandResult",
    "ProxyRequest",
    "ProxyInfo",
    "ParserSession",
    "ParserEvent",
    "ParserStats",
    "ParserHealth",
    "WebhookConfig",
    # RPC Response Models
    "BaseRPCResponse",
    "ParserRegisterResponse",
    "ParserStatusResponse",
    "ParserListResponse",
    "ParserHealthResponse",
    "SessionStartResponse",
    "SessionEndResponse",
    "CommandExecuteResponse",
    "CommandCreateResponse",
    "CommandStatusResponse",
    "ProxyAllocateResponse",
    "ProxyReleaseResponse",
    "ProxyCheckResponse",
    # RPC Request Models
    "BaseRPCRequest",
    "ParserRegisterRequest",
    "ParserStatusRequest",
    "ParserListRequest",
    "ParserHealthRequest",
    "SessionStartRequest",
    "SessionEndRequest",
    "CommandExecuteRequest",
    "CommandCreateRequest",
    "CommandStatusRequest",
    "ProxyAllocateRequest",
    "ProxyReleaseRequest",
    "ProxyCheckRequest",
    # Client/Server
    "ParserBridgeClient",
    "ParserBridgeServer",
]
