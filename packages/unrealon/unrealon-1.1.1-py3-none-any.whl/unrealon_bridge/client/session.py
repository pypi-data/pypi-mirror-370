"""
Session management for Parser Bridge Client.
"""

from typing import Optional
from unrealon_rpc.logging import get_logger

from ..models import (
    SessionStartRequest, SessionStartResponse,
    SessionEndRequest, SessionEndResponse
)

logger = get_logger(__name__)


class SessionMixin:
    """Mixin for session management functionality."""

    async def start_session(self, session_type: str = "default", metadata: Optional[dict[str, str]] = None) -> str:
        """
        Start a new parser session.

        Args:
            session_type: Type of session
            metadata: Session metadata

        Returns:
            Session ID
        """
        self._ensure_registered()

        request = SessionStartRequest(
            parser_id=self.parser_id,
            session_type=session_type,
            metadata=metadata
        )

        result = await self.bridge_client.call_rpc(
            method="parser.start_session", 
            params=request.model_dump()
        )

        response = SessionStartResponse.model_validate(result)
        
        if response.success and response.session:
            self.session_id = response.session.session_id
            logger.info(f"Session started: {self.session_id}")
            return self.session_id
        else:
            raise RuntimeError(f"Session start failed: {response.error}")

    async def end_session(self) -> None:
        """End current parser session."""
        if not self.session_id:
            return

        request = SessionEndRequest(session_id=self.session_id)

        result = await self.bridge_client.call_rpc(
            method="parser.end_session", 
            params=request.model_dump()
        )

        response = SessionEndResponse.model_validate(result)
        
        if response.success:
            logger.info(f"Session ended: {self.session_id}")
            self.session_id = None
        else:
            logger.error(f"Session end failed: {response.error}")
