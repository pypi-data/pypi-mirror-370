"""
Error Manager - Smart error handling and retry logic with Pydantic v2

Strict compliance with CRITICAL_REQUIREMENTS.md:
- No Dict[str, Any] usage
- Complete type annotations
- Custom exception hierarchy
- No bare except clauses
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Callable, Optional, List, Type, TypeVar, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
import functools
import logging


F = TypeVar('F', bound=Callable[..., Any])


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorInfo(BaseModel):
    """Error information with strict typing"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    exception_type: str = Field(
        ...,
        description="Exception type name"
    )
    exception_message: str = Field(
        ...,
        description="Exception message"
    )
    severity: ErrorSeverity = Field(
        ...,
        description="Error severity level"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error occurrence timestamp"
    )
    operation: str = Field(
        ...,
        min_length=1,
        description="Operation where error occurred"
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts"
    )
    recoverable: bool = Field(
        default=True,
        description="Whether error is recoverable"
    )
    context: dict[str, str] = Field(
        default_factory=dict,
        description="Additional error context"
    )


class RetryConfig(BaseModel):
    """Retry configuration with validation"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    base_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Base delay between retries in seconds"
    )
    max_delay: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum delay between retries in seconds"
    )
    exponential_base: float = Field(
        default=2.0,
        ge=1.1,
        le=10.0,
        description="Exponential backoff base"
    )
    jitter: bool = Field(
        default=True,
        description="Add random jitter to delays"
    )
    retry_on_exceptions: List[str] = Field(
        default_factory=lambda: ["Exception"],
        description="Exception types to retry on"
    )
    
    @field_validator('max_delay')
    @classmethod
    def validate_max_delay(cls, v: float, info) -> float:
        """Validate max_delay is greater than base_delay"""
        if 'base_delay' in info.data and v < info.data['base_delay']:
            raise ValueError("max_delay must be greater than base_delay")
        return v


class CircuitBreakerState(BaseModel):
    """Circuit breaker state tracking"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    total_requests: int = Field(default=0, ge=0)
    failures: int = Field(default=0, ge=0)
    failure_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    last_failure: Optional[datetime] = Field(default=None)
    is_open: bool = Field(default=False)


class ErrorManagerError(Exception):
    """Base exception for error manager"""
    def __init__(self, message: str, operation: str, details: Optional[dict[str, str]] = None):
        self.message = message
        self.operation = operation
        self.details = details or {}
        super().__init__(message)


class RetryExhaustedException(ErrorManagerError):
    """Raised when all retry attempts are exhausted"""
    pass


class CircuitBreakerOpenError(ErrorManagerError):
    """Raised when circuit breaker is open"""
    pass


class ErrorManager:
    """
    🛡️ Error Manager - Smart error handling and retry logic
    
    Features:
    - Automatic retry with exponential backoff
    - Error classification and severity
    - Circuit breaker pattern
    - Error pattern detection
    - Type-safe error handling
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self._error_history: List[ErrorInfo] = []
        self._retry_configs: dict[str, RetryConfig] = {}
        self._circuit_breaker_states: dict[str, CircuitBreakerState] = {}
    
    def register_retry_config(self, operation: str, config: RetryConfig) -> None:
        """Register retry configuration for an operation"""
        if not operation.strip():
            raise ValueError("Operation name cannot be empty")
        
        self._retry_configs[operation] = config
    
    def classify_error(self, exception: Exception, operation: str) -> ErrorSeverity:
        """Classify error severity based on exception type"""
        exception_type = type(exception).__name__
        
        # Network/connection errors - usually recoverable
        if exception_type in ['ConnectionError', 'TimeoutError', 'ConnectTimeout']:
            return ErrorSeverity.MEDIUM
        
        # Browser/automation errors - might be recoverable
        if 'playwright' in exception_type.lower() or 'selenium' in exception_type.lower():
            return ErrorSeverity.MEDIUM
        
        # Parse/data errors - usually low severity
        if exception_type in ['ValueError', 'KeyError', 'AttributeError', 'TypeError']:
            return ErrorSeverity.LOW
        
        # Memory/system errors - critical
        if exception_type in ['MemoryError', 'OSError', 'SystemError']:
            return ErrorSeverity.CRITICAL
        
        # Permission errors - high severity
        if exception_type in ['PermissionError', 'FileNotFoundError']:
            return ErrorSeverity.HIGH
        
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    def should_retry(self, error_info: ErrorInfo, config: RetryConfig) -> bool:
        """Determine if operation should be retried"""
        # Check max attempts
        if error_info.retry_count >= config.max_attempts:
            return False
        
        # Check if exception type is retryable
        if error_info.exception_type not in config.retry_on_exceptions:
            # Check if "Exception" is in the list (catch-all)
            if "Exception" not in config.retry_on_exceptions:
                return False
        
        # Check circuit breaker
        if self._is_circuit_open(error_info.operation):
            return False
        
        # Critical errors shouldn't be retried
        if error_info.severity == ErrorSeverity.CRITICAL:
            return False
        
        return error_info.recoverable
    
    def calculate_delay(self, retry_count: int, config: RetryConfig) -> float:
        """Calculate retry delay with exponential backoff"""
        delay = config.base_delay * (config.exponential_base ** retry_count)
        delay = min(delay, config.max_delay)
        
        if config.jitter:
            # Add random jitter (±25%)
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter
        
        return max(0.1, delay)  # Minimum 0.1 second delay
    
    def record_error(
        self, 
        exception: Exception, 
        operation: str,
        context: Optional[dict[str, str]] = None
    ) -> ErrorInfo:
        """Record an error occurrence"""
        error_info = ErrorInfo(
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            severity=self.classify_error(exception, operation),
            operation=operation,
            recoverable=self._is_recoverable(exception),
            context=context or {}
        )
        
        self._error_history.append(error_info)
        self._update_circuit_breaker(operation, success=False)
        
        return error_info
    
    def record_success(self, operation: str) -> None:
        """Record a successful operation"""
        self._update_circuit_breaker(operation, success=True)
    
    def with_retry(
        self, 
        operation: str, 
        config: Optional[RetryConfig] = None
    ) -> Callable[[F], F]:
        """Decorator for automatic retry logic"""
        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                retry_config = config or self._retry_configs.get(operation, RetryConfig())
                last_error: Optional[Exception] = None
                
                for attempt in range(retry_config.max_attempts):
                    try:
                        result = await func(*args, **kwargs)
                        self.record_success(operation)
                        return result
                    
                    except Exception as e:
                        error_info = self.record_error(e, operation)
                        error_info.retry_count = attempt
                        last_error = e
                        
                        if not self.should_retry(error_info, retry_config):
                            break
                        
                        if attempt < retry_config.max_attempts - 1:
                            delay = self.calculate_delay(attempt, retry_config)
                            self.logger.warning(
                                f"Operation '{operation}' failed (attempt {attempt + 1}), "
                                f"retrying in {delay:.1f}s: {e}"
                            )
                            await asyncio.sleep(delay)
                
                # All retries exhausted
                self.logger.error(f"Operation '{operation}' failed after {retry_config.max_attempts} attempts")
                if last_error:
                    raise RetryExhaustedException(
                        message=f"Operation failed after {retry_config.max_attempts} attempts",
                        operation=operation,
                        details={"last_error": str(last_error)}
                    ) from last_error
                else:
                    raise RetryExhaustedException(
                        message=f"Operation failed after {retry_config.max_attempts} attempts",
                        operation=operation
                    )
            
            return wrapper  # type: ignore
        return decorator
    
    def _is_recoverable(self, exception: Exception) -> bool:
        """Determine if an error is recoverable"""
        exception_type = type(exception).__name__
        
        # System errors are usually not recoverable
        if exception_type in ['MemoryError', 'OSError', 'KeyboardInterrupt', 'SystemExit']:
            return False
        
        # Network errors are usually recoverable
        if exception_type in ['ConnectionError', 'TimeoutError', 'ConnectTimeout']:
            return True
        
        # Most other errors are recoverable
        return True
    
    def _is_circuit_open(self, operation: str) -> bool:
        """Check if circuit breaker is open for operation"""
        state = self._circuit_breaker_states.get(operation)
        if not state:
            return False
        
        # Circuit is open if failure rate is too high
        if state.failure_rate > 0.5 and state.total_requests > 10:
            # Check if cooldown period has passed
            if state.last_failure:
                cooldown_period = timedelta(minutes=5)
                if datetime.now() - state.last_failure < cooldown_period:
                    return True
        
        return False
    
    def _update_circuit_breaker(self, operation: str, success: bool) -> None:
        """Update circuit breaker state"""
        if operation not in self._circuit_breaker_states:
            self._circuit_breaker_states[operation] = CircuitBreakerState()
        
        state = self._circuit_breaker_states[operation]
        state.total_requests += 1
        
        if not success:
            state.failures += 1
            state.last_failure = datetime.now()
        
        state.failure_rate = state.failures / state.total_requests
        state.is_open = self._is_circuit_open(operation)
    
    def get_error_stats(self) -> dict[str, float]:
        """Get error statistics"""
        if not self._error_history:
            return {
                "total_errors": 0.0,
                "recent_errors_24h": 0.0,
                "critical_errors": 0.0,
                "high_errors": 0.0,
                "medium_errors": 0.0,
                "low_errors": 0.0
            }
        
        recent_errors = [
            e for e in self._error_history 
            if e.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        severity_counts = {
            "critical": len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
            "high": len([e for e in recent_errors if e.severity == ErrorSeverity.HIGH]),
            "medium": len([e for e in recent_errors if e.severity == ErrorSeverity.MEDIUM]),
            "low": len([e for e in recent_errors if e.severity == ErrorSeverity.LOW])
        }
        
        return {
            "total_errors": float(len(self._error_history)),
            "recent_errors_24h": float(len(recent_errors)),
            "critical_errors": float(severity_counts["critical"]),
            "high_errors": float(severity_counts["high"]),
            "medium_errors": float(severity_counts["medium"]),
            "low_errors": float(severity_counts["low"])
        }
    
    def get_circuit_breaker_states(self) -> dict[str, CircuitBreakerState]:
        """Get circuit breaker states"""
        return {
            operation: CircuitBreakerState.model_validate(state.model_dump())
            for operation, state in self._circuit_breaker_states.items()
        }
    
    def reset_circuit_breaker(self, operation: str) -> None:
        """Reset circuit breaker for operation"""
        if operation in self._circuit_breaker_states:
            self._circuit_breaker_states[operation] = CircuitBreakerState()
    
    def clear_error_history(self) -> None:
        """Clear error history"""
        self._error_history.clear()
