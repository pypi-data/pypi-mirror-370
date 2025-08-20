"""
HTML Analyzer Models - Pydantic v2 models for HTML analysis operations.

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Pydantic v2 models everywhere
- Custom exception hierarchy
- No try blocks in imports
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HTMLAnalysisResult(BaseModel):
    """Complete HTML analysis result with proper typing."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    success: bool = Field(..., description="Analysis success status")
    original_html_size: int = Field(..., ge=0, description="Original HTML size in characters")
    cleaned_html: str = Field(..., description="Cleaned HTML content")
    cleaned_html_size: int = Field(..., ge=0, description="Cleaned HTML size in characters")
    extracted_data: dict[str, str] = Field(default_factory=dict, description="Extracted JavaScript data")
    analysis_result: dict[str, str] = Field(default_factory=dict, description="LLM analysis result")
    cleaning_stats: dict[str, float] = Field(default_factory=dict, description="Cleaning statistics")
    error_message: str = Field(default="", description="Error message if failed")


class HTMLParseResult(BaseModel):
    """Standardized HTML parsing result for ParserManager."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    success: str = Field(..., description="Success status as string (true/false)")
    parsed_data: str = Field(..., description="Parsed data as string")
    markdown: str = Field(..., description="Markdown representation")
    error_message: str = Field(..., description="Error message if failed")


class HTMLAnalyzerStats(BaseModel):
    """HTML analyzer statistics."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    cleaned_count: int = Field(default=0, ge=0, description="Number of HTML documents cleaned")
    total_reduction: float = Field(default=0.0, ge=0.0, description="Total size reduction percentage")
    websocket_enabled: bool = Field(..., description="Whether WebSocket analyzer is enabled")


class HTMLCleaningRequest(BaseModel):
    """Request model for HTML cleaning operations."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    html: str = Field(..., min_length=1, description="HTML content to clean")
    preserve_js_data: bool = Field(default=True, description="Whether to extract JavaScript data")
    aggressive_cleaning: bool = Field(default=False, description="Whether to apply aggressive cleaning")


class HTMLAnalysisRequest(BaseModel):
    """Request model for HTML analysis operations."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    html: str = Field(..., min_length=1, description="HTML content to analyze")
    instructions: Optional[str] = Field(default=None, description="Analysis instructions for LLM")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    url: Optional[str] = Field(default=None, description="Source URL for logging")
    clean_first: bool = Field(default=True, description="Whether to clean HTML before analysis")
    preserve_js_data: bool = Field(default=True, description="Whether to extract JavaScript data")
    aggressive_cleaning: bool = Field(default=False, description="Whether to apply aggressive cleaning")


class HTMLParseRequest(BaseModel):
    """Complete HTML parsing request model."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    html: str = Field(..., min_length=1, description="HTML content to parse")
    url: Optional[str] = Field(default=None, description="Source URL for logging")
    instructions: Optional[str] = Field(default=None, description="Analysis instructions")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    clean_first: bool = Field(default=True, description="Whether to clean HTML before analysis")
    preserve_js_data: bool = Field(default=True, description="Whether to extract JavaScript data")
    aggressive_cleaning: bool = Field(default=False, description="Whether to apply aggressive cleaning")


class HTMLAnalyzerError(Exception):
    """Base exception for HTML analyzer operations."""

    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class HTMLCleaningError(HTMLAnalyzerError):
    """Raised when HTML cleaning fails."""

    pass


class HTMLAnalysisError(HTMLAnalyzerError):
    """Raised when HTML analysis fails."""

    pass


class WebSocketAnalysisError(HTMLAnalyzerError):
    """Raised when WebSocket analysis fails."""

    pass
