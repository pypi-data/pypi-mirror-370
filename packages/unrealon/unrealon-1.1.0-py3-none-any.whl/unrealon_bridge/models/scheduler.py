"""
Task Scheduler Models - UnrealOn RPC v2.0

Pydantic v2 models for hybrid RPC + Redis Queue task scheduling system.
Provides complete type safety for scheduled tasks, cron expressions, and task execution.

COMPLIANCE: 100% Pydantic v2, no Dict[str, Any], strict typing everywhere.
"""

import uuid
from enum import Enum
from typing import Optional, List, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing_extensions import Annotated

from .base import BaseParserModel


class TaskStatus(str, Enum):
    """Task execution status with clear state transitions."""
    
    PENDING = "pending"        # Task created, waiting for execution
    QUEUED = "queued"         # Task added to Redis Queue
    RUNNING = "running"       # Task currently executing
    COMPLETED = "completed"   # Task finished successfully
    FAILED = "failed"         # Task failed with error
    CANCELLED = "cancelled"   # Task cancelled by user
    TIMEOUT = "timeout"       # Task exceeded timeout
    RETRY = "retry"           # Task failed, will retry


class TaskPriority(int, Enum):
    """Task priority levels for queue ordering."""
    
    CRITICAL = 1    # System critical tasks
    HIGH = 3        # High priority tasks
    NORMAL = 5      # Default priority
    LOW = 7         # Background tasks
    BULK = 9        # Bulk processing tasks


class ScheduleType(str, Enum):
    """Types of task scheduling."""
    
    IMMEDIATE = "immediate"    # Execute immediately via RPC
    DELAYED = "delayed"        # Execute after delay via Queue
    RECURRING = "recurring"    # Execute on cron schedule
    CONDITIONAL = "conditional" # Execute when condition met


class TaskExecutionMode(str, Enum):
    """Task execution mode selection."""
    
    RPC_ONLY = "rpc_only"         # Force RPC execution
    QUEUE_ONLY = "queue_only"     # Force Queue execution
    HYBRID_AUTO = "hybrid_auto"   # Auto-select based on parser status
    HYBRID_PREFER_RPC = "hybrid_prefer_rpc"     # Prefer RPC, fallback to Queue
    HYBRID_PREFER_QUEUE = "hybrid_prefer_queue" # Prefer Queue, fallback to RPC


class CronExpression(BaseModel):
    """Cron expression with validation and parsing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )
    
    expression: Annotated[str, Field(
        description="Cron expression (minute hour day month weekday)",
        examples=["0 2 * * *", "*/15 * * * *", "0 9 * * 1-5"]
    )]
    
    timezone: Annotated[str, Field(
        default="UTC",
        description="Timezone for cron execution",
        examples=["UTC", "America/New_York", "Asia/Seoul"]
    )]
    
    @field_validator('expression')
    @classmethod
    def validate_cron_expression(cls, v: str) -> str:
        """Validate cron expression format."""
        if not v or not v.strip():
            raise ValueError("Cron expression cannot be empty")
        
        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 parts: minute hour day month weekday")
        
        # Basic validation for each part
        minute, hour, day, month, weekday = parts
        
        # Validate ranges (basic check)
        for part, name, max_val in [
            (minute, "minute", 59),
            (hour, "hour", 23), 
            (day, "day", 31),
            (month, "month", 12),
            (weekday, "weekday", 7)
        ]:
            if part != "*" and not any(c in part for c in ["/", "-", ","]):
                try:
                    val = int(part)
                    if val < 0 or val > max_val:
                        raise ValueError(f"Invalid {name} value: {val}")
                except ValueError as e:
                    if "invalid literal" not in str(e):
                        raise
        
        return v.strip()


class TaskParameters(BaseModel):
    """Strongly typed task parameters."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    command_type: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Type of command to execute",
        examples=["scrape", "parse", "daily_update", "cleanup"]
    )]
    
    parameters: Annotated[dict[str, str], Field(
        default_factory=dict,
        description="Command parameters (string values only for Redis compatibility)"
    )]
    
    timeout: Annotated[int, Field(
        default=300,
        ge=1,
        le=86400,  # 24 hours max
        description="Task timeout in seconds"
    )]
    
    @field_validator('parameters')
    @classmethod
    def validate_parameters(cls, v: dict[str, str]) -> dict[str, str]:
        """Ensure all parameter values are strings."""
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Parameter key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise ValueError(f"Parameter value must be string, got {type(value)} for key '{key}'")
        
        return v


class TaskRetryConfig(BaseModel):
    """Task retry configuration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_retries: Annotated[int, Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts"
    )]
    
    retry_delay: Annotated[int, Field(
        default=60,
        ge=1,
        le=3600,
        description="Initial retry delay in seconds"
    )]
    
    exponential_backoff: Annotated[bool, Field(
        default=True,
        description="Use exponential backoff for retry delays"
    )]
    
    max_retry_delay: Annotated[int, Field(
        default=3600,
        ge=60,
        le=86400,
        description="Maximum retry delay in seconds"
    )]


class ScheduledTask(BaseParserModel):
    """Complete scheduled task definition with full type safety."""
    
    # Task identification
    task_id: Annotated[str, Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique task identifier"
    )]
    
    task_name: Annotated[str, Field(
        min_length=1,
        max_length=200,
        description="Human-readable task name"
    )]
    
    # Parser targeting
    parser_type: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Target parser type",
        examples=["encar_parser", "autotrader_parser"]
    )]
    
    parser_id: Annotated[Optional[str], Field(
        default=None,
        description="Specific parser ID (optional, for targeting specific instance)"
    )]
    
    # Task execution
    task_parameters: TaskParameters
    execution_mode: TaskExecutionMode = TaskExecutionMode.HYBRID_AUTO
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Scheduling
    schedule_type: ScheduleType
    scheduled_at: Annotated[Optional[datetime], Field(
        default=None,
        description="When to execute (for delayed tasks)"
    )]
    
    cron_schedule: Annotated[Optional[CronExpression], Field(
        default=None,
        description="Cron schedule (for recurring tasks)"
    )]
    
    # Status and tracking
    status: TaskStatus = TaskStatus.PENDING
    created_at: Annotated[datetime, Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )]
    
    updated_at: Annotated[datetime, Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )]
    
    # Execution tracking
    started_at: Annotated[Optional[datetime], Field(
        default=None,
        description="Task execution start time"
    )]
    
    completed_at: Annotated[Optional[datetime], Field(
        default=None,
        description="Task completion time"
    )]
    
    # Retry configuration
    retry_config: TaskRetryConfig = Field(default_factory=TaskRetryConfig)
    retry_count: Annotated[int, Field(
        default=0,
        ge=0,
        description="Current retry attempt count"
    )]
    
    # Results and errors
    last_error: Annotated[Optional[str], Field(
        default=None,
        description="Last error message if failed"
    )]
    
    execution_log: Annotated[List[str], Field(
        default_factory=list,
        description="Execution log entries"
    )]
    
    # Metadata
    tags: Annotated[List[str], Field(
        default_factory=list,
        description="Task tags for filtering and organization"
    )]
    
    metadata: Annotated[dict[str, str], Field(
        default_factory=dict,
        description="Additional task metadata (string values only)"
    )]
    
    @model_validator(mode='after')
    def validate_schedule_consistency(self) -> 'ScheduledTask':
        """Validate scheduling configuration consistency."""
        if self.schedule_type == ScheduleType.DELAYED:
            if not self.scheduled_at:
                raise ValueError("Delayed tasks must have scheduled_at timestamp")
        
        elif self.schedule_type == ScheduleType.RECURRING:
            if not self.cron_schedule:
                raise ValueError("Recurring tasks must have cron_schedule")
        
        elif self.schedule_type == ScheduleType.IMMEDIATE:
            if self.scheduled_at or self.cron_schedule:
                raise ValueError("Immediate tasks cannot have scheduling configuration")
        
        return self
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: dict[str, str]) -> dict[str, str]:
        """Ensure metadata values are strings."""
        if not isinstance(v, dict):
            raise ValueError("Metadata must be a dictionary")
        
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Metadata key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise ValueError(f"Metadata value must be string, got {type(value)} for key '{key}'")
        
        return v
    
    def add_log_entry(self, message: str) -> None:
        """Add entry to execution log."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        self.updated_at = datetime.utcnow()
    
    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.add_log_entry("Task execution started")
    
    def mark_completed(self, result_message: Optional[str] = None) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        message = result_message or "Task completed successfully"
        self.add_log_entry(message)
    
    def mark_failed(self, error_message: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.last_error = error_message
        self.updated_at = datetime.utcnow()
        self.add_log_entry(f"Task failed: {error_message}")
    
    def increment_retry(self) -> None:
        """Increment retry count and update status."""
        self.retry_count += 1
        self.status = TaskStatus.RETRY
        self.updated_at = datetime.utcnow()
        self.add_log_entry(f"Retry attempt {self.retry_count}/{self.retry_config.max_retries}")
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status in [TaskStatus.FAILED, TaskStatus.TIMEOUT] and
            self.retry_count < self.retry_config.max_retries
        )
    
    def get_next_retry_delay(self) -> int:
        """Calculate next retry delay in seconds."""
        if not self.can_retry():
            return 0
        
        base_delay = self.retry_config.retry_delay
        
        if self.retry_config.exponential_backoff:
            delay = base_delay * (2 ** self.retry_count)
            return min(delay, self.retry_config.max_retry_delay)
        
        return base_delay


class TaskQueue(BaseModel):
    """Redis Queue configuration for task scheduling."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    queue_name: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Redis queue name"
    )]
    
    redis_url: Annotated[str, Field(
        description="Redis connection URL",
        examples=["redis://localhost:6379/1"]
    )]
    
    max_workers: Annotated[int, Field(
        default=4,
        ge=1,
        le=20,
        description="Maximum concurrent workers"
    )]
    
    worker_timeout: Annotated[int, Field(
        default=3600,
        ge=60,
        le=86400,
        description="Worker timeout in seconds"
    )]
    
    visibility_timeout: Annotated[int, Field(
        default=300,
        ge=30,
        le=3600,
        description="Task visibility timeout in seconds"
    )]
    
    dead_letter_queue: Annotated[Optional[str], Field(
        default=None,
        description="Dead letter queue name for failed tasks"
    )]


class TaskExecutionResult(BaseParserModel):
    """Result of task execution with complete type safety."""
    
    task_id: Annotated[str, Field(description="Task identifier")]
    
    success: Annotated[bool, Field(description="Execution success status")]
    
    execution_time: Annotated[float, Field(
        ge=0.0,
        description="Execution time in seconds"
    )]
    
    result_data: Annotated[dict[str, str], Field(
        default_factory=dict,
        description="Task result data (string values only)"
    )]
    
    error_message: Annotated[Optional[str], Field(
        default=None,
        description="Error message if failed"
    )]
    
    retry_count: Annotated[int, Field(
        default=0,
        ge=0,
        description="Number of retries performed"
    )]
    
    executed_at: Annotated[datetime, Field(
        default_factory=datetime.utcnow,
        description="Execution timestamp"
    )]
    
    executed_by: Annotated[Optional[str], Field(
        default=None,
        description="Parser ID that executed the task"
    )]
    
    @field_validator('result_data')
    @classmethod
    def validate_result_data(cls, v: dict[str, str]) -> dict[str, str]:
        """Ensure result data values are strings."""
        if not isinstance(v, dict):
            raise ValueError("Result data must be a dictionary")
        
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Result key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise ValueError(f"Result value must be string, got {type(value)} for key '{key}'")
        
        return v


class ParserStatus(BaseModel):
    """Parser online/offline status tracking."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    parser_id: Annotated[str, Field(description="Parser identifier")]
    
    parser_type: Annotated[str, Field(description="Parser type")]
    
    status: Annotated[str, Field(
        description="Parser status",
        pattern="^(online|offline|connecting|disconnecting)$"
    )]
    
    last_seen: Annotated[datetime, Field(
        default_factory=datetime.utcnow,
        description="Last heartbeat timestamp"
    )]
    
    capabilities: Annotated[List[str], Field(
        default_factory=list,
        description="Parser capabilities"
    )]
    
    current_tasks: Annotated[int, Field(
        default=0,
        ge=0,
        description="Number of currently executing tasks"
    )]
    
    max_concurrent_tasks: Annotated[int, Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum concurrent tasks this parser can handle"
    )]
    
    def is_online(self, timeout_seconds: int = 300) -> bool:
        """Check if parser is considered online."""
        if self.status != "online":
            return False
        
        time_since_last_seen = datetime.utcnow() - self.last_seen
        return time_since_last_seen.total_seconds() <= timeout_seconds
    
    def can_accept_task(self) -> bool:
        """Check if parser can accept new tasks."""
        return (
            self.is_online() and 
            self.current_tasks < self.max_concurrent_tasks
        )


# Custom exceptions for scheduler
class SchedulerError(Exception):
    """Base scheduler error."""
    
    def __init__(self, message: str, task_id: Optional[str] = None, details: Optional[dict[str, str]] = None):
        self.message = message
        self.task_id = task_id
        self.details = details or {}
        super().__init__(message)


class TaskValidationError(SchedulerError):
    """Task validation errors."""
    pass


class TaskExecutionError(SchedulerError):
    """Task execution errors."""
    pass


class ParserUnavailableError(SchedulerError):
    """Parser not available for task execution."""
    pass


class QueueError(SchedulerError):
    """Redis Queue operation errors."""
    pass


# Export all models and exceptions
__all__ = [
    # Enums
    "TaskStatus",
    "TaskPriority", 
    "ScheduleType",
    "TaskExecutionMode",
    
    # Models
    "CronExpression",
    "TaskParameters",
    "TaskRetryConfig", 
    "ScheduledTask",
    "TaskQueue",
    "TaskExecutionResult",
    "ParserStatus",
    
    # Exceptions
    "SchedulerError",
    "TaskValidationError",
    "TaskExecutionError",
    "ParserUnavailableError",
    "QueueError"
]
