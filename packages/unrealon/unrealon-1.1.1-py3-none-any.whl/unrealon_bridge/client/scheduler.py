"""
Scheduler client mixin for Parser Bridge Client.

Provides scheduler-related functionality for parsers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from unrealon_rpc.logging import get_logger
from unrealon_bridge.models.scheduler import (
    ScheduledTask,
    TaskParameters,
    CronExpression,
    TaskRetryConfig,
    TaskExecutionResult,
    ParserStatus,
    SchedulerError,
)

logger = get_logger(__name__)


class SchedulerMixin:
    """Scheduler functionality mixin for Parser Bridge Client."""

    async def create_scheduled_task(
        self,
        task_type: str,
        parameters: TaskParameters,
        cron_expression: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        retry_config: Optional[TaskRetryConfig] = None,
        priority: int = 5,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Create a new scheduled task.
        
        Args:
            task_type: Type of task (command, scrape, parse, etc.)
            parameters: Task parameters
            cron_expression: Optional cron expression for recurring tasks
            scheduled_at: Optional specific execution time
            retry_config: Optional retry configuration
            priority: Task priority (1-10, higher = more important)
            timeout_seconds: Task timeout in seconds
            
        Returns:
            Task creation response with task_id and scheduling info
        """
        try:
            request_data = {
                "parser_id": self.parser_id,
                "task_type": task_type,
                "parameters": parameters.model_dump(),
                "priority": priority,
                "timeout_seconds": timeout_seconds
            }
            
            if cron_expression:
                request_data["cron_expression"] = cron_expression
            
            if scheduled_at:
                request_data["scheduled_at"] = scheduled_at.isoformat()
            
            if retry_config:
                request_data["retry_config"] = retry_config.model_dump()
            
            response = await self.bridge_client.call_rpc(
                method="scheduler.create_task",
                params=request_data,
                timeout=30
            )
            
            logger.info(
                f"Created scheduled task: {task_type}",
                component="scheduler_client",
                operation="create_task",
                parser_id=self.parser_id,
                task_type=task_type,
                cron_expression=cron_expression
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to create scheduled task: {e}",
                component="scheduler_client",
                operation="create_task",
                error=e
            )
            raise SchedulerError(f"Failed to create scheduled task: {e}")

    async def list_scheduled_tasks(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List scheduled tasks for this parser.
        
        Args:
            task_type: Optional filter by task type
            status: Optional filter by status
            limit: Maximum number of tasks to return
            offset: Offset for pagination
            
        Returns:
            List of scheduled tasks
        """
        try:
            request_data = {
                "parser_id": self.parser_id,
                "limit": limit,
                "offset": offset
            }
            
            if task_type:
                request_data["task_type"] = task_type
            
            if status:
                request_data["status"] = status
            
            response = await self.bridge_client.call_rpc(
                method="scheduler.list_tasks",
                params=request_data,
                timeout=30
            )
            
            logger.info(
                f"Listed scheduled tasks: {response.get('total_count', 0)} total",
                component="scheduler_client",
                operation="list_tasks",
                parser_id=self.parser_id,
                task_type=task_type,
                status=status
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to list scheduled tasks: {e}",
                component="scheduler_client",
                operation="list_tasks",
                error=e
            )
            raise SchedulerError(f"Failed to list scheduled tasks: {e}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status and execution history.
        
        Args:
            task_id: Task ID to query
            
        Returns:
            Task status and execution history
        """
        try:
            response = await self.bridge_client.call_rpc(
                method="scheduler.get_task",
                params={"task_id": task_id},
                timeout=30
            )
            
            logger.info(
                f"Retrieved task status: {task_id}",
                component="scheduler_client",
                operation="get_task",
                task_id=task_id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to get task status: {e}",
                component="scheduler_client",
                operation="get_task",
                error=e
            )
            raise SchedulerError(f"Failed to get task status: {e}")

    async def cancel_scheduled_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            Cancellation response
        """
        try:
            response = await self.bridge_client.call_rpc(
                method="scheduler.cancel_task",
                params={"task_id": task_id},
                timeout=30
            )
            
            logger.info(
                f"Cancelled scheduled task: {task_id}",
                component="scheduler_client",
                operation="cancel_task",
                task_id=task_id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to cancel scheduled task: {e}",
                component="scheduler_client",
                operation="cancel_task",
                error=e
            )
            raise SchedulerError(f"Failed to cancel scheduled task: {e}")

    async def update_parser_status_for_scheduler(
        self,
        status: str,
        current_task_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update parser status for scheduler.
        
        Args:
            status: Parser status (online, offline, busy, error)
            current_task_id: Currently executing task ID
            capabilities: Parser capabilities
            
        Returns:
            Status update response
        """
        try:
            request_data = {
                "parser_id": self.parser_id,
                "status": status,
                "last_seen": datetime.utcnow().isoformat()
            }
            
            if current_task_id:
                request_data["current_task_id"] = current_task_id
            
            if capabilities:
                request_data["capabilities"] = capabilities
            
            response = await self.bridge_client.call_rpc(
                method="scheduler.update_parser_status",
                params=request_data,
                timeout=30
            )
            
            logger.info(
                f"Updated parser status for scheduler: {status}",
                component="scheduler_client",
                operation="update_parser_status",
                parser_id=self.parser_id,
                status=status
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to update parser status: {e}",
                component="scheduler_client",
                operation="update_parser_status",
                error=e
            )
            raise SchedulerError(f"Failed to update parser status: {e}")

    async def get_parser_scheduler_status(self) -> Dict[str, Any]:
        """
        Get parser status and active tasks from scheduler.
        
        Returns:
            Parser status and active tasks
        """
        try:
            response = await self.bridge_client.call_rpc(
                method="scheduler.get_parser_status",
                params={"parser_id": self.parser_id},
                timeout=30
            )
            
            logger.info(
                f"Retrieved parser scheduler status",
                component="scheduler_client",
                operation="get_parser_status",
                parser_id=self.parser_id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to get parser scheduler status: {e}",
                component="scheduler_client",
                operation="get_parser_status",
                error=e
            )
            raise SchedulerError(f"Failed to get parser scheduler status: {e}")

    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.
        
        Returns:
            Scheduler statistics
        """
        try:
            response = await self.bridge_client.call_rpc(
                method="scheduler.get_stats",
                params={},
                timeout=30
            )
            
            logger.info(
                "Retrieved scheduler statistics",
                component="scheduler_client",
                operation="get_stats"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to get scheduler stats: {e}",
                component="scheduler_client",
                operation="get_stats",
                error=e
            )
            raise SchedulerError(f"Failed to get scheduler stats: {e}")

    # Convenience methods for common task types
    
    async def schedule_scraping_task(
        self,
        target_url: str,
        scraping_config: Dict[str, Any],
        cron_expression: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Schedule a scraping task.
        
        Args:
            target_url: URL to scrape
            scraping_config: Scraping configuration
            cron_expression: Optional cron expression for recurring scraping
            scheduled_at: Optional specific execution time
            priority: Task priority
            
        Returns:
            Task creation response
        """
        parameters = TaskParameters(
            command_type="scrape",
            parameters={
                "target_url": target_url,
                **{k: str(v) for k, v in scraping_config.items()}
            }
        )
        
        return await self.create_scheduled_task(
            task_type="scrape",
            parameters=parameters,
            cron_expression=cron_expression,
            scheduled_at=scheduled_at,
            priority=priority
        )

    async def schedule_parsing_task(
        self,
        input_data: str,
        parsing_config: Dict[str, Any],
        cron_expression: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Schedule a parsing task.
        
        Args:
            input_data: Data to parse
            parsing_config: Parsing configuration
            cron_expression: Optional cron expression for recurring parsing
            scheduled_at: Optional specific execution time
            priority: Task priority
            
        Returns:
            Task creation response
        """
        parameters = TaskParameters(
            command_type="parse",
            parameters={
                "input_data": input_data,
                **{k: str(v) for k, v in parsing_config.items()}
            }
        )
        
        return await self.create_scheduled_task(
            task_type="parse",
            parameters=parameters,
            cron_expression=cron_expression,
            scheduled_at=scheduled_at,
            priority=priority
        )

    async def schedule_command_task(
        self,
        command_type: str,
        command_params: Dict[str, Any],
        cron_expression: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Schedule a command execution task.
        
        Args:
            command_type: Type of command to execute
            command_params: Command parameters
            cron_expression: Optional cron expression for recurring commands
            scheduled_at: Optional specific execution time
            priority: Task priority
            
        Returns:
            Task creation response
        """
        parameters = TaskParameters(
            command_type=command_type,
            parameters={k: str(v) for k, v in command_params.items()}
        )
        
        return await self.create_scheduled_task(
            task_type="command",
            parameters=parameters,
            cron_expression=cron_expression,
            scheduled_at=scheduled_at,
            priority=priority
        )
