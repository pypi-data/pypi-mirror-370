"""
Security Metrics and Observability Module for LogicPwn
Provides comprehensive security monitoring, metrics collection, and alerting capabilities.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json
import logging
from datetime import datetime, timedelta

class SecurityEventType(Enum):
    """Types of security events to monitor."""
    AUTHENTICATION_FAILURE = "auth_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    SUSPICIOUS_REQUEST = "suspicious_request"
    DATA_LEAK_DETECTED = "data_leak_detected"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    IDOR_VULNERABILITY = "idor_vulnerability"
    EXPLOIT_SUCCESS = "exploit_success"
    EXPLOIT_FAILURE = "exploit_failure"
    MEMORY_LEAK_WARNING = "memory_leak_warning"
    THREAD_SAFETY_VIOLATION = "thread_safety_violation"

class SecuritySeverity(Enum):
    """Severity levels for security events."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SecurityEvent:
    """Represents a security-related event."""
    timestamp: float
    event_type: SecurityEventType
    severity: SecuritySeverity
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_module: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class SecurityMetrics:
    """Container for security metrics."""
    total_events: int = 0
    events_by_type: Dict[SecurityEventType, int] = field(default_factory=lambda: defaultdict(int))
    events_by_severity: Dict[SecuritySeverity, int] = field(default_factory=lambda: defaultdict(int))
    avg_response_time: float = 0.0
    failed_requests: int = 0
    successful_requests: int = 0
    circuit_breaker_trips: int = 0
    rate_limit_violations: int = 0
    data_leak_incidents: int = 0
    memory_leak_warnings: int = 0
    thread_safety_violations: int = 0

class SecurityMetricsCollector:
    """
    Collects and analyzes security metrics across LogicPwn components.
    Thread-safe implementation with configurable retention and alerting.
    """
    
    def __init__(self, 
                 max_events: int = 10000,
                 retention_hours: int = 24,
                 enable_alerts: bool = True):
        """
        Initialize security metrics collector.
        
        Args:
            max_events: Maximum number of events to store in memory
            retention_hours: How long to retain events (hours)
            enable_alerts: Whether to enable security alerting
        """
        self.max_events = max_events
        self.retention_hours = retention_hours
        self.enable_alerts = enable_alerts
        
        self._events: deque = deque(maxlen=max_events)
        self._metrics = SecurityMetrics()
        self._lock = threading.RLock()
        self._alert_handlers: List[Callable[[SecurityEvent], None]] = []
        
        # Performance tracking
        self._request_times: deque = deque(maxlen=1000)
        
        # Alerting thresholds
        self._alert_thresholds = {
            SecurityEventType.AUTHENTICATION_FAILURE: 5,  # per minute
            SecurityEventType.RATE_LIMIT_EXCEEDED: 10,    # per minute
            SecurityEventType.DATA_LEAK_DETECTED: 1,      # immediate alert
            SecurityEventType.CIRCUIT_BREAKER_OPEN: 1,    # immediate alert
            SecurityEventType.MEMORY_LEAK_WARNING: 3,     # per hour
            SecurityEventType.THREAD_SAFETY_VIOLATION: 1, # immediate alert
        }
        
        # Rate tracking for alerting
        self._event_rates = defaultdict(lambda: deque(maxlen=100))
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_events, daemon=True)
        self._cleanup_thread.start()
    
    def record_event(self, event: SecurityEvent) -> None:
        """
        Record a security event.
        
        Args:
            event: Security event to record
        """
        with self._lock:
            # Add timestamp if not set
            if not hasattr(event, 'timestamp') or event.timestamp == 0:
                event.timestamp = time.time()
            
            # Store event
            self._events.append(event)
            
            # Update metrics
            self._metrics.total_events += 1
            self._metrics.events_by_type[event.event_type] += 1
            self._metrics.events_by_severity[event.severity] += 1
            
            # Update specific counters
            if event.event_type == SecurityEventType.CIRCUIT_BREAKER_OPEN:
                self._metrics.circuit_breaker_trips += 1
            elif event.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED:
                self._metrics.rate_limit_violations += 1
            elif event.event_type == SecurityEventType.DATA_LEAK_DETECTED:
                self._metrics.data_leak_incidents += 1
            elif event.event_type == SecurityEventType.MEMORY_LEAK_WARNING:
                self._metrics.memory_leak_warnings += 1
            elif event.event_type == SecurityEventType.THREAD_SAFETY_VIOLATION:
                self._metrics.thread_safety_violations += 1
            elif event.event_type == SecurityEventType.EXPLOIT_FAILURE:
                self._metrics.failed_requests += 1
            elif event.event_type == SecurityEventType.EXPLOIT_SUCCESS:
                self._metrics.successful_requests += 1
            
            # Track event rate for alerting
            self._event_rates[event.event_type].append(event.timestamp)
            
            # Check for alerting conditions
            if self.enable_alerts:
                self._check_alert_conditions(event)
    
    def record_request_time(self, duration: float) -> None:
        """Record request execution time for performance metrics."""
        with self._lock:
            self._request_times.append(duration)
            
            # Update average response time
            if self._request_times:
                self._metrics.avg_response_time = sum(self._request_times) / len(self._request_times)
    
    def add_alert_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """
        Add an alert handler function.
        
        Args:
            handler: Function to call when security alerts are triggered
        """
        with self._lock:
            self._alert_handlers.append(handler)
    
    def get_metrics(self) -> SecurityMetrics:
        """Get current security metrics."""
        with self._lock:
            return SecurityMetrics(
                total_events=self._metrics.total_events,
                events_by_type=dict(self._metrics.events_by_type),
                events_by_severity=dict(self._metrics.events_by_severity),
                avg_response_time=self._metrics.avg_response_time,
                failed_requests=self._metrics.failed_requests,
                successful_requests=self._metrics.successful_requests,
                circuit_breaker_trips=self._metrics.circuit_breaker_trips,
                rate_limit_violations=self._metrics.rate_limit_violations,
                data_leak_incidents=self._metrics.data_leak_incidents,
                memory_leak_warnings=self._metrics.memory_leak_warnings,
                thread_safety_violations=self._metrics.thread_safety_violations
            )
    
    def get_recent_events(self, 
                         event_type: Optional[SecurityEventType] = None,
                         severity: Optional[SecuritySeverity] = None,
                         limit: int = 100) -> List[SecurityEvent]:
        """
        Get recent security events with optional filtering.
        
        Args:
            event_type: Filter by event type
            severity: Filter by severity level
            limit: Maximum number of events to return
            
        Returns:
            List of recent security events
        """
        with self._lock:
            events = list(self._events)
            
            # Apply filters
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            if severity:
                events = [e for e in events if e.severity == severity]
            
            # Sort by timestamp (most recent first) and limit
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events[:limit]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a comprehensive metrics summary for reporting."""
        metrics = self.get_metrics()
        
        # Calculate success rate
        total_requests = metrics.successful_requests + metrics.failed_requests
        success_rate = (metrics.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Get recent critical events
        critical_events = self.get_recent_events(severity=SecuritySeverity.CRITICAL, limit=10)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_events": metrics.total_events,
            "success_rate": f"{success_rate:.2f}%",
            "avg_response_time": f"{metrics.avg_response_time:.3f}s",
            "security_incidents": {
                "circuit_breaker_trips": metrics.circuit_breaker_trips,
                "rate_limit_violations": metrics.rate_limit_violations,
                "data_leak_incidents": metrics.data_leak_incidents,
                "memory_leak_warnings": metrics.memory_leak_warnings,
                "thread_safety_violations": metrics.thread_safety_violations
            },
            "events_by_severity": {
                severity.name: count for severity, count in metrics.events_by_severity.items()
            },
            "recent_critical_events": [
                {
                    "type": event.event_type.value,
                    "message": event.message,
                    "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                    "source": event.source_module
                }
                for event in critical_events
            ]
        }
    
    def _check_alert_conditions(self, event: SecurityEvent) -> None:
        """Check if the event triggers any alert conditions."""
        current_time = time.time()
        
        # Check immediate alerts (critical events)
        if (event.severity == SecuritySeverity.CRITICAL or 
            event.event_type in [SecurityEventType.DATA_LEAK_DETECTED, 
                                SecurityEventType.THREAD_SAFETY_VIOLATION]):
            self._trigger_alert(event)
            return
        
        # Check rate-based alerts
        if event.event_type in self._alert_thresholds:
            threshold = self._alert_thresholds[event.event_type]
            event_times = self._event_rates[event.event_type]
            
            # Count events in the last minute for per-minute thresholds
            minute_ago = current_time - 60
            recent_events = sum(1 for t in event_times if t >= minute_ago)
            
            if recent_events >= threshold:
                alert_event = SecurityEvent(
                    timestamp=current_time,
                    event_type=event.event_type,
                    severity=SecuritySeverity.HIGH,
                    message=f"Rate threshold exceeded: {recent_events} {event.event_type.value} events in 1 minute",
                    metadata={"threshold": threshold, "actual_rate": recent_events},
                    source_module="security_metrics"
                )
                self._trigger_alert(alert_event)
    
    def _trigger_alert(self, event: SecurityEvent) -> None:
        """Trigger security alert handlers."""
        for handler in self._alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logging.error(f"Error in security alert handler: {e}")
    
    def _cleanup_old_events(self) -> None:
        """Background thread to clean up old events."""
        while True:
            try:
                current_time = time.time()
                cutoff_time = current_time - (self.retention_hours * 3600)
                
                with self._lock:
                    # Remove old events
                    while self._events and self._events[0].timestamp < cutoff_time:
                        self._events.popleft()
                    
                    # Clean up rate tracking
                    for event_type in self._event_rates:
                        event_times = self._event_rates[event_type]
                        while event_times and event_times[0] < cutoff_time:
                            event_times.popleft()
                
                # Sleep for 1 hour before next cleanup
                time.sleep(3600)
                
            except Exception as e:
                logging.error(f"Error in security metrics cleanup: {e}")
                time.sleep(60)  # Shorter sleep on error

# Global security metrics collector instance
security_metrics = SecurityMetricsCollector()

def record_security_event(event_type: SecurityEventType, 
                         severity: SecuritySeverity,
                         message: str,
                         metadata: Optional[Dict[str, Any]] = None,
                         source_module: Optional[str] = None) -> None:
    """
    Convenience function to record a security event.
    
    Args:
        event_type: Type of security event
        severity: Severity level
        message: Human-readable message
        metadata: Additional event metadata
        source_module: Source module name
    """
    event = SecurityEvent(
        timestamp=time.time(),
        event_type=event_type,
        severity=severity,
        message=message,
        metadata=metadata or {},
        source_module=source_module
    )
    security_metrics.record_event(event)

def setup_default_alert_handlers() -> None:
    """Set up default security alert handlers."""
    
    def log_alert_handler(event: SecurityEvent) -> None:
        """Log security alerts to the standard logger."""
        log_level = logging.CRITICAL if event.severity == SecuritySeverity.CRITICAL else logging.WARNING
        logging.log(log_level, f"SECURITY ALERT: {event.message} (Type: {event.event_type.value}, Source: {event.source_module})")
    
    security_metrics.add_alert_handler(log_alert_handler)

# Initialize default alert handlers
setup_default_alert_handlers()
