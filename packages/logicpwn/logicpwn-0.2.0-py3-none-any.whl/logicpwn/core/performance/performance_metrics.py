"""
Performance metrics dataclass and helpers for LogicPwn performance monitoring.
"""
import time
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    operation_name: str
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def memory_delta(self) -> float:
        """Memory usage change."""
        return self.memory_after - self.memory_before

    @property
    def memory_usage_mb(self) -> float:
        """Memory usage in MB."""
        return self.memory_after / 1024 / 1024 