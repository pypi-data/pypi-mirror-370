"""
Circuit Breaker pattern implementation for LogicPwn reliability and fault tolerance.

This module provides circuit breaker functionality to prevent cascading failures
and provide fast failure responses when services are unavailable.
"""

import time
import threading
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from logicpwn.core.logging import log_info, log_warning, log_error

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing fast, not calling service
    HALF_OPEN = "half_open" # Testing if service is back up


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5          # Failures needed to open circuit
    recovery_timeout: float = 60.0      # Seconds to wait before trying half-open
    success_threshold: int = 3          # Successes needed in half-open to close
    timeout: float = 10.0               # Request timeout
    exception_whitelist: List[type] = field(default_factory=list)  # Exceptions that don't count as failures


@dataclass 
class CircuitBreakerMetrics:
    """Metrics tracking for circuit breaker."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    state_changes: int = 0


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    def __init__(self, name: str, failure_count: int):
        self.name = name
        self.failure_count = failure_count
        super().__init__(f"Circuit breaker '{name}' is OPEN after {failure_count} failures")


class CircuitBreaker:
    """
    Circuit breaker implementation for reliable service calls.
    
    The circuit breaker prevents cascading failures by:
    1. CLOSED: Normal operation, monitoring for failures
    2. OPEN: Fast-fail mode, rejecting calls without attempting them
    3. HALF_OPEN: Testing mode, allowing limited calls to test recovery
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique identifier for this circuit breaker
            config: Configuration for circuit breaker behavior
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = threading.RLock()  # Allow recursive locking
        
        log_info(f"Circuit breaker '{name}' initialized", {
            "failure_threshold": self.config.failure_threshold,
            "recovery_timeout": self.config.recovery_timeout,
            "success_threshold": self.config.success_threshold
        })
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator interface for circuit breaker."""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        wrapper.__name__ = f"circuit_breaker_{self.name}({func.__name__})"
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenException: If circuit breaker is open
            Any exception raised by the function
        """
        with self._lock:
            self._update_state()
            
            if self.state == CircuitBreakerState.OPEN:
                self.metrics.total_requests += 1
                raise CircuitBreakerOpenException(self.name, self.metrics.failed_requests)
            
            # Allow call in CLOSED or HALF_OPEN state
            self.metrics.total_requests += 1
            
        try:
            # Execute function with timeout
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success
            with self._lock:
                self._record_success(execution_time)
            
            return result
            
        except Exception as e:
            # Check if exception should be ignored
            if any(isinstance(e, exc_type) for exc_type in self.config.exception_whitelist):
                log_info(f"Circuit breaker '{self.name}' ignoring whitelisted exception: {type(e).__name__}")
                raise
            
            # Record failure
            with self._lock:
                self._record_failure(e)
            
            raise
    
    def _update_state(self) -> None:
        """Update circuit breaker state based on current metrics."""
        current_time = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.metrics.consecutive_failures >= self.config.failure_threshold:
                self._transition_to_open()
                
        elif self.state == CircuitBreakerState.OPEN:
            if (self.metrics.last_failure_time and 
                current_time - self.metrics.last_failure_time >= self.config.recovery_timeout):
                self._transition_to_half_open()
                
        elif self.state == CircuitBreakerState.HALF_OPEN:
            if self.metrics.consecutive_successes >= self.config.success_threshold:
                self._transition_to_closed()
            elif self.metrics.consecutive_failures >= 1:
                self._transition_to_open()
    
    def _record_success(self, execution_time: float) -> None:
        """Record successful execution."""
        self.metrics.successful_requests += 1
        self.metrics.consecutive_successes += 1
        self.metrics.consecutive_failures = 0
        
        log_info(f"Circuit breaker '{self.name}' recorded success", {
            "execution_time": execution_time,
            "consecutive_successes": self.metrics.consecutive_successes,
            "state": self.state.value
        })
    
    def _record_failure(self, exception: Exception) -> None:
        """Record failed execution."""
        self.metrics.failed_requests += 1
        self.metrics.consecutive_failures += 1
        self.metrics.consecutive_successes = 0
        self.metrics.last_failure_time = time.time()
        
        log_warning(f"Circuit breaker '{self.name}' recorded failure", {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "consecutive_failures": self.metrics.consecutive_failures,
            "state": self.state.value
        })
    
    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        if self.state != CircuitBreakerState.OPEN:
            self.state = CircuitBreakerState.OPEN
            self.metrics.state_changes += 1
            
            log_error(f"Circuit breaker '{self.name}' OPENED", {
                "consecutive_failures": self.metrics.consecutive_failures,
                "failure_threshold": self.config.failure_threshold,
                "total_requests": self.metrics.total_requests,
                "recovery_timeout": self.config.recovery_timeout
            })
    
    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        if self.state != CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.HALF_OPEN
            self.metrics.state_changes += 1
            self.metrics.consecutive_successes = 0
            self.metrics.consecutive_failures = 0
            
            log_info(f"Circuit breaker '{self.name}' entered HALF_OPEN", {
                "recovery_timeout_elapsed": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold
            })
    
    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        if self.state != CircuitBreakerState.CLOSED:
            self.state = CircuitBreakerState.CLOSED
            self.metrics.state_changes += 1
            self.metrics.consecutive_failures = 0
            
            log_info(f"Circuit breaker '{self.name}' CLOSED (recovered)", {
                "consecutive_successes": self.metrics.consecutive_successes,
                "success_threshold": self.config.success_threshold
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current circuit breaker metrics."""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (
                    self.metrics.successful_requests / self.metrics.total_requests 
                    if self.metrics.total_requests > 0 else 0.0
                ),
                "consecutive_failures": self.metrics.consecutive_failures,
                "consecutive_successes": self.metrics.consecutive_successes,
                "state_changes": self.metrics.state_changes,
                "last_failure_time": self.metrics.last_failure_time,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout": self.config.timeout
                }
            }
    
    def force_open(self) -> None:
        """Force circuit breaker to OPEN state (for testing/manual intervention)."""
        with self._lock:
            self._transition_to_open()
            log_warning(f"Circuit breaker '{self.name}' manually forced OPEN")
    
    def force_close(self) -> None:
        """Force circuit breaker to CLOSED state (for testing/manual intervention)."""
        with self._lock:
            self._transition_to_closed()
            log_info(f"Circuit breaker '{self.name}' manually forced CLOSED")
    
    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.metrics = CircuitBreakerMetrics()
            log_info(f"Circuit breaker '{self.name}' reset to initial state")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
    
    def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics for all registered circuit breakers."""
        with self._lock:
            return [breaker.get_metrics() for breaker in self._breakers.values()]
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()
