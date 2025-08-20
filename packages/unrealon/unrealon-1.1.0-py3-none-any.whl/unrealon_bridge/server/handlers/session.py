"""
Session-related RPC handlers.
"""

import uuid
from datetime import datetime
from unrealon_rpc.logging import get_logger

from ...models import (
    ParserSession,
    SessionStartRequest, SessionStartResponse,
    SessionEndRequest, SessionEndResponse
)

logger = get_logger(__name__)


class SessionHandlers:
    """Handlers for session-related RPC operations."""

    async def handle_session_start(self, parser_id: str, session_type: str, metadata: dict = None) -> dict:
        """Handle session start."""
        try:
            # Create request object for validation
            request = SessionStartRequest(
                parser_id=parser_id,
                session_type=session_type,
                metadata=metadata
            )
            
            session = ParserSession(
                session_id=str(uuid.uuid4()),
                parser_id=request.parser_id,
                session_type=request.session_type,
                metadata=request.metadata or {}
            )
            self.sessions[session.session_id] = session

            logger.info(f"Session started: {session.session_id} for parser {session.parser_id}")

            response = SessionStartResponse(success=True, session=session)
            return response.model_dump(mode='json')
        except Exception as e:
            logger.error(f"Session start failed: {e}")
            response = SessionStartResponse(success=False, error=str(e))
            return response.model_dump(mode='json')

    async def handle_session_end(self, session_id: str) -> dict:
        """Handle session end."""
        try:
            # Create request object for validation
            request = SessionEndRequest(session_id=session_id)
            
            if request.session_id in self.sessions:
                session = self.sessions[request.session_id]
                session.ended_at = datetime.now()
                session.status = "completed"

                logger.info(f"Session ended: {request.session_id}")

            response = SessionEndResponse(success=True, session_id=request.session_id, message="Session ended")
            return response.model_dump(mode='json')
        except Exception as e:
            logger.error(f"Session end failed: {e}")
            response = SessionEndResponse(success=False, session_id=session_id, error=str(e))
            return response.model_dump(mode='json')
