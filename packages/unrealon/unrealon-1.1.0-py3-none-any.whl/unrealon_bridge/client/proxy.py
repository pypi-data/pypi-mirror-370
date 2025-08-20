"""
Proxy management for Parser Bridge Client.
"""

from typing import Optional
from unrealon_rpc.logging import get_logger

from ..models import (
    ProxyInfo, ProxyAllocateRequest, ProxyAllocateResponse,
    ProxyReleaseRequest, ProxyReleaseResponse
)

logger = get_logger(__name__)


class ProxyMixin:
    """Mixin for proxy management functionality."""

    async def request_proxy(self, proxy_type: str = "http", location: Optional[str] = None) -> ProxyInfo:
        """
        Request proxy allocation.

        Args:
            proxy_type: Type of proxy needed
            location: Preferred proxy location

        Returns:
            Allocated proxy information
        """
        self._ensure_registered()

        request = ProxyAllocateRequest(
            parser_id=self.parser_id,
            proxy_type=proxy_type,
            location=location
        )

        result = await self.bridge_client.call_rpc(
            method="proxy.allocate", 
            params=request.model_dump()
        )

        response = ProxyAllocateResponse.model_validate(result)
        
        if response.success and response.proxy:
            logger.info(f"Proxy allocated: {response.proxy.proxy_id} for {self.parser_id}")
            return response.proxy
        else:
            raise RuntimeError(f"Proxy allocation failed: {response.error}")

    async def release_proxy(self, proxy_id: str) -> None:
        """
        Release proxy allocation.

        Args:
            proxy_id: Proxy ID to release
        """
        request = ProxyReleaseRequest(proxy_id=proxy_id)
        
        result = await self.bridge_client.call_rpc(
            method="proxy.release", 
            params=request.model_dump()
        )

        response = ProxyReleaseResponse.model_validate(result)
        
        if response.success:
            logger.info(f"Proxy released: {proxy_id}")
        else:
            logger.error(f"Proxy release failed: {response.error}")
