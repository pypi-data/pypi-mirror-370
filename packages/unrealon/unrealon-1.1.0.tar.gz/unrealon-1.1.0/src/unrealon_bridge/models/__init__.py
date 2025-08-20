"""
Bridge Parsers Models - Decomposed and strictly typed.

All models follow CRITICAL_REQUIREMENTS.md:
- NO Dict[str, Any] usage
- Strict Pydantic v2 typing
- NO raw JSON handling
- Complete type annotations
"""

# Base models
from .base import BaseParserModel, BaseRPCRequest, BaseRPCResponse

# Core domain models
from .parser import ParserInfo, ParserStats, ParserHealth, ParserSystemStats
from .command import ParserCommand, CommandResult
from .proxy import ProxyRequest, ProxyInfo
from .session import ParserSession
from .events import ParserEvent, WebhookConfig
from .html_parser import (
    HTMLParseRequest, HTMLParseResult, HTMLParseResponse,
    HTMLParseRPCRequest, HTMLParseRPCResponse
)
from .logging import (
    ParserLogEntry, ParserLogRequest, ParserLogResponse
)
from .scheduler import (
    TaskStatus, TaskPriority, ScheduleType, TaskExecutionMode,
    CronExpression, TaskParameters, TaskRetryConfig, ScheduledTask,
    TaskQueue, TaskExecutionResult, ParserStatus,
    SchedulerError, TaskValidationError, TaskExecutionError,
    ParserUnavailableError, QueueError
)

# RPC Request models (strict typing)
from .requests import (
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

# RPC Response models (strict typing)
from .responses import (
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
)

__all__ = [
    # Base models
    "BaseParserModel",
    "BaseRPCRequest",
    "BaseRPCResponse",
    # Core domain models
    "ParserInfo",
    "ParserStats",
    "ParserHealth",
    "ParserSystemStats",
    "ParserCommand",
    "CommandResult",
    "ProxyRequest",
    "ProxyInfo",
    "ParserSession",
    "ParserEvent",
    "WebhookConfig",
    # HTML Parser models
    "HTMLParseRequest",
    "HTMLParseResult", 
    "HTMLParseResponse",
    "HTMLParseRPCRequest",
    "HTMLParseRPCResponse",
    # Parser Logging models
    "ParserLogEntry",
    "ParserLogRequest", 
    "ParserLogResponse",
    # Scheduler models
    "TaskStatus",
    "TaskPriority", 
    "ScheduleType",
    "TaskExecutionMode",
    "CronExpression",
    "TaskParameters",
    "TaskRetryConfig",
    "ScheduledTask",
    "TaskQueue", 
    "TaskExecutionResult",
    "ParserStatus",
    # Scheduler exceptions
    "SchedulerError",
    "TaskValidationError",
    "TaskExecutionError",
    "ParserUnavailableError",
    "QueueError",
    # RPC Request models
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
    # RPC Response models
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
]
