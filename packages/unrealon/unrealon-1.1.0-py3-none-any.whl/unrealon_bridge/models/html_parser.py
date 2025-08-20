"""
HTML Parser models for LLM-based HTML parsing.

Models for sending HTML content to Django backend for AI-powered parsing.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseParserModel


class HTMLParseRequest(BaseParserModel):
    """Request for HTML parsing via AI/LLM."""
    
    html_content: str = Field(..., description="Raw HTML content to parse")
    parser_id: str = Field(..., description="ID of the parser making the request")
    url: Optional[str] = Field(None, description="Source URL of the HTML (for context)")
    parse_type: str = Field("general", description="Type of parsing (product, listing, article, etc.)")
    instructions: Optional[str] = Field(None, description="Additional parsing instructions")
    timeout: int = Field(60, description="Timeout in seconds (default 60s for LLM processing)")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class HTMLParseResult(BaseParserModel):
    """Result of HTML parsing."""
    
    success: bool = Field(..., description="Whether parsing was successful")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed JSON data")
    markdown: Optional[str] = Field(None, description="Markdown instructions from Django parser")
    error_message: Optional[str] = Field(None, description="Error message if parsing failed")


class HTMLParseResponse(BaseParserModel):
    """Response for HTML parsing request."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[HTMLParseResult] = Field(None, description="Parsing result")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    processed_at: datetime = Field(default_factory=datetime.now, description="When the request was processed")








# Request/Response models for RPC
class HTMLParseRPCRequest(BaseParserModel):
    """RPC request for HTML parsing."""
    
    html_content: str
    parser_id: str
    url: Optional[str] = None
    parse_type: str = "general"
    instructions: Optional[str] = None
    timeout: int = 60
    metadata: Dict[str, str] = Field(default_factory=dict)


class HTMLParseRPCResponse(BaseParserModel):
    """RPC response for HTML parsing."""
    
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    result: Optional[HTMLParseResult] = None
    request_id: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.now)






