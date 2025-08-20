"""
Base models for parser bridge operations.

Provides common base classes and shared types for all parser models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BaseParserModel(BaseModel):
    """Base class for all parser models with strict validation."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, str_strip_whitespace=True, validate_default=True)


class BaseRPCRequest(BaseParserModel):
    """Base class for all RPC requests."""

    pass


class BaseRPCResponse(BaseParserModel):
    """Base class for all RPC responses."""

    success: bool = Field(description="Whether the operation was successful")
    message: Optional[str] = Field(default=None, description="Human-readable message")
    error: Optional[str] = Field(default=None, description="Error message if success=False")
