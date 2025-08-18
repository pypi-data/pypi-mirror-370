"""
Performance monitoring context manager, decorator, and monitor class for LogicPwn.
"""
import time
import psutil
import threading
from typing import List, Optional, Callable, Any, Dict
from contextlib import contextmanager
from logicpwn.core.performance.performance_metrics import PerformanceMetrics

class PerformanceMonitor:
    """Real-time performance monitoring."""
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.current_operation: Optional[str] = None
        self.start_time: Optional[float] = None
        self.start_memory: Optional[float] = None
        self.peak_memory: float = 0
        self._lock = threading.Lock()

    def __enter__(self):
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring()

    def start_monitoring(self, operation_name: str = "default"):
        with self._lock:
            self.current_operation = operation_name
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss
            self.peak_memory = self.start_memory

    def stop_monitoring(self) -> Optional[PerformanceMetrics]:
        if not self.start_time:
            return None
        with self._lock:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            duration = end_time - self.start_time
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics = PerformanceMetrics(
                operation_name=self.current_operation,
                duration=duration,
                memory_before=self.start_memory,
                memory_after=end_memory,
                memory_peak=self.peak_memory,
                cpu_percent=cpu_percent
            )
            self.metrics.append(metrics)
            self.current_operation = None
            self.start_time = None
            self.start_memory = None
            self.peak_memory = 0
            return metrics

    def monitor_operation(self, operation_name: str):
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                self.start_monitoring(operation_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.stop_monitoring()
            return wrapper
        return decorator

    def get_metrics(self) -> List[PerformanceMetrics]:
        with self._lock:
            return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        import statistics
        if not self.metrics:
            return {}
        durations = [m.duration for m in self.metrics]
        memory_deltas = [m.memory_delta for m in self.metrics]
        cpu_percents = [m.cpu_percent for m in self.metrics]
        return {
            'total_operations': len(self.metrics),
            'total_duration': sum(durations),
            'average_duration': statistics.mean(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_memory_delta': sum(memory_deltas),
            'average_memory_delta': statistics.mean(memory_deltas),
            'peak_memory_usage': max(m.memory_peak for m in self.metrics),
            'average_cpu_percent': statistics.mean(cpu_percents),
            'operations': [m.operation_name for m in self.metrics]
        }

def monitor_performance(operation_name: str):
    """Decorator for monitoring performance of a function."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start_monitoring(operation_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.stop_monitoring()
        return wrapper
    return decorator

def monitor_async_performance(operation_name: str):
    """Decorator for monitoring performance of an async function."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start_monitoring(operation_name)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                monitor.stop_monitoring()
        return wrapper
    return decorator

@contextmanager
def performance_context(operation_name: str):
    """Context manager for performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring(operation_name)
    try:
        yield monitor
    finally:
        monitor.stop_monitoring() 