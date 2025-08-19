"""
Adaptive Rate Limiting for LogicPwn - Dynamic throttling based on response patterns.

This module provides intelligent rate limiting that adapts based on:
- Response status codes and error patterns
- Server response times and performance
- Rate limit indicators in responses
- Circuit breaker state
"""

import time
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque
import statistics
from logicpwn.core.logging import log_info, log_warning, log_error


@dataclass
class RateLimitConfig:
    """Configuration for adaptive rate limiting."""
    base_delay: float = 1.0                    # Base delay between requests (seconds)
    max_delay: float = 30.0                    # Maximum delay between requests (seconds)
    min_delay: float = 0.1                     # Minimum delay between requests (seconds)
    backoff_multiplier: float = 2.0            # Multiplier for exponential backoff
    recovery_factor: float = 0.8               # Factor to reduce delay on success
    rate_limit_status_codes: List[int] = field(default_factory=lambda: [429, 503, 502])
    error_status_codes: List[int] = field(default_factory=lambda: [500, 501, 502, 503, 504])
    response_time_threshold: float = 5.0       # Seconds - slow response threshold
    window_size: int = 10                      # Number of recent requests to track
    adaptation_sensitivity: float = 0.1        # How quickly to adapt (0.0-1.0)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    timestamp: float
    response_time: float
    status_code: int
    success: bool
    rate_limited: bool
    error: bool


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts delays based on server response patterns.
    
    Features:
    - Exponential backoff on rate limiting
    - Adaptive delay based on response times
    - Recovery on successful requests
    - Circuit breaker integration
    - Comprehensive metrics collection
    """
    
    def __init__(self, name: str, config: Optional[RateLimitConfig] = None):
        """
        Initialize adaptive rate limiter.
        
        Args:
            name: Unique identifier for this rate limiter
            config: Configuration for rate limiting behavior
        """
        self.name = name
        self.config = config or RateLimitConfig()
        self.current_delay = self.config.base_delay
        
        # Thread-safe state management
        self._lock = threading.RLock()
        self.last_request_time = 0.0
        self.consecutive_rate_limits = 0
        self.consecutive_errors = 0
        self.consecutive_successes = 0
        
        # Request history for adaptive behavior
        self.request_history: deque = deque(maxlen=self.config.window_size)
        
        # Statistics
        self.total_requests = 0
        self.total_delays_applied = 0
        self.total_delay_time = 0.0
        
        log_info(f"Adaptive rate limiter '{name}' initialized", {
            "base_delay": self.config.base_delay,
            "max_delay": self.config.max_delay,
            "backoff_multiplier": self.config.backoff_multiplier
        })
    
    def wait_if_needed(self) -> float:
        """
        Apply rate limiting delay if needed.
        
        Returns:
            Actual delay applied in seconds
        """
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.current_delay:
                delay_needed = self.current_delay - time_since_last
                
                log_info(f"Rate limiter '{self.name}' applying delay", {
                    "delay": delay_needed,
                    "current_delay_setting": self.current_delay,
                    "time_since_last": time_since_last
                })
                
                time.sleep(delay_needed)
                self.total_delays_applied += 1
                self.total_delay_time += delay_needed
                
                self.last_request_time = time.time()
                return delay_needed
            else:
                self.last_request_time = current_time
                return 0.0
    
    def record_request(self, response_time: float, status_code: int, exception: Optional[Exception] = None) -> None:
        """
        Record request results and adapt rate limiting accordingly.
        
        Args:
            response_time: Time taken for the request in seconds
            status_code: HTTP status code received
            exception: Exception that occurred during request (if any)
        """
        with self._lock:
            self.total_requests += 1
            
            # Classify request result
            rate_limited = status_code in self.config.rate_limit_status_codes
            error = (status_code in self.config.error_status_codes or 
                    exception is not None or 
                    status_code >= 400)
            success = not error and not rate_limited
            slow_response = response_time > self.config.response_time_threshold
            
            # Create metrics record
            metrics = RequestMetrics(
                timestamp=time.time(),
                response_time=response_time,
                status_code=status_code,
                success=success,
                rate_limited=rate_limited,
                error=error
            )
            self.request_history.append(metrics)
            
            # Update consecutive counters
            if rate_limited:
                self.consecutive_rate_limits += 1
                self.consecutive_errors = 0
                self.consecutive_successes = 0
            elif error:
                self.consecutive_errors += 1
                self.consecutive_rate_limits = 0
                self.consecutive_successes = 0
            elif success:
                self.consecutive_successes += 1
                self.consecutive_rate_limits = 0
                self.consecutive_errors = 0
            
            # Adapt delay based on response patterns
            old_delay = self.current_delay
            self._adapt_delay(rate_limited, error, success, slow_response, response_time)
            
            # Log adaptation decision
            if abs(self.current_delay - old_delay) > 0.01:  # Significant change
                log_info(f"Rate limiter '{self.name}' adapted delay", {
                    "old_delay": old_delay,
                    "new_delay": self.current_delay,
                    "reason": self._get_adaptation_reason(rate_limited, error, success, slow_response),
                    "consecutive_rate_limits": self.consecutive_rate_limits,
                    "consecutive_errors": self.consecutive_errors,
                    "consecutive_successes": self.consecutive_successes,
                    "response_time": response_time,
                    "status_code": status_code
                })
    
    def _adapt_delay(self, rate_limited: bool, error: bool, success: bool, 
                    slow_response: bool, response_time: float) -> None:
        """Adapt the current delay based on request results."""
        
        if rate_limited:
            # Aggressive backoff on rate limiting
            self.current_delay = min(
                self.current_delay * self.config.backoff_multiplier,
                self.config.max_delay
            )
            
        elif error and self.consecutive_errors > 1:
            # Moderate backoff on repeated errors
            self.current_delay = min(
                self.current_delay * (1 + self.config.adaptation_sensitivity),
                self.config.max_delay
            )
            
        elif slow_response:
            # Increase delay for slow responses to reduce server load
            server_stress_factor = min(response_time / self.config.response_time_threshold, 3.0)
            self.current_delay = min(
                self.current_delay * (1 + self.config.adaptation_sensitivity * server_stress_factor),
                self.config.max_delay
            )
            
        elif success:
            # Recovery on successful requests
            if self.consecutive_successes > 1:
                self.current_delay = max(
                    self.current_delay * self.config.recovery_factor,
                    self.config.min_delay
                )
            
        # Additional adaptive logic based on request history
        if len(self.request_history) >= self.config.window_size:
            self._adapt_based_on_history()
    
    def _adapt_based_on_history(self) -> None:
        """Adapt delay based on historical request patterns."""
        recent_requests = list(self.request_history)
        
        # Calculate success rate
        success_rate = sum(1 for r in recent_requests if r.success) / len(recent_requests)
        error_rate = sum(1 for r in recent_requests if r.error) / len(recent_requests)
        rate_limit_rate = sum(1 for r in recent_requests if r.rate_limited) / len(recent_requests)
        
        # Calculate average response time
        response_times = [r.response_time for r in recent_requests]
        avg_response_time = statistics.mean(response_times)
        
        # Adapt based on overall patterns
        if rate_limit_rate > 0.3:  # High rate limiting
            self.current_delay = min(
                self.current_delay * 1.5,
                self.config.max_delay
            )
            
        elif error_rate > 0.5:  # High error rate
            self.current_delay = min(
                self.current_delay * 1.2,
                self.config.max_delay
            )
            
        elif success_rate > 0.8 and avg_response_time < self.config.response_time_threshold:
            # Good performance, can potentially speed up
            self.current_delay = max(
                self.current_delay * 0.9,
                self.config.min_delay
            )
    
    def _get_adaptation_reason(self, rate_limited: bool, error: bool, 
                             success: bool, slow_response: bool) -> str:
        """Get human-readable reason for delay adaptation."""
        if rate_limited:
            return "rate_limited"
        elif error:
            return "error_response"
        elif slow_response:
            return "slow_response"
        elif success:
            return "successful_recovery"
        else:
            return "historical_patterns"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current rate limiter metrics."""
        with self._lock:
            recent_requests = list(self.request_history)
            
            if recent_requests:
                success_rate = sum(1 for r in recent_requests if r.success) / len(recent_requests)
                error_rate = sum(1 for r in recent_requests if r.error) / len(recent_requests)
                rate_limit_rate = sum(1 for r in recent_requests if r.rate_limited) / len(recent_requests)
                avg_response_time = statistics.mean([r.response_time for r in recent_requests])
            else:
                success_rate = error_rate = rate_limit_rate = avg_response_time = 0.0
            
            return {
                "name": self.name,
                "current_delay": self.current_delay,
                "total_requests": self.total_requests,
                "total_delays_applied": self.total_delays_applied,
                "total_delay_time": self.total_delay_time,
                "consecutive_rate_limits": self.consecutive_rate_limits,
                "consecutive_errors": self.consecutive_errors,
                "consecutive_successes": self.consecutive_successes,
                "recent_success_rate": success_rate,
                "recent_error_rate": error_rate,
                "recent_rate_limit_rate": rate_limit_rate,
                "recent_avg_response_time": avg_response_time,
                "config": {
                    "base_delay": self.config.base_delay,
                    "max_delay": self.config.max_delay,
                    "min_delay": self.config.min_delay,
                    "backoff_multiplier": self.config.backoff_multiplier,
                    "recovery_factor": self.config.recovery_factor
                }
            }
    
    def reset(self) -> None:
        """Reset rate limiter to initial state."""
        with self._lock:
            self.current_delay = self.config.base_delay
            self.last_request_time = 0.0
            self.consecutive_rate_limits = 0
            self.consecutive_errors = 0
            self.consecutive_successes = 0
            self.request_history.clear()
            self.total_requests = 0
            self.total_delays_applied = 0
            self.total_delay_time = 0.0
            
            log_info(f"Rate limiter '{self.name}' reset to initial state")


class RateLimiterRegistry:
    """Registry for managing multiple rate limiters."""
    
    def __init__(self):
        self._limiters: Dict[str, AdaptiveRateLimiter] = {}
        self._lock = threading.Lock()
    
    def get_limiter(self, name: str, config: Optional[RateLimitConfig] = None) -> AdaptiveRateLimiter:
        """Get or create a rate limiter by name."""
        with self._lock:
            if name not in self._limiters:
                self._limiters[name] = AdaptiveRateLimiter(name, config)
            return self._limiters[name]
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics for all registered rate limiters."""
        with self._lock:
            return [limiter.get_metrics() for limiter in self._limiters.values()]
    
    def reset_all(self) -> None:
        """Reset all rate limiters."""
        with self._lock:
            for limiter in self._limiters.values():
                limiter.reset()


# Global registry instance
rate_limiter_registry = RateLimiterRegistry()
