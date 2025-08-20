"""
WebSocket message models for daemon communication.

Strict Pydantic v2 compliance and type safety.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageType(str, Enum):
    """WebSocket message types."""
    REGISTER = "register"
    COMMAND = "command"
    COMMAND_RESPONSE = "command_response"
    STATUS = "status"
    HEARTBEAT = "heartbeat"


class BridgeMessageType(str, Enum):
    """Bridge WebSocket message types."""
    REGISTER = "register"
    RPC_CALL = "rpc_call"
    PUBSUB_PUBLISH = "pubsub_publish"
    HEARTBEAT = "heartbeat"


class RegistrationMessage(BaseModel):
    """Daemon registration message."""
    type: MessageType = Field(default=MessageType.REGISTER)
    parser_id: str = Field(..., min_length=1, description="Parser identifier")
    parser_type: str = Field(default="daemon", description="Parser type")
    version: str = Field(default="1.0.0", description="Parser version")
    capabilities: List[str] = Field(default_factory=lambda: ["parse", "search", "status", "health"])


class CommandMessage(BaseModel):
    """Incoming command message."""
    type: MessageType = Field(default=MessageType.COMMAND)
    command_type: str = Field(..., min_length=1, description="Command type")
    command_id: str = Field(..., min_length=1, description="Command identifier")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Command parameters")


class CommandResponseMessage(BaseModel):
    """Command response message."""
    type: MessageType = Field(default=MessageType.COMMAND_RESPONSE)
    command_id: str = Field(..., min_length=1, description="Command identifier")
    success: bool = Field(..., description="Command success status")
    result_data: Optional[dict[str, Any]] = Field(default=None, description="Command result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class StatusMessage(BaseModel):
    """Daemon status message."""
    type: MessageType = Field(default=MessageType.STATUS)
    parser_id: str = Field(..., min_length=1, description="Parser identifier")
    running: bool = Field(..., description="Daemon running status")
    uptime_seconds: float = Field(..., ge=0, description="Uptime in seconds")
    total_runs: int = Field(..., ge=0, description="Total runs executed")
    successful_runs: int = Field(..., ge=0, description="Successful runs")
    failed_runs: int = Field(..., ge=0, description="Failed runs")


class HeartbeatMessage(BaseModel):
    """Daemon heartbeat message."""
    type: MessageType = Field(default=MessageType.HEARTBEAT)
    parser_id: str = Field(..., min_length=1, description="Parser identifier")
    timestamp: str = Field(..., description="Heartbeat timestamp")
    status: str = Field(default="alive", description="Daemon status")


# Bridge message models
class BridgeRegistrationPayload(BaseModel):
    """Payload for bridge registration message."""
    client_type: str = Field(default="daemon", description="Client type")
    parser_id: str = Field(..., min_length=1, description="Parser identifier")
    version: str = Field(default="1.0.0", description="Parser version")
    capabilities: List[str] = Field(default_factory=lambda: ["parse", "search", "status", "health"])


class BridgeMessage(BaseModel):
    """Bridge WebSocket message format."""
    message_type: BridgeMessageType = Field(..., description="Message type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Message payload")
    message_id: Optional[str] = Field(default=None, description="Message ID")
    api_key: Optional[str] = Field(default=None, description="API key")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID")
    reply_to: Optional[str] = Field(default=None, description="Reply to address")


class BridgeRegistrationMessage(BaseModel):
    """Bridge registration message."""
    message_type: BridgeMessageType = Field(default=BridgeMessageType.REGISTER)
    payload: BridgeRegistrationPayload = Field(..., description="Registration payload")
    message_id: Optional[str] = Field(default=None, description="Message ID")
    api_key: Optional[str] = Field(default=None, description="API key")
