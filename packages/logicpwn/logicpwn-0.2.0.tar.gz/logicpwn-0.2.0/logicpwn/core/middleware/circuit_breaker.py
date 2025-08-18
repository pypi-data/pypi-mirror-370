"""
Circuit breaker middleware for resilient request handling.
"""
import time
from typing import Optional, Any
from logicpwn.core.middleware.middleware import BaseMiddleware, MiddlewareContext
from logicpwn.core.logging import log_info, log_warning, log_error
from logicpwn.exceptions import RequestExecutionError

class CircuitBreakerError(RequestExecutionError):
    """Exception raised when circuit breaker is open."""
    pass

class CircuitBreakerMiddleware(BaseMiddleware):
    """Circuit breaker middleware for resilient request handling."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, 
                 error_threshold: float = 0.5):
        super().__init__("CircuitBreaker")
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.error_threshold = error_threshold  # Percentage of errors to trigger circuit
        
        # State tracking
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.state_change_time = time.time()
        
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Check circuit breaker state before processing request."""
        if not self.enabled:
            return context
            
        current_time = time.time()
        
        # Check if circuit should move from open to half_open
        if (self.state == "open" and 
            self.last_failure_time and 
            current_time - self.last_failure_time > self.recovery_timeout):
            self._change_state("half_open", current_time)
        
        # Block request if circuit is open
        if self.state == "open":
            raise CircuitBreakerError(
                f"Circuit breaker is open. Last failure: {self.last_failure_time}. "
                f"Recovery timeout: {self.recovery_timeout}s"
            )
        
        # Add circuit breaker metadata to context
        context.metadata = context.metadata or {}
        context.metadata['circuit_breaker_state'] = self.state
        context.metadata['circuit_breaker_failure_count'] = self.failure_count
        
        return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
        """Update circuit breaker state based on response."""
        if not self.enabled:
            return response
            
        status_code = getattr(response, 'status_code', 200)
        current_time = time.time()
        
        if self._is_failure(status_code):
            self._record_failure(current_time)
        else:
            self._record_success(current_time)
        
        return response
    
    def _is_failure(self, status_code: int) -> bool:
        """Determine if response indicates a failure."""
        # Consider 5xx errors and timeouts as failures
        return status_code >= 500 or status_code == 408 or status_code == 429
    
    def _record_failure(self, current_time: float):
        """Record a failure and update circuit state."""
        self.failure_count += 1
        self.last_failure_time = current_time
        
        total_requests = self.failure_count + self.success_count
        error_rate = self.failure_count / max(total_requests, 1)
        
        # Open circuit if failure threshold reached and error rate exceeded
        if (self.failure_count >= self.failure_threshold and 
            error_rate >= self.error_threshold and 
            self.state != "open"):
            
            self._change_state("open", current_time)
            log_warning(f"Circuit breaker opened", {
                "failure_count": self.failure_count,
                "error_rate": f"{error_rate:.2%}",
                "threshold": self.failure_threshold
            })
    
    def _record_success(self, current_time: float):
        """Record a success and potentially close the circuit."""
        self.success_count += 1
        
        if self.state == "half_open":
            # Close circuit after successful request in half_open state
            self._change_state("closed", current_time)
            self.failure_count = 0  # Reset failure count
            log_info("Circuit breaker closed after successful request in half_open state")
            
        elif self.state == "closed":
            # Gradually reduce failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def _change_state(self, new_state: str, current_time: float):
        """Change circuit breaker state with logging."""
        old_state = self.state
        self.state = new_state
        self.state_change_time = current_time
        
        log_info(f"Circuit breaker state changed: {old_state} -> {new_state}", {
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        })
    
    def get_statistics(self) -> dict:
        """Get circuit breaker statistics."""
        current_time = time.time()
        total_requests = self.failure_count + self.success_count
        
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": total_requests,
            "error_rate": self.failure_count / max(total_requests, 1),
            "state_duration": current_time - self.state_change_time,
            "last_failure_time": self.last_failure_time,
            "recovery_timeout": self.recovery_timeout,
            "failure_threshold": self.failure_threshold
        }
    
    def reset(self):
        """Reset circuit breaker to initial state."""
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self._change_state("closed", time.time())
        log_info("Circuit breaker manually reset")
