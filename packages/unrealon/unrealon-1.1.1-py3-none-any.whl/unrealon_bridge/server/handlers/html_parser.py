"""
HTML Parser RPC handlers.

Clean implementation following CRITICAL_REQUIREMENTS.md:
- No inline imports
- Strict Pydantic v2 usage
- Complete type annotations
- No Dict[str, Any] usage
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import Optional

from unrealon_rpc.logging import get_logger

from ...models import HTMLParseRPCRequest, HTMLParseRPCResponse, HTMLParseResult

logger = get_logger(__name__)


class HTMLParserHandlers:
    """Handlers for HTML parser RPC operations."""

    def __init__(self) -> None:
        """Initialize HTML parser handlers."""
        pass

    async def handle_html_parse(self, html_content: str, parser_id: str, url: Optional[str] = None, parse_type: str = "general", instructions: Optional[str] = None, timeout: int = 60, metadata: Optional[dict] = None) -> dict:
        """
        Handle HTML parsing request.

        Forwards HTML content to Django backend for AI/LLM processing.
        Django will parse HTML and return JSON + markdown instructions.

        Args:
            html_content: Raw HTML content to parse
            parser_id: ID of the parser making the request
            url: Source URL of the HTML (optional)
            parse_type: Type of parsing (product, listing, article, etc.)
            instructions: Additional parsing instructions (optional)
            timeout: Timeout in seconds (default 60s for LLM processing)
            metadata: Additional metadata (optional)

        Returns:
            HTMLParseRPCResponse as dict with success, result, request_id
        """
        try:
            # Create and validate request object
            request = HTMLParseRPCRequest(html_content=html_content, parser_id=parser_id, url=url, parse_type=parse_type, instructions=instructions, timeout=timeout, metadata=metadata or {})

            request_id = str(uuid.uuid4())

            logger.info(f"HTML parse request from parser {parser_id}: " f"{len(html_content)} chars, type: {parse_type}")

            # TODO: In production, make RPC call to Django backend
            # For now, simulate the response
            result = await self._simulate_html_parsing(request)

            response = HTMLParseRPCResponse(success=True, result=result, request_id=request_id, message="HTML parsed successfully" if result.success else "HTML parsing failed")

            return response.model_dump(mode="json")

        except Exception as e:
            logger.error(f"HTML parsing failed for parser {parser_id}: {e}")

            response = HTMLParseRPCResponse(success=False, error=str(e), message="HTML parsing request failed")

            return response.model_dump(mode="json")

    async def _simulate_html_parsing(self, request: HTMLParseRPCRequest) -> HTMLParseResult:
        """
        Simulate HTML parsing for demo purposes.

        In production, this would make an RPC call to Django backend which would:
        1. Receive the HTML content
        2. Use LLM (GPT-4, Claude, etc.) to parse the HTML
        3. Return structured JSON data + markdown instructions

        Args:
            request: Validated HTML parse request

        Returns:
            HTMLParseResult with success/failure and data/markdown
        """
        # Simulate brief processing delay
        await asyncio.sleep(0.1)

        # Simulate success/failure (85% success rate)
        success_rate = 0.85
        is_successful = random.random() < success_rate

        if is_successful:
            return self._create_success_result(request)
        else:
            return HTMLParseResult(success=False, error_message="Failed to extract structured data from HTML")

    def _create_success_result(self, request: HTMLParseRPCRequest) -> HTMLParseResult:
        """Create successful parsing result with sample data."""
        # Sample parsed data
        parsed_data = {
            "title": "Sample Product Title",
            "price": "29,900,000",
            "description": "Sample product description extracted from HTML",
            "specifications": {"year": "2020", "mileage": "45,000 km", "fuel": "Gasoline"},
            "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        }
        # Make parsed_data with pydantic model

        # Generate markdown instructions
        markdown_instructions = f"""# HTML Parsing Results

## Extracted Data
Successfully parsed {request.parse_type} content from the provided HTML.

### Key Findings:
- **Title**: {parsed_data.get('title', 'N/A')}
- **Price**: {parsed_data.get('price', 'N/A')}
- **Content Size**: {len(request.html_content)} characters

### Parsing Notes:
- Applied {request.parse_type} parsing rules
- Processed HTML structure successfully
- Extracted all required fields

### Recommendations:
- Data quality appears good
- Consider validating price format
- Check for additional product images

### Next Steps:
1. Validate extracted data against business rules
2. Store in appropriate database tables
3. Process for further analysis
"""

        return HTMLParseResult(success=True, parsed_data=parsed_data, markdown=markdown_instructions)
