"""
Scheduler RPC handlers for Parser Bridge Server.

Handles scheduler-related RPC operations including task management,
cron scheduling, and parser status tracking.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from unrealon_rpc.logging import get_logger
from unrealon_bridge.models.scheduler import (
    ScheduledTask,
    TaskParameters,
    TaskPriority,
    ScheduleType,
    CronExpression,
    TaskRetryConfig,
    TaskExecutionResult,
    ParserStatus,
    TaskQueue,
    SchedulerError,
    TaskValidationError,
    TaskExecutionError,
)
from unrealon_bridge.models.responses import BaseRPCResponse

logger = get_logger(__name__)


class SchedulerTaskCreateResponse(BaseRPCResponse):
    """Response for task creation."""
    task_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    next_run: Optional[datetime] = None


class SchedulerTaskListResponse(BaseRPCResponse):
    """Response for task listing."""
    tasks: List[ScheduledTask]
    total_count: int


class SchedulerTaskStatusResponse(BaseRPCResponse):
    """Response for task status."""
    task: ScheduledTask
    execution_history: List[TaskExecutionResult]


class SchedulerParserStatusResponse(BaseRPCResponse):
    """Response for parser status."""
    parser_status: ParserStatus
    active_tasks: List[str]


class SchedulerStatsResponse(BaseRPCResponse):
    """Response for scheduler statistics."""
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    parsers_online: int
    parsers_offline: int


# In-memory storage for demonstration (in production, use Redis/Database)
_scheduled_tasks: Dict[str, ScheduledTask] = {}
_parser_statuses: Dict[str, ParserStatus] = {}
_task_execution_history: Dict[str, List[TaskExecutionResult]] = {}


class SchedulerHandlers:
    """Scheduler RPC handlers."""
    
    async def handle_scheduler_create_task(self, parser_id: str, task_type: str, parameters: dict, cron_expression: str = None, scheduled_at: str = None, retry_config: dict = None, priority: int = 5, timeout_seconds: int = 300, api_key: str = None) -> Dict[str, Any]:
        """Create a new scheduled task."""
        return await handle_scheduler_create_task(parser_id, task_type, parameters, cron_expression, scheduled_at, retry_config, priority, timeout_seconds, api_key)
    
    async def handle_scheduler_list_tasks(self, parser_id: str = None, task_type: str = None, status: str = None, limit: int = 100, offset: int = 0, api_key: str = None) -> Dict[str, Any]:
        """List scheduled tasks."""
        return await handle_scheduler_list_tasks(parser_id, task_type, status, limit, offset, api_key)
    
    async def handle_scheduler_get_task(self, **params) -> Dict[str, Any]:
        """Get task status and execution history."""
        return await handle_scheduler_get_task(**params)
    
    async def handle_scheduler_cancel_task(self, **params) -> Dict[str, Any]:
        """Cancel a scheduled task."""
        return await handle_scheduler_cancel_task(**params)
    
    async def handle_scheduler_update_parser_status(self, parser_id: str, status: str, last_seen: str = None, current_task_id: str = None, capabilities: list = None, api_key: str = None) -> Dict[str, Any]:
        """Update parser status for scheduler."""
        return await handle_scheduler_update_parser_status(parser_id, status, last_seen, current_task_id, capabilities, api_key)
    
    async def handle_scheduler_get_parser_status(self, **params) -> Dict[str, Any]:
        """Get parser status and active tasks."""
        return await handle_scheduler_get_parser_status(**params)
    
    async def handle_scheduler_get_stats(self, api_key: str = None) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return await handle_scheduler_get_stats(api_key)


async def handle_scheduler_create_task(parser_id: str, task_type: str, parameters: dict, cron_expression: str = None, scheduled_at: str = None, retry_config: dict = None, priority: int = 5, timeout_seconds: int = 300, api_key: str = None) -> Dict[str, Any]:
    """
    Create a new scheduled task.
    
    Expected params:
        parser_id: str
        task_type: str (command, scrape, parse, etc.)
        parameters: TaskParameters
        cron_expression: Optional[str]
        scheduled_at: Optional[datetime]
        retry_config: Optional[TaskRetryConfig]
        priority: Optional[int]
        timeout_seconds: Optional[int]
        api_key: Optional[str]
    """
    try:
        # Validate required parameters
        if not parser_id or not task_type:
            return SchedulerTaskCreateResponse(
                success=False,
                error="parser_id and task_type are required"
            ).model_dump(mode='json')
        
        # Create TaskParameters
        try:
            task_parameters = TaskParameters.model_validate(parameters)
        except Exception as e:
            raise TaskValidationError(f"Invalid task parameters: {e}")
        
        # Handle cron expression if provided
        cron_expr = None
        if cron_expression:
            try:
                cron_expr = CronExpression(expression=cron_expression)
            except Exception as e:
                raise TaskValidationError(f"Invalid cron expression: {e}")
        
        # Handle retry config if provided
        retry_cfg = None
        if retry_config:
            try:
                retry_cfg = TaskRetryConfig.model_validate(retry_config)
            except Exception as e:
                raise TaskValidationError(f"Invalid retry config: {e}")
        
        # Handle scheduled_at if provided
        scheduled_datetime = None
        if scheduled_at:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_at)
            except Exception as e:
                raise TaskValidationError(f"Invalid scheduled_at format: {e}")
        
        # Determine schedule type
        if cron_expr:
            schedule_type = ScheduleType.RECURRING
        elif scheduled_datetime:
            schedule_type = ScheduleType.DELAYED
        else:
            schedule_type = ScheduleType.IMMEDIATE
        
        # Create scheduled task
        task_data = {
            "task_name": f"{task_type}_{parser_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "parser_type": task_type,  # Using task_type as parser_type for now
            "parser_id": parser_id,
            "task_parameters": task_parameters,
            "priority": TaskPriority(priority) if priority in [1, 3, 5, 7, 9] else TaskPriority.NORMAL,
            "schedule_type": schedule_type,
        }
        
        # Add optional fields based on schedule type
        if cron_expr:
            task_data["cron_schedule"] = cron_expr
        if scheduled_datetime:
            task_data["scheduled_at"] = scheduled_datetime
        if retry_cfg:
            task_data["retry_config"] = retry_cfg
        
        task = ScheduledTask(**task_data)
        
        # Store task
        _scheduled_tasks[task.task_id] = task
        _task_execution_history[task.task_id] = []
        
        logger.info(
            f"Created scheduled task: {task.task_id}",
            component="scheduler",
            operation="create_task",
            parser_id=parser_id,
            task_type=task_type,
            api_key=api_key[:8] + "..." if api_key else None
        )
        
        return SchedulerTaskCreateResponse(
            success=True,
            task_id=task.task_id,
            scheduled_at=task.scheduled_at,
            next_run=task.scheduled_at  # For now, use scheduled_at as next_run
        ).model_dump(mode='json')
        
    except (TaskValidationError, SchedulerError) as e:
        logger.error(f"Task creation failed: {e}", component="scheduler", operation="create_task")
        return SchedulerTaskCreateResponse(
            success=False,
            error=str(e)
        ).model_dump(mode='json')
    except Exception as e:
        logger.error(f"Unexpected error creating task: {e}", component="scheduler", operation="create_task", error=e)
        return SchedulerTaskCreateResponse(
            success=False,
            error="Internal server error"
        ).model_dump(mode='json')


async def handle_scheduler_list_tasks(parser_id: str = None, task_type: str = None, status: str = None, limit: int = 100, offset: int = 0, api_key: str = None) -> Dict[str, Any]:
    """
    List scheduled tasks.
    
    Expected params:
        parser_id: Optional[str] - filter by parser
        task_type: Optional[str] - filter by task type
        status: Optional[str] - filter by status
        limit: Optional[int] - limit results
        offset: Optional[int] - offset for pagination
        api_key: Optional[str]
    """
    try:
        
        # Filter tasks
        filtered_tasks = []
        for task in _scheduled_tasks.values():
            if parser_id and task.parser_id != parser_id:
                continue
            if task_type and task.task_type != task_type:
                continue
            if status and task.status != status:
                continue
            filtered_tasks.append(task)
        
        # Sort by created_at (newest first)
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply pagination
        total_count = len(filtered_tasks)
        paginated_tasks = filtered_tasks[offset:offset + limit]
        
        logger.info(
            f"Listed {len(paginated_tasks)} tasks (total: {total_count})",
            component="scheduler",
            operation="list_tasks",
            parser_id=parser_id,
            task_type=task_type,
            status=status
        )
        
        return SchedulerTaskListResponse(
            success=True,
            tasks=paginated_tasks,
            total_count=total_count
        ).model_dump(mode='json')
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}", component="scheduler", operation="list_tasks", error=e)
        return SchedulerTaskListResponse(
            success=False,
            error="Internal server error",
            tasks=[],
            total_count=0
        ).model_dump(mode='json')


async def handle_scheduler_get_task(**params) -> Dict[str, Any]:
    """
    Get task status and execution history.
    
    Expected params:
        task_id: str
        api_key: Optional[str]
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return SchedulerTaskStatusResponse(
                success=False,
                error="task_id is required",
                task=None,
                execution_history=[]
            ).model_dump(mode='json')
        
        task = _scheduled_tasks.get(task_id)
        if not task:
            raise TaskExecutionError(f"Task not found: {task_id}")
        
        execution_history = _task_execution_history.get(task_id, [])
        
        logger.info(
            f"Retrieved task: {task_id}",
            component="scheduler",
            operation="get_task",
            task_status=task.status
        )
        
        return SchedulerTaskStatusResponse(
            success=True,
            task=task,
            execution_history=execution_history
        ).model_dump(mode='json')
        
    except TaskExecutionError as e:
        logger.warning(f"Task not found: {e}", component="scheduler", operation="get_task")
        return SchedulerTaskStatusResponse(
            success=False,
            error=str(e),
            task=None,
            execution_history=[]
        ).model_dump(mode='json')
    except Exception as e:
        logger.error(f"Error getting task: {e}", component="scheduler", operation="get_task", error=e)
        return SchedulerTaskStatusResponse(
            success=False,
            error="Internal server error",
            task=None,
            execution_history=[]
        ).model_dump(mode='json')


async def handle_scheduler_cancel_task(**params) -> Dict[str, Any]:
    """
    Cancel a scheduled task.
    
    Expected params:
        task_id: str
        api_key: Optional[str]
    """
    try:
        task_id = params.get("task_id")
        if not task_id:
            return BaseRPCResponse(
                success=False,
                error="task_id is required"
            ).model_dump(mode='json')
        
        task = _scheduled_tasks.get(task_id)
        if not task:
            raise TaskExecutionError(f"Task not found: {task_id}")
        
        # Update task status
        task.status = "cancelled"
        task.updated_at = datetime.utcnow()
        
        logger.info(
            f"Cancelled task: {task_id}",
            component="scheduler",
            operation="cancel_task",
            parser_id=task.parser_id
        )
        
        return BaseRPCResponse(
            success=True,
            message=f"Task {task_id} cancelled successfully"
        ).model_dump(mode='json')
        
    except TaskExecutionError as e:
        logger.warning(f"Task not found: {e}", component="scheduler", operation="cancel_task")
        return BaseRPCResponse(
            success=False,
            error=str(e)
        ).model_dump(mode='json')
    except Exception as e:
        logger.error(f"Error cancelling task: {e}", component="scheduler", operation="cancel_task", error=e)
        return BaseRPCResponse(
            success=False,
            error="Internal server error"
        ).model_dump(mode='json')


async def handle_scheduler_update_parser_status(parser_id: str, status: str, last_seen: str = None, current_task_id: str = None, capabilities: list = None, api_key: str = None) -> Dict[str, Any]:
    """
    Update parser status for scheduler.
    
    Expected params:
        parser_id: str
        status: str (online, offline, busy, error)
        last_seen: Optional[datetime]
        current_task_id: Optional[str]
        capabilities: Optional[List[str]]
        api_key: Optional[str]
    """
    try:
        if not parser_id or not status:
            return BaseRPCResponse(
                success=False,
                error="parser_id and status are required"
            ).model_dump(mode='json')
        
        # Handle last_seen
        last_seen_datetime = datetime.utcnow()
        if last_seen:
            try:
                last_seen_datetime = datetime.fromisoformat(last_seen)
            except Exception:
                pass  # Use current time if parsing fails
        
        # Create or update parser status
        parser_status = ParserStatus(
            parser_id=parser_id,
            parser_type="generic",  # Default parser type
            status=status,
            last_seen=last_seen_datetime,
            capabilities=capabilities or []
        )
        
        _parser_statuses[parser_id] = parser_status
        
        logger.info(
            f"Updated parser status: {parser_id} -> {status}",
            component="scheduler",
            operation="update_parser_status",
            parser_id=parser_id,
            status=status
        )
        
        return BaseRPCResponse(
            success=True,
            message=f"Parser {parser_id} status updated to {status}"
        ).model_dump(mode='json')
        
    except Exception as e:
        logger.error(f"Error updating parser status: {e}", component="scheduler", operation="update_parser_status", error=e)
        return BaseRPCResponse(
            success=False,
            error="Internal server error"
        ).model_dump(mode='json')


async def handle_scheduler_get_parser_status(**params) -> Dict[str, Any]:
    """
    Get parser status and active tasks.
    
    Expected params:
        parser_id: str
        api_key: Optional[str]
    """
    try:
        parser_id = params.get("parser_id")
        if not parser_id:
            return SchedulerParserStatusResponse(
                success=False,
                error="parser_id is required",
                parser_status=None,
                active_tasks=[]
            ).model_dump(mode='json')
        
        parser_status = _parser_statuses.get(parser_id)
        if not parser_status:
            return SchedulerParserStatusResponse(
                success=False,
                error=f"Parser not found: {parser_id}",
                parser_status=None,
                active_tasks=[]
            ).model_dump(mode='json')
        
        # Find active tasks for this parser
        active_tasks = []
        for task in _scheduled_tasks.values():
            if task.parser_id == parser_id and task.status in ["pending", "running"]:
                active_tasks.append(task.task_id)
        
        logger.info(
            f"Retrieved parser status: {parser_id}",
            component="scheduler",
            operation="get_parser_status",
            parser_status=parser_status.status,
            active_tasks_count=len(active_tasks)
        )
        
        return SchedulerParserStatusResponse(
            success=True,
            parser_status=parser_status,
            active_tasks=active_tasks
        ).model_dump(mode='json')
        
    except Exception as e:
        logger.error(f"Error getting parser status: {e}", component="scheduler", operation="get_parser_status", error=e)
        return SchedulerParserStatusResponse(
            success=False,
            error="Internal server error",
            parser_status=None,
            active_tasks=[]
        ).model_dump(mode='json')


async def handle_scheduler_get_stats(api_key: str = None) -> Dict[str, Any]:
    """
    Get scheduler statistics.
    
    Expected params:
        api_key: Optional[str]
    """
    try:
        # Count tasks by status
        total_tasks = len(_scheduled_tasks)
        active_tasks = sum(1 for task in _scheduled_tasks.values() if task.status in ["pending", "running"])
        completed_tasks = sum(1 for task in _scheduled_tasks.values() if task.status == "completed")
        failed_tasks = sum(1 for task in _scheduled_tasks.values() if task.status == "failed")
        
        # Count parsers by status
        parsers_online = sum(1 for parser in _parser_statuses.values() if parser.status == "online")
        parsers_offline = sum(1 for parser in _parser_statuses.values() if parser.status == "offline")
        
        logger.info(
            "Retrieved scheduler statistics",
            component="scheduler",
            operation="get_stats",
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            parsers_online=parsers_online
        )
        
        return SchedulerStatsResponse(
            success=True,
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            parsers_online=parsers_online,
            parsers_offline=parsers_offline
        ).model_dump(mode='json')
        
    except Exception as e:
        logger.error(f"Error getting scheduler stats: {e}", component="scheduler", operation="get_stats", error=e)
        return SchedulerStatsResponse(
            success=False,
            error="Internal server error",
            total_tasks=0,
            active_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            parsers_online=0,
            parsers_offline=0
        ).model_dump(mode='json')
