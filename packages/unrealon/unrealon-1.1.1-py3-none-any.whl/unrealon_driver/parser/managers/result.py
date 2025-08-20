"""
Result Manager - Automatic result tracking and metrics with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations  
- Pydantic v2 models everywhere
- Custom exception hierarchy
"""

from typing import Optional, List, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


T = TypeVar('T', bound=BaseModel)


class OperationStatus(str, Enum):
    """Operation status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParseMetrics(BaseModel):
    """Parse operation metrics with strict typing"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    started_at: datetime = Field(
        default_factory=datetime.now,
        description="Operation start time"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Operation completion time"
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Operation duration in seconds"
    )
    pages_processed: int = Field(
        default=0,
        ge=0,
        description="Number of pages processed"
    )
    items_found: int = Field(
        default=0,
        ge=0,
        description="Number of items found"
    )
    errors_count: int = Field(
        default=0,
        ge=0,
        description="Number of errors encountered"
    )
    warnings_count: int = Field(
        default=0,
        ge=0,
        description="Number of warnings encountered"
    )
    status: OperationStatus = Field(
        default=OperationStatus.PENDING,
        description="Current operation status"
    )
    
    def complete(self, status: OperationStatus = OperationStatus.COMPLETED) -> None:
        """Mark operation as completed"""
        self.completed_at = datetime.now()
        if self.completed_at and self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.status = status


class ParseResult(BaseModel, Generic[T]):
    """Generic parse result with metrics and strict typing"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    data: List[T] = Field(
        default_factory=list,
        description="Parsed data items"
    )
    metrics: ParseMetrics = Field(
        default_factory=ParseMetrics,
        description="Operation metrics"
    )
    source_urls: List[str] = Field(
        default_factory=list,
        description="Source URLs processed"
    )
    parser_id: str = Field(
        ...,
        min_length=1,
        description="Parser identifier"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if operation failed"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Warning messages"
    )
    
    @field_validator('source_urls')
    @classmethod
    def validate_urls(cls, v: List[str]) -> List[str]:
        """Validate URL format"""
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")
        return v
    
    def model_post_init(self, __context) -> None:
        """Update metrics after initialization"""
        self.metrics.items_found = len(self.data)


class ResultManagerError(Exception):
    """Base exception for result manager errors"""
    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class OperationNotFoundError(ResultManagerError):
    """Raised when operation is not found"""
    pass


class InvalidOperationStateError(ResultManagerError):
    """Raised when operation is in invalid state"""
    pass


class ResultManager:
    """
    🎯 Result Manager - Automatic result tracking and metrics
    
    Features:
    - Automatic timing and metrics
    - Result aggregation  
    - Error tracking
    - Performance monitoring
    - Type-safe operations
    """
    
    def __init__(self, parser_id: str):
        if not parser_id.strip():
            raise ValueError("Parser ID cannot be empty")
        
        self.parser_id: str = parser_id
        self._current_metrics: Optional[ParseMetrics] = None
        self._results_history: List[ParseResult] = []
    
    def start_operation(self) -> ParseMetrics:
        """Start tracking a new parse operation"""
        if self._current_metrics and self._current_metrics.status == OperationStatus.RUNNING:
            raise InvalidOperationStateError(
                message="Cannot start new operation while another is running",
                operation="start_operation",
                details={"current_status": self._current_metrics.status.value}
            )
        
        self._current_metrics = ParseMetrics(status=OperationStatus.RUNNING)
        return self._current_metrics
    
    def track_page(self) -> None:
        """Track a processed page"""
        if not self._current_metrics:
            raise OperationNotFoundError(
                message="No operation in progress",
                operation="track_page"
            )
        
        self._current_metrics.pages_processed += 1
    
    def track_error(self) -> None:
        """Track an error"""
        if not self._current_metrics:
            raise OperationNotFoundError(
                message="No operation in progress", 
                operation="track_error"
            )
        
        self._current_metrics.errors_count += 1
    
    def track_warning(self) -> None:
        """Track a warning"""
        if not self._current_metrics:
            raise OperationNotFoundError(
                message="No operation in progress",
                operation="track_warning"
            )
        
        self._current_metrics.warnings_count += 1
    
    def complete_operation(
        self, 
        data: List[T], 
        source_urls: List[str],
        success: bool = True,
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None
    ) -> ParseResult[T]:
        """Complete the current operation and return result"""
        if not self._current_metrics:
            raise OperationNotFoundError(
                message="No operation in progress",
                operation="complete_operation"
            )
        
        status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
        self._current_metrics.complete(status)
        
        result = ParseResult[T](
            data=data,
            metrics=self._current_metrics,
            source_urls=source_urls,
            parser_id=self.parser_id,
            error_message=error_message,
            warnings=warnings or []
        )
        
        self._results_history.append(result)
        self._current_metrics = None
        
        return result
    
    def cancel_operation(self, reason: str) -> None:
        """Cancel the current operation"""
        if not self._current_metrics:
            raise OperationNotFoundError(
                message="No operation in progress",
                operation="cancel_operation"
            )
        
        self._current_metrics.complete(OperationStatus.CANCELLED)
        
        # Create cancelled result
        result = ParseResult[BaseModel](
            data=[],
            metrics=self._current_metrics,
            source_urls=[],
            parser_id=self.parser_id,
            error_message=f"Operation cancelled: {reason}"
        )
        
        self._results_history.append(result)
        self._current_metrics = None
    
    def get_current_metrics(self) -> Optional[ParseMetrics]:
        """Get current operation metrics"""
        return self._current_metrics
    
    def get_history(self) -> List[ParseResult]:
        """Get results history"""
        return [
            ParseResult.model_validate(result.model_dump()) 
            for result in self._results_history
        ]
    
    def get_stats(self) -> dict[str, float]:
        """Get overall statistics"""
        if not self._results_history:
            return {
                "total_operations": 0.0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "total_items": 0.0,
                "total_pages": 0.0
            }
        
        successful = [
            r for r in self._results_history 
            if r.metrics.status == OperationStatus.COMPLETED
        ]
        
        total_items = sum(r.metrics.items_found for r in self._results_history)
        total_pages = sum(r.metrics.pages_processed for r in self._results_history)
        
        durations = [
            r.metrics.duration_seconds 
            for r in self._results_history 
            if r.metrics.duration_seconds is not None
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            "total_operations": float(len(self._results_history)),
            "successful_operations": float(len(successful)),
            "failed_operations": float(len(self._results_history) - len(successful)),
            "success_rate": len(successful) / len(self._results_history) * 100.0,
            "total_items_found": float(total_items),
            "total_pages_processed": float(total_pages),
            "average_duration_seconds": round(avg_duration, 2),
            "items_per_operation": total_items / len(self._results_history) if self._results_history else 0.0
        }
    
    def clear_history(self) -> None:
        """Clear results history"""
        self._results_history.clear()
    
    def get_recent_results(self, limit: int = 10) -> List[ParseResult]:
        """Get recent results with limit"""
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        return self._results_history[-limit:]
