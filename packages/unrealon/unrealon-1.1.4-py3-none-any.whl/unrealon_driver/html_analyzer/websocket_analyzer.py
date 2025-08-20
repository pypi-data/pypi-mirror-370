"""
WebSocket HTML Analyzer - Handles HTML analysis via WebSocket communication.
"""

from typing import Optional, Dict, Any
from unrealon_driver.smart_logging import create_smart_logger
from unrealon_driver.websocket import websocket_manager, WebSocketConfig

from .config import HTMLAnalyzerConfig


class WebSocketHTMLAnalyzer:
    """
    WebSocket-based HTML analyzer that sends HTML to server for LLM analysis.
    """
    
    def __init__(self, config: HTMLAnalyzerConfig):
        self.config = config
        self.logger = create_smart_logger(parser_id=config.parser_id)
        
        # Initialize WebSocket if configured
        if config.websocket_url and config.enable_websocket_analysis:
            self._websocket_config = WebSocketConfig(
                url=config.websocket_url,
                api_key=config.api_key,
                parser_id=config.parser_id
            )
            self._websocket_initialized = False
        else:
            self._websocket_config = None
            self._websocket_initialized = False
    
    async def analyze_html(
        self, 
        html: str, 
        instructions: Optional[str] = None, 
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Analyze HTML content via WebSocket
        
        Args:
            html: HTML content to analyze
            instructions: Analysis instructions
            session_id: Session identifier
            **kwargs: Additional parameters
            
        Returns:
            Analysis result dictionary
        """
        if not self._websocket_config:
            self.logger.warning("🔌 WebSocket not configured for HTML analysis")
            return {
                "success": "false",
                "parsed_data": "",
                "markdown": "",
                "error_message": "WebSocket not configured"
            }
        
        try:
            # Ensure WebSocket connection
            if not self._websocket_initialized:
                await self._initialize_websocket()
            
            self.logger.info("🤖 Analyzing HTML with LLM via WebSocket...")
            
            # Prepare analysis request
            analysis_request = {
                "type": "html_analysis_request",
                "parser_id": self.config.parser_id,
                "session_id": session_id,
                "html_content": html,
                "instructions": instructions or "Extract and structure the data from this HTML",
                "parse_type": "general",
                "timeout": kwargs.get("timeout", self.config.default_timeout),
                "metadata": kwargs.get("metadata", {})
            }
            
            # Send request via WebSocket
            if websocket_manager.connected:
                response = await websocket_manager.send_request(
                    analysis_request, 
                    timeout=kwargs.get("timeout", self.config.default_timeout)
                )
                
                if response and response.get("success"):
                    self.logger.info("✅ HTML analysis completed successfully")
                    return {
                        "success": "true",
                        "parsed_data": str(response.get("parsed_data", "")),
                        "markdown": response.get("markdown", ""),
                        "error_message": ""
                    }
                else:
                    error_msg = response.get("error_message", "Analysis failed") if response else "No response"
                    self.logger.error(f"❌ HTML analysis failed: {error_msg}")
                    return {
                        "success": "false", 
                        "parsed_data": "",
                        "markdown": "",
                        "error_message": error_msg
                    }
            else:
                self.logger.warning("🔌 WebSocket not connected for HTML analysis")
                return {
                    "success": "false",
                    "parsed_data": "",
                    "markdown": "",
                    "error_message": "WebSocket not connected"
                }
                
        except Exception as e:
            self.logger.error(f"❌ HTML analysis failed: {str(e)}")
            return {
                "success": "false",
                "parsed_data": "",
                "markdown": "",
                "error_message": str(e)
            }
    
    async def _initialize_websocket(self) -> bool:
        """Initialize WebSocket connection"""
        if not self._websocket_config:
            return False
        
        try:
            success = await websocket_manager.initialize(self._websocket_config)
            if success:
                self._websocket_initialized = True
                self.logger.info("🔌 WebSocket initialized for HTML analysis")
            else:
                self.logger.warning("🔌 WebSocket initialization failed")
            return success
        except Exception as e:
            self.logger.error(f"❌ WebSocket initialization error: {e}")
            return False
    
    async def close(self):
        """Close WebSocket connection"""
        if self._websocket_initialized:
            await websocket_manager.disconnect()
            self._websocket_initialized = False
            self.logger.info("🔌 WebSocket connection closed")


def create_websocket_analyzer(config: HTMLAnalyzerConfig) -> WebSocketHTMLAnalyzer:
    """
    Create WebSocket HTML analyzer
    
    Args:
        config: HTML analyzer configuration
        
    Returns:
        Configured WebSocketHTMLAnalyzer instance
    """
    return WebSocketHTMLAnalyzer(config)
