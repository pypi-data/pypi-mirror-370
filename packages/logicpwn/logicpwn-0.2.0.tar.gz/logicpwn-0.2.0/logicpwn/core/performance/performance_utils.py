"""
Performance utility functions for LogicPwn performance monitoring.
"""
from typing import Dict, Any
from logicpwn.core.performance.performance_monitor import PerformanceMonitor

def get_performance_summary() -> Dict[str, Any]:
    """Get a summary of all performance metrics collected so far."""
    monitor = PerformanceMonitor()
    return monitor.get_summary() 