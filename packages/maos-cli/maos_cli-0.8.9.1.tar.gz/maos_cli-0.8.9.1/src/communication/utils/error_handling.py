"""Comprehensive error handling and retry logic for MAOS communication."""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategies."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    JITTERED_BACKOFF = "jittered_backoff"


@dataclass
class RetryPolicy:
    """Retry policy configuration."""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1  # 10% jitter
    retryable_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError, TimeoutError, asyncio.TimeoutError
    ])
    non_retryable_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ValueError, TypeError, KeyError
    ])
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should be retried."""
        if attempt >= self.max_attempts:
            return False
        
        # Check non-retryable exceptions first
        for exc_type in self.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # Check retryable exceptions
        for exc_type in self.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default: retry for most exceptions
        return True
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry."""
        if self.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.base_delay
        
        elif self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (self.backoff_multiplier ** (attempt - 1))
        
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * attempt
        
        elif self.strategy == RetryStrategy.JITTERED_BACKOFF:
            exponential_delay = self.base_delay * (self.backoff_multiplier ** (attempt - 1))
            jitter = exponential_delay * self.jitter_factor * (0.5 - asyncio.get_event_loop().time() % 1)
            delay = exponential_delay + jitter
        
        else:
            delay = self.base_delay
        
        # Cap at max delay
        return min(delay, self.max_delay)


@dataclass
class ErrorContext:
    """Context information for an error."""
    error: Exception
    severity: ErrorSeverity
    component: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    attempt: int = 1
    context_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = field(default_factory=lambda: traceback.format_exc())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "severity": self.severity.value,
            "component": self.component,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat(),
            "attempt": self.attempt,
            "context_data": self.context_data,
            "stack_trace": self.stack_trace
        }


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 60.0  # Seconds before trying recovery
    success_threshold: int = 3  # Successes before closing
    timeout: float = 30.0  # Operation timeout
    
    # Monitored exceptions
    monitored_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError, TimeoutError, asyncio.TimeoutError
    ])


class CircuitBreaker:
    """Circuit breaker for protecting against cascading failures."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State tracking
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.next_attempt_time: Optional[datetime] = None
        
        # Metrics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_rejections = 0
        
        logger.info(f"Circuit breaker initialized: {name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        self.total_requests += 1
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._attempt_reset()
            else:
                self.total_rejections += 1
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)
            
            # Success
            self._record_success()
            return result
            
        except Exception as e:
            # Check if this exception should be monitored
            if any(isinstance(e, exc_type) for exc_type in self.config.monitored_exceptions):
                self._record_failure()
            
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if not self.last_failure_time:
            return True
        
        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.config.recovery_timeout
    
    def _attempt_reset(self):
        """Attempt to reset circuit to half-open."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
    
    def _record_success(self):
        """Record successful operation."""
        self.total_successes += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _record_failure(self):
        """Record failed operation."""
        self.total_failures += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Go back to open on any failure in half-open
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit."""
        self.state = CircuitBreakerState.OPEN
        self.next_attempt_time = datetime.utcnow() + timedelta(seconds=self.config.recovery_timeout)
        logger.warning(f"Circuit breaker {self.name} OPENED after {self.failure_count} failures")
    
    def _close_circuit(self):
        """Close the circuit."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.next_attempt_time = None
        logger.info(f"Circuit breaker {self.name} CLOSED")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_requests": self.total_requests,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_rejections": self.total_rejections,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "next_attempt_time": self.next_attempt_time.isoformat() if self.next_attempt_time else None
        }


class ErrorHandler:
    """Comprehensive error handler with retry logic and circuit breakers."""
    
    def __init__(self):
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.error_counts: Dict[str, int] = {}
        self.component_errors: Dict[str, List[ErrorContext]] = {}
        
        # Retry policies by component/operation
        self.retry_policies: Dict[str, RetryPolicy] = {}
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Error callbacks
        self.error_callbacks: List[Callable[[ErrorContext], None]] = []
        
        # Default retry policy
        self.default_retry_policy = RetryPolicy()
        
        # Metrics
        self.metrics = {
            "total_errors": 0,
            "total_retries": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "circuit_breaker_opens": 0,
            "critical_errors": 0
        }
        
        logger.info("Error handler initialized")
    
    def set_retry_policy(self, component: str, policy: RetryPolicy):
        """Set retry policy for a component."""
        self.retry_policies[component] = policy
        logger.info(f"Set retry policy for component: {component}")
    
    def create_circuit_breaker(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Create and register a circuit breaker."""
        circuit_breaker = CircuitBreaker(name, config)
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self.circuit_breakers.get(name)
    
    async def handle_error(
        self,
        error: Exception,
        component: str,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context_data: Optional[Dict[str, Any]] = None,
        attempt: int = 1
    ) -> ErrorContext:
        """Handle an error with proper logging and tracking."""
        try:
            # Create error context
            error_context = ErrorContext(
                error=error,
                severity=severity,
                component=component,
                operation=operation,
                attempt=attempt,
                context_data=context_data or {}
            )
            
            # Record error
            await self._record_error(error_context)
            
            # Log error
            await self._log_error(error_context)
            
            # Trigger callbacks
            await self._trigger_callbacks(error_context)
            
            return error_context
            
        except Exception as e:
            logger.error(f"Error handler failed: {e}")
            raise
    
    async def execute_with_retry(
        self,
        func: Callable,
        component: str,
        operation: str,
        *args,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker_name: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic and optional circuit breaker."""
        policy = retry_policy or self.retry_policies.get(component, self.default_retry_policy)
        circuit_breaker = None
        
        if circuit_breaker_name:
            circuit_breaker = self.circuit_breakers.get(circuit_breaker_name)
        
        last_exception = None
        
        for attempt in range(1, policy.max_attempts + 1):
            try:
                # Use circuit breaker if available
                if circuit_breaker:
                    return await circuit_breaker.call(func, *args, **kwargs)
                else:
                    # Execute directly
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
            except Exception as e:
                last_exception = e
                
                # Handle the error
                error_context = await self.handle_error(
                    e, component, operation, 
                    severity=ErrorSeverity.HIGH if attempt == policy.max_attempts else ErrorSeverity.MEDIUM,
                    context_data=context_data,
                    attempt=attempt
                )
                
                # Check if we should retry
                if not policy.should_retry(e, attempt):
                    logger.error(f"Non-retryable error in {component}.{operation}: {e}")
                    break
                
                if attempt < policy.max_attempts:
                    # Calculate delay and wait
                    delay = policy.calculate_delay(attempt)
                    logger.info(f"Retrying {component}.{operation} in {delay:.2f}s (attempt {attempt + 1}/{policy.max_attempts})")
                    
                    self.metrics["total_retries"] += 1
                    await asyncio.sleep(delay)
                else:
                    self.metrics["failed_retries"] += 1
                    logger.error(f"Max retries exceeded for {component}.{operation}")
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
    
    async def _record_error(self, error_context: ErrorContext):
        """Record error in history and statistics."""
        # Add to history
        self.error_history.append(error_context)
        
        # Limit history size
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # Update counts
        error_key = f"{error_context.component}.{error_context.operation}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Component-specific errors
        if error_context.component not in self.component_errors:
            self.component_errors[error_context.component] = []
        self.component_errors[error_context.component].append(error_context)
        
        # Limit component error history
        if len(self.component_errors[error_context.component]) > 100:
            self.component_errors[error_context.component] = self.component_errors[error_context.component][-100:]
        
        # Update metrics
        self.metrics["total_errors"] += 1
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.metrics["critical_errors"] += 1
    
    async def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level."""
        error_dict = error_context.to_dict()
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR in {error_context.component}.{error_context.operation}: {error_context.error}")
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH ERROR in {error_context.component}.{error_context.operation}: {error_context.error}")
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM ERROR in {error_context.component}.{error_context.operation}: {error_context.error}")
        else:
            logger.info(f"LOW ERROR in {error_context.component}.{error_context.operation}: {error_context.error}")
    
    async def _trigger_callbacks(self, error_context: ErrorContext):
        """Trigger registered error callbacks."""
        for callback in self.error_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(error_context)
                else:
                    callback(error_context)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    def add_error_callback(self, callback: Callable[[ErrorContext], None]):
        """Add error callback."""
        self.error_callbacks.append(callback)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "errors_by_severity": {
                severity.value: sum(1 for e in self.error_history if e.severity == severity)
                for severity in ErrorSeverity
            },
            "errors_by_component": {
                component: len(errors)
                for component, errors in self.component_errors.items()
            },
            "recent_errors": [e.to_dict() for e in self.error_history[-10:]],
            "circuit_breaker_stats": {
                name: cb.get_stats()
                for name, cb in self.circuit_breakers.items()
            },
            "metrics": self.metrics
        }
    
    def get_component_errors(self, component: str, limit: int = 50) -> List[ErrorContext]:
        """Get recent errors for a component."""
        return self.component_errors.get(component, [])[-limit:]
    
    def clear_error_history(self):
        """Clear error history (for testing/maintenance)."""
        self.error_history.clear()
        self.error_counts.clear()
        self.component_errors.clear()
        
        # Reset circuit breaker stats
        for cb in self.circuit_breakers.values():
            cb.total_requests = 0
            cb.total_failures = 0
            cb.total_successes = 0
            cb.total_rejections = 0
        
        logger.info("Error history cleared")


# Decorator for automatic retry
def retry_on_error(
    component: str,
    operation: str,
    retry_policy: Optional[RetryPolicy] = None,
    circuit_breaker_name: Optional[str] = None,
    error_handler: Optional[ErrorHandler] = None
):
    """Decorator for automatic retry on function errors."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler()
            return await handler.execute_with_retry(
                func, component, operation,
                *args,
                retry_policy=retry_policy,
                circuit_breaker_name=circuit_breaker_name,
                **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler()
            return asyncio.run(handler.execute_with_retry(
                func, component, operation,
                *args,
                retry_policy=retry_policy,
                circuit_breaker_name=circuit_breaker_name,
                **kwargs
            ))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Custom exceptions
class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass