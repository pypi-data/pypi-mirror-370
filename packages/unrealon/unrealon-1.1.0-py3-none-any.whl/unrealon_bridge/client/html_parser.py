"""
HTML Parser functionality for Parser Bridge Client.

Provides methods for sending HTML content to Django for AI-powered parsing.
"""

from typing import Optional, Dict
from unrealon_rpc.logging import get_logger

from ..models import HTMLParseResult, HTMLParseRPCResponse, HTMLParseRPCRequest

logger = get_logger(__name__)


class HTMLParserMixin:
    """Mixin for HTML parsing functionality."""

    async def parse_html(
        self,
        html_content: str,
        url: Optional[str] = None,
        parse_type: str = "general",
        instructions: Optional[str] = None,
        timeout: int = 60,
        metadata: Optional[Dict[str, str]] = None
    ) -> HTMLParseResult:
        """
        Parse HTML content using AI/LLM via Django backend.

        Args:
            html_content: Raw HTML content to parse
            url: Source URL of the HTML (for context)
            parse_type: Type of parsing (product, listing, article, etc.)
            instructions: Additional parsing instructions for the LLM
            timeout: Timeout in seconds (default 60s for LLM processing)
            metadata: Additional metadata

        Returns:
            HTMLParseResult with parsed data or error information

        Example:
            ```python
            # Parse product page HTML
            result = await client.parse_html(
                html_content="<html>...</html>",
                url="https://encar.com/car/123456",
                parse_type="car_product",
                instructions="Extract car details, price, and specifications"
            )
            
            if result.success:
                print(f"Parsed data: {result.parsed_data}")
                print(f"Instructions: {result.markdown}")
            else:
                print(f"Parse failed: {result.error_message}")
            ```
        """
        if not self.registered:
            logger.warning("Cannot parse HTML - parser not registered")
            return HTMLParseResult(
                success=False,
                error_message="Parser not registered"
            )

        try:
            logger.info(f"Parsing HTML content: {len(html_content)} chars, type: {parse_type}")

            request = HTMLParseRPCRequest(
                html_content=html_content,
                parser_id=self.parser_id,
                url=url,
                parse_type=parse_type,
                instructions=instructions,
                timeout=timeout,
                metadata=metadata or {}
            )

            response = await self.bridge_client.call_rpc(
                method="html_parser.parse",
                params=request.model_dump(),
                timeout=timeout + 5  # Add buffer for network/processing
            )

            rpc_response = HTMLParseRPCResponse.model_validate(response)
            
            if rpc_response.success and rpc_response.result:
                logger.info(f"HTML parsing completed successfully")
                return rpc_response.result
            else:
                error_msg = rpc_response.error or "Unknown parsing error"
                logger.error(f"HTML parsing failed: {error_msg}")
                return HTMLParseResult(
                    success=False,
                    error_message=error_msg
                )

        except Exception as e:
            error_msg = f"HTML parsing request failed: {e}"
            logger.error(error_msg)
            return HTMLParseResult(
                success=False,
                error_message=error_msg
            )

    async def parse_html_with_retry(
        self,
        html_content: str,
        max_retries: int = 3,
        **kwargs
    ) -> HTMLParseResult:
        """
        Parse HTML with automatic retry on failure.

        Args:
            html_content: Raw HTML content to parse
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to parse_html

        Returns:
            HTMLParseResult with parsed data or error information
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.parse_html(html_content, **kwargs)
                
                if result.success:
                    if attempt > 0:
                        logger.info(f"HTML parsing succeeded on attempt {attempt + 1}")
                    return result
                else:
                    last_error = result.error_message
                    if attempt < max_retries - 1:
                        logger.warning(f"HTML parsing failed on attempt {attempt + 1}, retrying...")
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    logger.warning(f"HTML parsing error on attempt {attempt + 1}, retrying: {e}")

        logger.error(f"HTML parsing failed after {max_retries} attempts")
        return HTMLParseResult(
            success=False,
            error_message=f"Failed after {max_retries} attempts. Last error: {last_error}"
        )