"""
Command-related RPC handlers.
"""

import uuid
from unrealon_rpc.logging import get_logger

from ...models import (
    ParserCommand, CommandResult,
    CommandExecuteRequest, CommandExecuteResponse,
    CommandCreateRequest, CommandCreateResponse,
    CommandStatusRequest, CommandStatusResponse
)

logger = get_logger(__name__)


class CommandHandlers:
    """Handlers for command-related RPC operations."""

    async def handle_command_execute(self, parser_id: str, command_type: str, parameters: dict, timeout: int = 30) -> dict:
        """Handle command execution."""
        try:
            # Create request object for validation
            request = CommandExecuteRequest(
                parser_id=parser_id,
                command_type=command_type,
                parameters=parameters,
                timeout=timeout
            )
            
            command = ParserCommand(
                command_id=str(uuid.uuid4()),
                command_type=request.command_type,
                parser_id=request.parser_id,
                parameters=request.parameters,
                timeout=request.timeout
            )
            self.commands[command.command_id] = command

            # Forward command to daemon via WebSocket
            daemon_client = self.get_client_by_parser_id(parser_id)
            if daemon_client:
                logger.info(f"📤 Forwarding command {command.command_type} to daemon {parser_id}")
                # Send command via WebSocket
                command_message = {
                    "message_type": "command",
                    "command_id": command.command_id,
                    "command_type": command.command_type,
                    "parameters": command.parameters,
                    "parser_id": parser_id
                }
                await daemon_client.send_message(command_message)
                # For now, return mock response - daemon should respond via WebSocket later
                result_data = {
                    "command_type": command.command_type,
                    "status": "forwarded_to_daemon",
                    "parser_id": parser_id
                }
            else:
                logger.warning(f"⚠️ No daemon found for parser {parser_id}")
                # Fallback to local handlers
                handler = self.command_handlers.get(command.command_type)
                if handler:
                    logger.info(f"🔧 Using local handler for {command.command_type}")
                    result_data = await handler(command)
                else:
                    logger.warning(f"⚠️ No handler found for {command.command_type}")
                    result_data = {"error": f"No daemon connected for parser {parser_id}"}

            result = CommandResult(
                command_id=command.command_id,
                success=True,
                result_data=result_data,
                execution_time=0.5
            )

            logger.info(f"Command executed: {command.command_id} ({command.command_type})")

            response = CommandExecuteResponse(success=True, result=result)
            return response.model_dump(mode='json')

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            response = CommandExecuteResponse(success=False, error=str(e))
            return response.model_dump(mode='json')

    async def handle_command_create(self, request: CommandCreateRequest) -> CommandCreateResponse:
        """Handle command creation."""
        try:
            command = ParserCommand(
                command_id=str(uuid.uuid4()),
                command_type=request.command_type,
                parser_id=request.parser_id,
                parameters=request.parameters
            )
            self.commands[command.command_id] = command

            return CommandCreateResponse(success=True, command=command)
        except Exception as e:
            return CommandCreateResponse(success=False, error=str(e))

    async def handle_command_get_status(self, request: CommandStatusRequest) -> CommandStatusResponse:
        """Handle command status request."""
        command = self.commands.get(request.command_id)

        if not command:
            return CommandStatusResponse(success=False, error=f"Command {request.command_id} not found")

        return CommandStatusResponse(success=True, command=command)
