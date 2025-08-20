"""
Proxy-related RPC handlers.
"""

import uuid
from unrealon_rpc.logging import get_logger

from ...models import (
    ProxyInfo,
    ProxyAllocateRequest, ProxyAllocateResponse,
    ProxyReleaseRequest, ProxyReleaseResponse,
    ProxyCheckRequest, ProxyCheckResponse
)

logger = get_logger(__name__)


class ProxyHandlers:
    """Handlers for proxy-related RPC operations."""

    async def handle_proxy_allocate(self, parser_id: str, proxy_type: str, location: str = None) -> dict:
        """Handle proxy allocation."""
        try:
            # Create request object for validation
            request = ProxyAllocateRequest(
                parser_id=parser_id,
                proxy_type=proxy_type,
                location=location
            )
            
            # Proxy allocation should be implemented by external service
            proxy_info = ProxyInfo(
                proxy_id=str(uuid.uuid4()), 
                parser_id=request.parser_id,
                host="127.0.0.1", 
                port=8080, 
                proxy_type=request.proxy_type,
                location=request.location
            )

            self.proxies[proxy_info.proxy_id] = proxy_info

            logger.info(f"Proxy allocated: {proxy_info.proxy_id} for {request.parser_id}")

            response = ProxyAllocateResponse(success=True, proxy=proxy_info)
            return response.model_dump(mode='json')

        except Exception as e:
            response = ProxyAllocateResponse(success=False, error=str(e))
            return response.model_dump(mode='json')

    async def handle_proxy_release(self, proxy_id: str) -> dict:
        """Handle proxy release."""
        try:
            # Create request object for validation
            request = ProxyReleaseRequest(proxy_id=proxy_id)
            
            if request.proxy_id in self.proxies:
                del self.proxies[request.proxy_id]
                logger.info(f"Proxy released: {request.proxy_id}")

            response = ProxyReleaseResponse(success=True, proxy_id=request.proxy_id, message="Proxy released")
            return response.model_dump(mode='json')
        except Exception as e:
            logger.error(f"Proxy release failed: {e}")
            response = ProxyReleaseResponse(success=False, proxy_id=proxy_id, error=str(e))
            return response.model_dump(mode='json')

    async def handle_proxy_check(self, request: ProxyCheckRequest) -> ProxyCheckResponse:
        """Handle proxy health check."""
        if request.proxy_id not in self.proxies:
            return ProxyCheckResponse(success=False, error="Proxy not found")

        # Proxy health check should be implemented by external service
        return ProxyCheckResponse(success=True, proxy_id=request.proxy_id, status="healthy")
