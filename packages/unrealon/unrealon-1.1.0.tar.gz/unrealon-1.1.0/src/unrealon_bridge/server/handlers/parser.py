"""
Parser-related RPC handlers.
"""

from unrealon_rpc.logging import get_logger
from unrealon_bridge.configs import load_bridge_config
from unrealon_bridge.models import ParserInfo, ParserHealth, ParserSystemStats, ParserRegisterRequest, ParserRegisterResponse, ParserStatusRequest, ParserStatusResponse, ParserListRequest, ParserListResponse, ParserHealthRequest, ParserHealthResponse

logger = get_logger(__name__)


class ParserHandlers:
    """Handlers for parser-related RPC operations."""

    async def handle_parser_register(self, parser_id: str, parser_type: str, version: str, capabilities: list, metadata: dict = None, api_key: str = None) -> dict:
        """Handle parser registration."""
        try:
            # Load bridge configuration
            config = load_bridge_config()

            # Check if API key is required
            if config.security.require_api_key:
                if not api_key:
                    response = ParserRegisterResponse(success=False, error="API key is required")
                    return response.model_dump(mode="json")

                # Validate API key
                if not config.is_valid_api_key(api_key):
                    logger.warning(f"Invalid API key attempted: {api_key[:8] if api_key else 'None'}...")
                    response = ParserRegisterResponse(success=False, error="Invalid API key")
                    return response.model_dump(mode="json")

            # Create request object for validation
            request = ParserRegisterRequest(parser_id=parser_id, parser_type=parser_type, version=version, capabilities=capabilities, metadata=metadata)

            parser_info = ParserInfo(parser_id=request.parser_id, parser_type=request.parser_type, version=request.version, capabilities=request.capabilities, metadata=request.metadata or {})
            self.parsers[parser_info.parser_id] = parser_info
            
            # Find and map the most recent WebSocket client (daemon usually connects then registers immediately)
            if self.bridge.connections:
                # Get the most recently connected client
                latest_client_id = max(self.bridge.connections.keys(), 
                                     key=lambda cid: self.bridge.connections[cid].client_info.connected_at)
                self.parser_to_client[parser_info.parser_id] = latest_client_id
                logger.info(f"🔗 Mapped parser {parser_info.parser_id} to client {latest_client_id}")
            else:
                logger.warning(f"⚠️ No WebSocket clients connected during parser registration")

            # Log successful registration
            api_key_display = api_key[:8] + "..." if api_key else "None"
            logger.info(f"Parser registered: {parser_info.parser_id} ({parser_info.parser_type}) with API key: {api_key_display}")

            # Log test key usage in development
            if config.is_development() and api_key in config.security.test_api_keys:
                logger.info(f"🧪 Using test API key for development: {api_key}")

            response = ParserRegisterResponse(success=True, parser_id=parser_info.parser_id, message="Parser registered successfully")
            return response.model_dump(mode="json")
        except Exception as e:
            logger.error(f"Parser registration failed: {e}")
            response = ParserRegisterResponse(success=False, error=str(e))
            return response.model_dump(mode="json")

    async def handle_parser_get_status(self, parser_id: str) -> dict:
        """Handle parser status request."""
        parser_info = self.parsers.get(parser_id)

        if not parser_info:
            response = ParserStatusResponse(success=False, error=f"Parser {parser_id} not found")
            return response.model_dump(mode="json")

        response = ParserStatusResponse(success=True, parser=parser_info)
        return response.model_dump(mode="json")

    async def handle_parser_list(self, parser_type: str = None) -> dict:
        """Handle parser list request."""
        parsers = list(self.parsers.values())

        if parser_type:
            parsers = [p for p in parsers if p.parser_type == parser_type]

        response = ParserListResponse(success=True, parsers=parsers, total=len(parsers))
        return response.model_dump(mode="json")

    async def handle_parser_get_health(self, parser_id: str) -> dict:
        """Handle parser health check."""
        if parser_id not in self.parsers:
            response = ParserHealthResponse(success=False, error="Parser not found")
            return response.model_dump(mode="json")

        # Health check implementation should be provided by external service
        health = ParserHealth(parser_id=parser_id, status="healthy", response_time=0.1, memory_usage=50.0, cpu_usage=25.0, active_connections=1, queue_size=0)

        response = ParserHealthResponse(success=True, health=health)
        return response.model_dump(mode="json")
