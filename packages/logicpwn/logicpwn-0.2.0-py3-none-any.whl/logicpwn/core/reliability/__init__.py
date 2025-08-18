"""
Reliability module for LogicPwn - Circuit Breakers, Rate Limiting, Security Metrics, and Fault Tolerance.
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerState,
    CircuitBreakerOpenException,
    CircuitBreakerMetrics,
    circuit_breaker_registry
)

from .adaptive_rate_limiter import (
    AdaptiveRateLimiter,
    RateLimitConfig,
    RequestMetrics,
    rate_limiter_registry
)

from .security_metrics import (
    SecurityMetricsCollector, 
    SecurityEvent, 
    SecurityEventType, 
    SecuritySeverity,
    security_metrics,
    record_security_event
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig", 
    "CircuitBreakerState",
    "CircuitBreakerOpenException",
    "CircuitBreakerMetrics",
    "circuit_breaker_registry",
    "AdaptiveRateLimiter",
    "RateLimitConfig",
    "RequestMetrics", 
    "rate_limiter_registry",
    "SecurityMetricsCollector",
    "SecurityEvent",
    "SecurityEventType",
    "SecuritySeverity", 
    "security_metrics",
    "record_security_event"
]
