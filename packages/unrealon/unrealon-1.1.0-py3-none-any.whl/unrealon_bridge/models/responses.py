"""
RPC response models.

Strict typing for all RPC responses - NO raw dicts allowed!
"""

from typing import Optional, List
from pydantic import Field

from .base import BaseRPCResponse
from .parser import ParserInfo, ParserHealth
from .session import ParserSession
from .command import ParserCommand, CommandResult
from .proxy import ProxyInfo


class ParserRegisterResponse(BaseRPCResponse):
    """Response for parser registration."""

    parser_id: Optional[str] = Field(default=None, description="Registered parser ID")


class ParserStatusResponse(BaseRPCResponse):
    """Response for parser status request."""

    parser: Optional[ParserInfo] = Field(default=None, description="Parser information")


class ParserListResponse(BaseRPCResponse):
    """Response for parser list request."""

    parsers: List[ParserInfo] = Field(default_factory=list, description="List of parsers")
    total: int = Field(default=0, description="Total number of parsers")


class ParserHealthResponse(BaseRPCResponse):
    """Response for parser health check."""

    health: Optional[ParserHealth] = Field(default=None, description="Parser health information")


class SessionStartResponse(BaseRPCResponse):
    """Response for session start."""

    session: Optional[ParserSession] = Field(default=None, description="Started session information")


class SessionEndResponse(BaseRPCResponse):
    """Response for session end."""

    session_id: Optional[str] = Field(default=None, description="Ended session ID")


class CommandExecuteResponse(BaseRPCResponse):
    """Response for command execution."""

    result: Optional[CommandResult] = Field(default=None, description="Command execution result")


class CommandCreateResponse(BaseRPCResponse):
    """Response for command creation."""

    command: Optional[ParserCommand] = Field(default=None, description="Created command")


class CommandStatusResponse(BaseRPCResponse):
    """Response for command status request."""

    command: Optional[ParserCommand] = Field(default=None, description="Command information")


class ProxyAllocateResponse(BaseRPCResponse):
    """Response for proxy allocation."""

    proxy: Optional[ProxyInfo] = Field(default=None, description="Allocated proxy information")


class ProxyReleaseResponse(BaseRPCResponse):
    """Response for proxy release."""

    proxy_id: Optional[str] = Field(default=None, description="Released proxy ID")


class ProxyCheckResponse(BaseRPCResponse):
    """Response for proxy health check."""

    proxy_id: Optional[str] = Field(default=None, description="Checked proxy ID")
    status: Optional[str] = Field(default=None, description="Proxy status")
