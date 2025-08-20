"""
Connection and registration management for Parser Bridge Client.
"""

import uuid
from typing import Optional
from unrealon_rpc.logging import get_logger

from ..models import (
    ParserInfo, ParserRegisterRequest, ParserRegisterResponse
)

logger = get_logger(__name__)


class ConnectionMixin:
    """Mixin for connection and registration functionality."""

    async def connect(self) -> None:
        """Connect to bridge and register parser."""
        await self.bridge_client.connect()
        # Auto-register parser after connection
        await self.register_parser()

    async def disconnect(self) -> None:
        """Disconnect from bridge."""
        if self.session_id:
            # Session cleanup will be handled by the main client
            pass

        await self.bridge_client.disconnect()

    async def register_parser(self, metadata: Optional[dict[str, str]] = None) -> ParserInfo:
        """
        Register parser with the system.

        Args:
            metadata: Additional parser metadata

        Returns:
            Parser registration information
        """
        request = ParserRegisterRequest(
            parser_id=str(uuid.uuid4()),
            parser_type=self.parser_type,
            version=self.parser_version,
            capabilities=self.capabilities,
            metadata=metadata
        )

        # Prepare params with API key
        params = request.model_dump()
        if hasattr(self, 'api_key') and self.api_key:
            params["api_key"] = self.api_key
            logger.info(f"🔑 Adding API key to params: {self.api_key[:8]}...")
        else:
            logger.warning(f"⚠️ No API key available! hasattr: {hasattr(self, 'api_key')}, api_key: {getattr(self, 'api_key', 'NOT_FOUND')}")
        
        result = await self.bridge_client.call_rpc(
            method="parser.register", 
            params=params
        )

        # Parse response using typed model
        response = ParserRegisterResponse.model_validate(result)
        
        if response.success:
            self.parser_id = response.parser_id or request.parser_id
            self.registered = True

            logger.info(f"Parser registered: {self.parser_id} ({self.parser_type})")

            return ParserInfo(
                parser_id=self.parser_id,
                parser_type=self.parser_type,
                version=self.parser_version,
                capabilities=self.capabilities,
                metadata=metadata or {}
            )
        else:
            raise RuntimeError(f"Parser registration failed: {response.error}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
