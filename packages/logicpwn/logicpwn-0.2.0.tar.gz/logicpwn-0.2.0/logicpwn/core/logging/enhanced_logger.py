"""
Enhanced logging functionality with error tracking and pattern detection.
"""
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass

@dataclass
class ErrorPattern:
    """Represents a detected error pattern."""
    pattern_type: str
    error_type: str
    frequency: int
    recommendation: str
    first_occurrence: float
    last_occurrence: float

class ErrorTracker:
    """Track error frequency and patterns for better monitoring."""
    
    def __init__(self, window_size: int = 3600, pattern_threshold: int = 5):
        self.window_size = window_size
        self.pattern_threshold = pattern_threshold
        self.error_counts = defaultdict(deque)
        self.error_patterns = {}
        self.pattern_notifications = set()  # Prevent spam notifications
        
    def track_error(self, error_type: str, error_message: str, context: Optional[Dict] = None) -> Optional[ErrorPattern]:
        """Track error occurrence and detect patterns."""
        current_time = time.time()
        
        # Add error to tracking
        self.error_counts[error_type].append({
            'timestamp': current_time,
            'message': error_message,
            'context': context or {}
        })
        
        # Clean old entries
        self._cleanup_old_entries(error_type, current_time)
        
        # Check for patterns
        return self._detect_patterns(error_type, current_time)
    
    def _cleanup_old_entries(self, error_type: str, current_time: float):
        """Remove entries older than the window size."""
        cutoff_time = current_time - self.window_size
        while (self.error_counts[error_type] and 
               self.error_counts[error_type][0]['timestamp'] < cutoff_time):
            self.error_counts[error_type].popleft()
    
    def _detect_patterns(self, error_type: str, current_time: float) -> Optional[ErrorPattern]:
        """Detect error patterns and return recommendations."""
        error_entries = list(self.error_counts[error_type])
        
        if len(error_entries) < self.pattern_threshold:
            return None
        
        # Calculate time intervals between errors
        timestamps = [entry['timestamp'] for entry in error_entries]
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        if not intervals:
            return None
        
        avg_interval = sum(intervals) / len(intervals)
        pattern_key = f"{error_type}_{current_time // 60}"  # Group by minute
        
        # High frequency pattern (errors < 1 minute apart on average)
        if avg_interval < 60 and pattern_key not in self.pattern_notifications:
            self.pattern_notifications.add(pattern_key)
            return ErrorPattern(
                pattern_type="high_frequency",
                error_type=error_type,
                frequency=len(error_entries),
                recommendation="Consider implementing circuit breaker, rate limiting, or retry backoff",
                first_occurrence=timestamps[0],
                last_occurrence=timestamps[-1]
            )
        
        # Burst pattern (many errors in short time)
        recent_errors = [t for t in timestamps if current_time - t < 300]  # Last 5 minutes
        if len(recent_errors) > self.pattern_threshold and pattern_key not in self.pattern_notifications:
            self.pattern_notifications.add(pattern_key)
            return ErrorPattern(
                pattern_type="burst",
                error_type=error_type,
                frequency=len(recent_errors),
                recommendation="Investigate recent changes or system load issues",
                first_occurrence=recent_errors[0],
                last_occurrence=recent_errors[-1]
            )
        
        return None
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        current_time = time.time()
        stats = {}
        
        for error_type, entries in self.error_counts.items():
            entry_list = list(entries)
            if not entry_list:
                continue
                
            stats[error_type] = {
                'total_count': len(entry_list),
                'first_occurrence': entry_list[0]['timestamp'],
                'last_occurrence': entry_list[-1]['timestamp'],
                'avg_frequency': len(entry_list) / (self.window_size / 3600),  # Per hour
                'recent_count': len([e for e in entry_list if current_time - e['timestamp'] < 300])
            }
        
        return stats
    
    def clear_pattern_notifications(self):
        """Clear pattern notifications to allow re-detection."""
        self.pattern_notifications.clear()

# Enhanced logger with error tracking
class EnhancedLogicPwnLogger:
    """Enhanced logger with error pattern detection and tracking."""
    
    def __init__(self, name: str = "logicpwn"):
        from logicpwn.core.logging.logger import LogicPwnLogger
        self.base_logger = LogicPwnLogger(name)
        self.error_tracker = ErrorTracker()
        
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Enhanced error logging with pattern detection."""
        # Use base logger for actual logging
        self.base_logger.log_error(error, context)
        
        # Track error for pattern detection
        error_type = type(error).__name__
        error_message = str(error)
        
        pattern = self.error_tracker.track_error(error_type, error_message, context)
        
        if pattern:
            from logicpwn.core.logging import log_warning
            log_warning(f"Error pattern detected: {pattern.pattern_type}", {
                "error_type": pattern.error_type,
                "frequency": pattern.frequency,
                "recommendation": pattern.recommendation,
                "timespan": f"{pattern.last_occurrence - pattern.first_occurrence:.2f}s"
            })
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics from tracker."""
        return self.error_tracker.get_error_statistics()
    
    def __getattr__(self, name):
        """Delegate other methods to base logger."""
        return getattr(self.base_logger, name)
