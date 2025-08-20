"""
Parser logging functionality for Parser Bridge Client.

Provides methods for sending parser logs to Django via WebSocket/Redis.
"""

from typing import Optional, Dict
from datetime import datetime
from unrealon_rpc.logging import get_logger

from ..models import ParserLogEntry, ParserLogResponse

logger = get_logger(__name__)


class LoggingMixin:
    """Mixin for parser logging functionality."""

    async def send_log(
        self,
        level: str,
        message: str,
        session_id: Optional[str] = None,
        command_id: Optional[str] = None,
        url: Optional[str] = None,
        operation: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
        error_details: Optional[str] = None
    ) -> bool:
        """
        Send log entry to Django via WebSocket/Redis.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            session_id: Parser session ID (optional)
            command_id: Command ID if related to command (optional)
            url: URL being processed (optional)
            operation: Operation being performed (optional)
            data: Additional log data (optional)
            error_details: Error details if error log (optional)

        Returns:
            True if log was sent successfully, False otherwise

        Example:
            ```python
            # Send info log
            await client.send_log("INFO", "Started parsing product page")
            
            # Send error log with details
            await client.send_log(
                "ERROR", 
                "Failed to parse product price",
                url="https://example.com/product/123",
                operation="price_extraction",
                error_details="Price element not found in DOM"
            )
            
            # Send log with session context
            await client.send_log(
                "DEBUG",
                "Processing page 5 of search results", 
                session_id=self.session_id,
                operation="pagination"
            )
            ```
        """
        if not self.registered:
            logger.warning("Cannot send log - parser not registered")
            return False

        try:
            log_entry = ParserLogEntry(
                parser_id=self.parser_id,
                level=level.upper(),
                message=message,
                session_id=session_id,
                command_id=command_id,
                url=url,
                operation=operation,
                data=data or {},
                error_details=error_details
            )
            
            response_dict = await self.bridge_client.call_rpc(
                method="parser.log",
                params=log_entry.model_dump()
            )

            response = ParserLogResponse.model_validate(response_dict)
            
            if response.success:
                logger.debug(f"Log sent to Django: {level} - {message}")
                return True
            else:
                logger.error(f"Failed to send log to Django: {response.error}")
                return False

        except Exception as e:
            logger.error(f"Log sending failed: {e}")
            return False

    async def log_debug(self, message: str, **kwargs) -> bool:
        """Send DEBUG level log."""
        return await self.send_log("DEBUG", message, **kwargs)

    async def log_info(self, message: str, **kwargs) -> bool:
        """Send INFO level log."""
        return await self.send_log("INFO", message, **kwargs)

    async def log_warning(self, message: str, **kwargs) -> bool:
        """Send WARNING level log."""
        return await self.send_log("WARNING", message, **kwargs)

    async def log_error(self, message: str, **kwargs) -> bool:
        """Send ERROR level log."""
        return await self.send_log("ERROR", message, **kwargs)

    async def log_critical(self, message: str, **kwargs) -> bool:
        """Send CRITICAL level log."""
        return await self.send_log("CRITICAL", message, **kwargs)

    async def log_operation_start(self, operation: str, **kwargs) -> bool:
        """Log the start of an operation."""
        return await self.log_info(f"Started {operation}", operation=operation, **kwargs)

    async def log_operation_end(self, operation: str, **kwargs) -> bool:
        """Log the end of an operation."""
        return await self.log_info(f"Completed {operation}", operation=operation, **kwargs)

    async def log_operation_error(self, operation: str, error: str, **kwargs) -> bool:
        """Log an operation error."""
        return await self.log_error(
            f"Failed {operation}: {error}", 
            operation=operation, 
            error_details=error,
            **kwargs
        )
