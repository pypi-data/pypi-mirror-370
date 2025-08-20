"""
Parser logging RPC handlers.

Handles parser log entries sent from parsers to Django.
"""

from typing import Optional
from unrealon_rpc.logging import get_logger

from ...models import ParserLogEntry, ParserLogRequest, ParserLogResponse

logger = get_logger(__name__)


class LoggingHandlers:
    """Handlers for parser logging RPC operations."""

    def __init__(self) -> None:
        """Initialize logging handlers."""
        pass

    async def handle_parser_log(
        self,
        parser_id: str,
        level: str,
        message: str,
        session_id: Optional[str] = None,
        command_id: Optional[str] = None,
        url: Optional[str] = None,
        operation: Optional[str] = None,
        data: Optional[dict] = None,
        error_details: Optional[str] = None
    ) -> dict:
        """
        Handle parser log entry.
        
        Receives log from parser and forwards to Django for storage/processing.
        
        Args:
            parser_id: ID of the parser sending the log
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            session_id: Parser session ID (optional)
            command_id: Command ID if related to command (optional)
            url: URL being processed (optional)
            operation: Operation being performed (optional)
            data: Additional log data (optional)
            error_details: Error details if error log (optional)
            
        Returns:
            ParserLogResponse as dict with success status
        """
        try:
            # Create and validate log entry
            log_entry = ParserLogEntry(
                parser_id=parser_id,
                level=level,
                message=message,
                session_id=session_id,
                command_id=command_id,
                url=url,
                operation=operation,
                data=data or {},
                error_details=error_details
            )
            
            # Log locally for debugging
            local_logger_method = getattr(logger, level.lower(), logger.info)
            local_logger_method(
                f"Parser {parser_id} log: {message}",
                component="parser_log",
                operation=operation
            )
            
            # Django will receive this RPC call via Redis and handle the log
            
            response = ParserLogResponse(
                success=True,
                message="Log entry received and forwarded to Django"
            )
            
            return response.model_dump(mode='json')
            
        except Exception as e:
            logger.error(f"Failed to handle parser log from {parser_id}: {e}")
            
            response = ParserLogResponse(
                success=False,
                error=str(e),
                message="Failed to process log entry"
            )
            
            return response.model_dump(mode='json')


