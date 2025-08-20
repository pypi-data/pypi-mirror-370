"""
Health monitoring for Parser Bridge Client.
"""

from unrealon_rpc.logging import get_logger

from ..models import (
    ParserHealth, ParserHealthRequest, ParserHealthResponse
)

logger = get_logger(__name__)


class HealthMixin:
    """Mixin for health monitoring functionality."""

    async def get_health(self) -> ParserHealth:
        """
        Get parser health information.

        Returns:
            Parser health status
        """
        self._ensure_registered()

        request = ParserHealthRequest(parser_id=self.parser_id)
        
        result = await self.bridge_client.call_rpc(
            method="parser.get_health", 
            params=request.model_dump()
        )

        response = ParserHealthResponse.model_validate(result)
        
        if response.success and response.health:
            return response.health
        else:
            raise RuntimeError(f"Health check failed: {response.error}")
