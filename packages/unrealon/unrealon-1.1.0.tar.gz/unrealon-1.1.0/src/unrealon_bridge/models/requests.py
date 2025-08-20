"""
RPC request models.

Strict typing for all RPC requests - NO Dict[str, Any] allowed!
"""

from typing import Optional, Dict, List
from pydantic import Field

from .base import BaseRPCRequest


class ParserRegisterRequest(BaseRPCRequest):
    """Request for parser registration."""

    parser_id: str = Field(description="Unique parser identifier")
    parser_type: str = Field(description="Type of parser")
    version: str = Field(description="Parser version")
    capabilities: List[str] = Field(default_factory=list, description="Parser capabilities")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata")


class ParserStatusRequest(BaseRPCRequest):
    """Request for parser status."""

    parser_id: str = Field(description="Parser ID to get status for")


class ParserListRequest(BaseRPCRequest):
    """Request for parser list."""

    parser_type: Optional[str] = Field(default=None, description="Filter by parser type")


class ParserHealthRequest(BaseRPCRequest):
    """Request for parser health check."""

    parser_id: str = Field(description="Parser ID to check health for")


class SessionStartRequest(BaseRPCRequest):
    """Request for session start."""

    parser_id: str = Field(description="Parser ID")
    session_type: str = Field(description="Type of session")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Session metadata")


class SessionEndRequest(BaseRPCRequest):
    """Request for session end."""

    session_id: str = Field(description="Session ID to end")


class CommandExecuteRequest(BaseRPCRequest):
    """Request for command execution."""

    command_type: str = Field(description="Type of command")
    parser_id: str = Field(description="Parser ID")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Command parameters")
    timeout: int = Field(default=300, description="Command timeout in seconds")


class CommandCreateRequest(BaseRPCRequest):
    """Request for command creation."""

    command_type: str = Field(description="Type of command")
    parser_id: str = Field(description="Parser ID")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Command parameters")


class CommandStatusRequest(BaseRPCRequest):
    """Request for command status."""

    command_id: str = Field(description="Command ID to get status for")


class ProxyAllocateRequest(BaseRPCRequest):
    """Request for proxy allocation."""

    parser_id: str = Field(description="Parser ID requesting proxy")
    proxy_type: str = Field(default="http", description="Type of proxy needed")
    location: Optional[str] = Field(default=None, description="Preferred proxy location")


class ProxyReleaseRequest(BaseRPCRequest):
    """Request for proxy release."""

    proxy_id: str = Field(description="Proxy ID to release")


class ProxyCheckRequest(BaseRPCRequest):
    """Request for proxy health check."""

    proxy_id: str = Field(description="Proxy ID to check")
