"""
Command execution for Parser Bridge Client.
"""

import uuid
from typing import Optional
from datetime import datetime
from unrealon_rpc.logging import get_logger

from ..models import (
    CommandResult, CommandExecuteRequest, CommandExecuteResponse
)

logger = get_logger(__name__)


class CommandsMixin:
    """Mixin for command execution functionality."""

    async def execute_command(self, command_type: str, parameters: Optional[dict[str, str]] = None, timeout: int = 300) -> CommandResult:
        """
        Execute a parser command.

        Args:
            command_type: Type of command to execute
            parameters: Command parameters
            timeout: Command timeout in seconds

        Returns:
            Command execution result
        """
        self._ensure_registered()

        request = CommandExecuteRequest(
            command_type=command_type,
            parser_id=self.parser_id,
            parameters=parameters or {},
            timeout=timeout
        )

        started_at = datetime.now()

        try:
            result = await self.bridge_client.call_rpc(
                method="parser.execute_command", 
                params=request.model_dump(), 
                timeout=timeout
            )

            response = CommandExecuteResponse.model_validate(result)
            
            if response.success and response.result:
                execution_time = (datetime.now() - started_at).total_seconds()
                
                # Log command completion
                await self._log_command_event(
                    event_type="command_completed", 
                    message=f"Command {command_type} completed",
                    data={"command_type": command_type, "execution_time": str(execution_time)}
                )

                return response.result
            else:
                raise RuntimeError(f"Command execution failed: {response.error}")

        except Exception as e:
            execution_time = (datetime.now() - started_at).total_seconds()
            
            # Create error result
            command_result = CommandResult(
                command_id=str(uuid.uuid4()),
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )

            # Log command error
            await self._log_command_event(
                event_type="command_failed", 
                level="error", 
                message=f"Command {command_type} failed: {str(e)}"
            )

            return command_result

    async def _log_command_event(self, event_type: str, message: str, level: str = "info", data: Optional[dict[str, str]] = None) -> None:
        """Log command-related event."""
        # Event logging will be handled by the main client
        pass
