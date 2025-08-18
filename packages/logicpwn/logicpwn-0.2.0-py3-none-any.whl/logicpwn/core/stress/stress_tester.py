"""
Stress testing and load testing module for LogicPwn.

This module provides comprehensive stress testing capabilities for
security testing workflows, including concurrent exploit chains,
performance metrics, and load testing scenarios.

Key Features:
- Concurrent exploit chain execution
- Performance metrics and monitoring
- Rate limiting and throttling
- Memory and CPU monitoring
- Comprehensive reporting
- Configurable test scenarios
- Error rate analysis

Usage::

    # Basic stress testing
    from logicpwn.core.stress_tester import StressTester
    
    tester = StressTester(max_concurrent=50, duration=300)
    results = await tester.run_stress_test(target_configs)
    
    # Advanced load testing with metrics
    async with StressTester() as tester:
                                            metrics = await tester.run_load_test(
                                                target_urls=urls,
                                                exploit_chains=chains,
                                                max_concurrent=100,
                                                duration=600
                                            )
                                            print(f"Requests/sec: {metrics.requests_per_second}")
                                            print(f"Error rate: {metrics.error_rate:.2f}%")
"""

import asyncio
import time
import psutil
import statistics
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from collections import defaultdict
import json
from datetime import datetime

from logicpwn.core.runner.async_runner_core import AsyncRequestRunner
from logicpwn.core.runner.async_session_manager import AsyncSessionManager
from logicpwn.core.performance import PerformanceMonitor, PerformanceBenchmark
from logicpwn.models.request_result import RequestResult
from logicpwn.exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from logicpwn.core.logging import log_info, log_warning, log_error


@dataclass
class StressTestConfig:
    """Configuration for stress testing."""
    max_concurrent: int = 50
    duration: int = 300  # 5 minutes
    rate_limit: Optional[float] = None  # requests per second
    timeout: int = 30
    verify_ssl: bool = True
    memory_monitoring: bool = True
    cpu_monitoring: bool = True
    error_threshold: float = 0.1  # 10% error rate threshold
    warmup_duration: int = 30  # 30 seconds warmup


@dataclass
class StressTestMetrics:
    """Metrics from stress testing."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    requests_per_second: float = 0.0
    average_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    status_code_distribution: Dict[int, int] = field(default_factory=dict)
    error_distribution: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
                                            """Convert metrics to dictionary."""
                                            return {
                                                "total_requests": self.total_requests,
                                                "successful_requests": self.successful_requests,
                                                "failed_requests": self.failed_requests,
                                                "total_duration": self.total_duration,
                                                "requests_per_second": self.requests_per_second,
                                                "average_response_time": self.average_response_time,
                                                "median_response_time": self.median_response_time,
                                                "p95_response_time": self.p95_response_time,
                                                "p99_response_time": self.p99_response_time,
                                                "error_rate": self.error_rate,
                                                "memory_usage_mb": self.memory_usage_mb,
                                                "cpu_usage_percent": self.cpu_usage_percent,
                                                "peak_memory_mb": self.peak_memory_mb,
                                                "peak_cpu_percent": self.peak_cpu_percent,
                                                "status_code_distribution": self.status_code_distribution,
                                                "error_distribution": self.error_distribution,
                                                "timestamp": self.timestamp.isoformat()
                                            }

    def __str__(self) -> str:
                                            return (f"StressTestMetrics("
                                                    f"requests={self.total_requests}, "
                                                    f"rps={self.requests_per_second:.2f}, "
                                                    f"error_rate={self.error_rate:.2f}%, "
                                                    f"avg_time={self.average_response_time:.3f}s)")


class StressTester:
    """Comprehensive stress testing for LogicPwn security workflows."""
    
    def __init__(self, config: Optional[StressTestConfig] = None):
                                            """
                                            Initialize stress tester.
                                            
                                            Args:
                                                config: Stress test configuration
                                            """
                                            self.config = config or StressTestConfig()
                                            self.metrics = StressTestMetrics()
                                            self.response_times: List[float] = []
                                            self.memory_samples: List[float] = []
                                            self.cpu_samples: List[float] = []
                                            self.start_time: Optional[float] = None
                                            self.end_time: Optional[float] = None
                                            self._monitoring_task: Optional[asyncio.Task] = None
                                            
    async def __aenter__(self):
                                            """Async context manager entry."""
                                            return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
                                            """Async context manager exit."""
                                            if self._monitoring_task:
                                                self._monitoring_task.cancel()
                                                try:
                                                    await self._monitoring_task
                                                except asyncio.CancelledError:
                                                    pass
    
    async def run_stress_test(self, 
                                                                 target_configs: List[Dict[str, Any]],
                                                                 auth_config: Optional[Dict[str, Any]] = None) -> StressTestMetrics:
                                            """
                                            Run a basic stress test with concurrent requests.
                                            
                                            Args:
                                                target_configs: List of request configurations
                                                auth_config: Optional authentication configuration
                                                
                                            Returns:
                                                StressTestMetrics with test results
                                            """
                                            log_info("Starting stress test", {
                                                "max_concurrent": self.config.max_concurrent,
                                                "duration": self.config.duration,
                                                "targets": len(target_configs)
                                            })
                                            
                                            self.start_time = time.time()
                                            
                                                # Start monitoring
                                            if self.config.memory_monitoring or self.config.cpu_monitoring:
                                                self._monitoring_task = asyncio.create_task(self._monitor_system_resources())
                                            
                                                # Warmup phase
                                            if self.config.warmup_duration > 0:
                                                await self._warmup_phase(target_configs, auth_config)
                                            
                                                # Main stress test
                                            await self._run_concurrent_requests(target_configs, auth_config)
                                            
                                            self.end_time = time.time()
                                            self._calculate_metrics()
                                            
                                            log_info("Stress test completed", {
                                                "total_requests": self.metrics.total_requests,
                                                "error_rate": f"{self.metrics.error_rate:.2f}%",
                                                "requests_per_second": f"{self.metrics.requests_per_second:.2f}"
                                            })
                                            
                                            return self.metrics
    
    async def run_load_test(self,
                                                               target_urls: List[str],
                                                               exploit_chains: List[List[Dict[str, Any]]],
                                                               auth_config: Optional[Dict[str, Any]] = None) -> StressTestMetrics:
                                            """
                                            Run a load test with exploit chains.
                                            
                                            Args:
                                                target_urls: List of target URLs
                                                exploit_chains: List of exploit chain configurations
                                                auth_config: Optional authentication configuration
                                                
                                            Returns:
                                                StressTestMetrics with test results
                                            """
                                            log_info("Starting load test with exploit chains", {
                                                "targets": len(target_urls),
                                                "exploit_chains": len(exploit_chains),
                                                "max_concurrent": self.config.max_concurrent
                                            })
                                            
                                            self.start_time = time.time()
                                            
                                                # Start monitoring
                                            if self.config.memory_monitoring or self.config.cpu_monitoring:
                                                self._monitoring_task = asyncio.create_task(self._monitor_system_resources())
                                            
                                                # Run exploit chains concurrently
                                            await self._run_exploit_chains(target_urls, exploit_chains, auth_config)
                                            
                                            self.end_time = time.time()
                                            self._calculate_metrics()
                                            
                                            return self.metrics
    
    async def run_burst_test(self,
                                                                target_config: Dict[str, Any],
                                                                burst_size: int = 100,
                                                                burst_count: int = 5,
                                                                auth_config: Optional[Dict[str, Any]] = None) -> StressTestMetrics:
                                            """
                                            Run burst testing with rapid request sequences.
                                            
                                            Args:
                                                target_config: Request configuration
                                                burst_size: Number of requests per burst
                                                burst_count: Number of bursts
                                                auth_config: Optional authentication configuration
                                                
                                            Returns:
                                                StressTestMetrics with test results
                                            """
                                            log_info("Starting burst test", {
                                                "burst_size": burst_size,
                                                "burst_count": burst_count,
                                                "target": target_config.get("url", "unknown")
                                            })
                                            
                                            self.start_time = time.time()
                                            
                                                # Start monitoring
                                            if self.config.memory_monitoring or self.config.cpu_monitoring:
                                                self._monitoring_task = asyncio.create_task(self._monitor_system_resources())
                                            
                                                # Run bursts
                                            for burst_num in range(burst_count):
                                                log_info(f"Executing burst {burst_num + 1}/{burst_count}")
                                                await self._run_burst(target_config, burst_size, auth_config)
                                                
                                                # Brief pause between bursts
                                                if burst_num < burst_count - 1:
                                                    await asyncio.sleep(1)
                                            
                                            self.end_time = time.time()
                                            self._calculate_metrics()
                                            
                                            return self.metrics
    
    async def _warmup_phase(self, 
                                                               target_configs: List[Dict[str, Any]],
                                                               auth_config: Optional[Dict[str, Any]] = None):
                                            """Run warmup phase to establish connections."""
                                            log_info(f"Warming up for {self.config.warmup_duration} seconds")
                                            
                                            warmup_start = time.time()
                                            warmup_requests = 0
                                            
                                            async with AsyncRequestRunner(max_concurrent=5) as runner:
                                                while time.time() - warmup_start < self.config.warmup_duration:
                                                    # Send a few warmup requests
                                                    for config in target_configs[:3]:  # Use first 3 configs
                                                        try:
                                                            await runner.send_request(**config)
                                                            warmup_requests += 1
                                                        except Exception as e:
                                                            log_warning(f"Warmup request failed: {e}")
                                                    
                                                    await asyncio.sleep(0.1)  # Small delay
                                            
                                            log_info(f"Warmup completed: {warmup_requests} requests")
    
    async def _run_concurrent_requests(self,
                                                                         target_configs: List[Dict[str, Any]],
                                                                         auth_config: Optional[Dict[str, Any]] = None):
                                            """Run concurrent requests for stress testing."""
                                            semaphore = asyncio.Semaphore(self.config.max_concurrent)
                                            
                                            async def execute_request(config: Dict[str, Any]) -> None:
                                                async with semaphore:
                                                    start_time = time.time()
                                                    
                                                    try:
                                                        if auth_config:
                                                            async with AsyncSessionManager(auth_config=auth_config) as session:
                                                                result = await session._send_authenticated_request(
                                                                    method=config.get("method", "GET"),
                                                                    url=config["url"],
                                                                    **{k: v for k, v in config.items() if k not in ["method", "url"]}
                                                                )
                                                        else:
                                                            async with AsyncRequestRunner() as runner:
                                                                result = await runner.send_request(**config)
                                                        
                                                        response_time = time.time() - start_time
                                                        self.response_times.append(response_time)
                                                        
                                                        # Update metrics
                                                        self.metrics.total_requests += 1
                                                        self.metrics.successful_requests += 1
                                                        
                                                        # Status code distribution
                                                        status_code = result.status_code if hasattr(result, 'status_code') else 0
                                                        self.metrics.status_code_distribution[status_code] = \
                                                            self.metrics.status_code_distribution.get(status_code, 0) + 1
                                                        
                                                    except Exception as e:
                                                        response_time = time.time() - start_time
                                                        self.response_times.append(response_time)
                                                        
                                                        # Update metrics
                                                        self.metrics.total_requests += 1
                                                        self.metrics.failed_requests += 1
                                                        
                                                        # Error distribution
                                                        error_type = type(e).__name__
                                                        self.metrics.error_distribution[error_type] = \
                                                            self.metrics.error_distribution.get(error_type, 0) + 1
                                                        
                                                        log_warning(f"Request failed: {e}")
                                            
                                                # Create tasks for all requests
                                            tasks = []
                                            test_end_time = time.time() + self.config.duration
                                            
                                            while time.time() < test_end_time:
                                                for config in target_configs:
                                                    if time.time() >= test_end_time:
                                                        break
                                                    tasks.append(asyncio.create_task(execute_request(config)))
                                                
                                                # Wait for some tasks to complete before adding more
                                                if len(tasks) >= self.config.max_concurrent * 2:
                                                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                                                    tasks = list(pending)
                                            
                                                # Wait for remaining tasks
                                            if tasks:
                                                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_exploit_chains(self,
                                                                     target_urls: List[str],
                                                                     exploit_chains: List[List[Dict[str, Any]]],
                                                                     auth_config: Optional[Dict[str, Any]] = None):
                                            """Run exploit chains concurrently."""
                                            semaphore = asyncio.Semaphore(self.config.max_concurrent)
                                            
                                            async def execute_exploit_chain(chain: List[Dict[str, Any]], target_url: str) -> None:
                                                async with semaphore:
                                                    try:
                                                        async with AsyncSessionManager(auth_config=auth_config) as session:
                                                            if auth_config:
                                                                await session.authenticate()
                                                            
                                                            for step_num, step_config in enumerate(chain):
                                                                start_time = time.time()
                                                                
                                                                # Update URL with target
                                                                step_config["url"] = step_config["url"].replace(
                                                                    "https://target.com", target_url
                                                                )
                                                                
                                                                result = await session._send_authenticated_request(
                                                                    method=step_config.get("method", "GET"),
                                                                    url=step_config["url"],
                                                                    **{k: v for k, v in step_config.items() 
                                                                       if k not in ["method", "url"]}
                                                                )
                                                                
                                                                response_time = time.time() - start_time
                                                                self.response_times.append(response_time)
                                                                
                                                                # Update metrics
                                                                self.metrics.total_requests += 1
                                                                self.metrics.successful_requests += 1
                                                                
                                                                # Status code distribution
                                                                status_code = result.status_code if hasattr(result, 'status_code') else 0
                                                                self.metrics.status_code_distribution[status_code] = \
                                                                    self.metrics.status_code_distribution.get(status_code, 0) + 1
                                                                
                                                    except Exception as e:
                                                        self.metrics.total_requests += 1
                                                        self.metrics.failed_requests += 1
                                                        
                                                        # Error distribution
                                                        error_type = type(e).__name__
                                                        self.metrics.error_distribution[error_type] = \
                                                            self.metrics.error_distribution.get(error_type, 0) + 1
                                                        
                                                        log_warning(f"Exploit chain failed: {e}")
                                            
                                                # Create tasks for all exploit chains
                                            tasks = []
                                            for i, chain in enumerate(exploit_chains):
                                                target_url = target_urls[i % len(target_urls)]
                                                tasks.append(asyncio.create_task(execute_exploit_chain(chain, target_url)))
                                            
                                                # Execute all chains
                                            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_burst(self,
                                                            target_config: Dict[str, Any],
                                                            burst_size: int,
                                                            auth_config: Optional[Dict[str, Any]] = None):
                                            """Run a burst of requests."""
                                            tasks = []
                                            
                                            for _ in range(burst_size):
                                                tasks.append(asyncio.create_task(self._execute_single_request(target_config, auth_config)))
                                            
                                            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_request(self,
                                                                        config: Dict[str, Any],
                                                                        auth_config: Optional[Dict[str, Any]] = None) -> None:
                                            """Execute a single request and update metrics."""
                                            start_time = time.time()
                                            
                                            try:
                                                if auth_config:
                                                    async with AsyncSessionManager(auth_config=auth_config) as session:
                                                        result = await session._send_authenticated_request(
                                                            method=config.get("method", "GET"),
                                                            url=config["url"],
                                                            **{k: v for k, v in config.items() if k not in ["method", "url"]}
                                                        )
                                                else:
                                                    async with AsyncRequestRunner() as runner:
                                                        result = await runner.send_request(**config)
                                                
                                                response_time = time.time() - start_time
                                                self.response_times.append(response_time)
                                                
                                                # Update metrics
                                                self.metrics.total_requests += 1
                                                self.metrics.successful_requests += 1
                                                
                                                # Status code distribution
                                                status_code = result.status_code if hasattr(result, 'status_code') else 0
                                                self.metrics.status_code_distribution[status_code] = \
                                                    self.metrics.status_code_distribution.get(status_code, 0) + 1
                                                
                                            except Exception as e:
                                                response_time = time.time() - start_time
                                                self.response_times.append(response_time)
                                                
                                                # Update metrics
                                                self.metrics.total_requests += 1
                                                self.metrics.failed_requests += 1
                                                
                                                # Error distribution
                                                error_type = type(e).__name__
                                                self.metrics.error_distribution[error_type] = \
                                                    self.metrics.error_distribution.get(error_type, 0) + 1
    
    async def _monitor_system_resources(self):
                                            """Monitor system resources during testing."""
                                            while True:
                                                try:
                                                    # Memory usage
                                                    if self.config.memory_monitoring:
                                                        process = psutil.Process()
                                                        memory_mb = process.memory_info().rss / 1024 / 1024
                                                        self.memory_samples.append(memory_mb)
                                                        self.metrics.peak_memory_mb = max(self.metrics.peak_memory_mb, memory_mb)
                                                    
                                                    # CPU usage
                                                    if self.config.cpu_monitoring:
                                                        cpu_percent = psutil.cpu_percent(interval=1)
                                                        self.cpu_samples.append(cpu_percent)
                                                        self.metrics.peak_cpu_percent = max(self.metrics.peak_cpu_percent, cpu_percent)
                                                    
                                                    await asyncio.sleep(1)
                                                    
                                                except asyncio.CancelledError:
                                                    break
                                                except Exception as e:
                                                    log_error(f"Resource monitoring error: {e}")
                                                    await asyncio.sleep(1)
    
    def _calculate_metrics(self):
                                            """Calculate final metrics from collected data."""
                                            if not self.response_times:
                                                return
                                            
                                                # Basic metrics
                                            self.metrics.total_duration = self.end_time - self.start_time
                                            self.metrics.requests_per_second = self.metrics.total_requests / self.metrics.total_duration
                                            self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
                                            
                                                # Response time metrics
                                            sorted_times = sorted(self.response_times)
                                            self.metrics.average_response_time = statistics.mean(sorted_times)
                                            self.metrics.median_response_time = statistics.median(sorted_times)
                                            
                                            if len(sorted_times) >= 20:
                                                self.metrics.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
                                                self.metrics.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
                                            
                                                # System resource metrics
                                            if self.memory_samples:
                                                self.metrics.memory_usage_mb = statistics.mean(self.memory_samples)
                                            
                                            if self.cpu_samples:
                                                self.metrics.cpu_usage_percent = statistics.mean(self.cpu_samples)
    
    def generate_report(self, output_format: str = "json") -> str:
                                            """
                                            Generate a comprehensive test report.
                                            
                                            Args:
                                                output_format: Report format ("json", "text", "html")
                                                
                                            Returns:
                                                Formatted report string
                                            """
                                            if output_format == "json":
                                                return json.dumps(self.metrics.to_dict(), indent=2)
                                            
                                            elif output_format == "text":
                                                report = f"""
Stress Test Report
==================

Test Configuration:
- Max Concurrent: {self.config.max_concurrent}
- Duration: {self.config.duration}s
- Rate Limit: {self.config.rate_limit or 'None'} req/s

Results:
- Total Requests: {self.metrics.total_requests}
- Successful: {self.metrics.successful_requests}
- Failed: {self.metrics.failed_requests}
- Error Rate: {self.metrics.error_rate:.2f}%

Performance:
- Requests/Second: {self.metrics.requests_per_second:.2f}
- Average Response Time: {self.metrics.average_response_time:.3f}s
- Median Response Time: {self.metrics.median_response_time:.3f}s
- P95 Response Time: {self.metrics.p95_response_time:.3f}s
- P99 Response Time: {self.metrics.p99_response_time:.3f}s

System Resources:
- Average Memory Usage: {self.metrics.memory_usage_mb:.2f} MB
- Peak Memory Usage: {self.metrics.peak_memory_mb:.2f} MB
- Average CPU Usage: {self.metrics.cpu_usage_percent:.1f}%
- Peak CPU Usage: {self.metrics.peak_cpu_percent:.1f}%

Status Code Distribution:
"""
                                                for status_code, count in sorted(self.metrics.status_code_distribution.items()):
                                                    percentage = (count / self.metrics.total_requests) * 100
                                                    report += f"- {status_code}: {count} ({percentage:.1f}%)\n"
                                                
                                                if self.metrics.error_distribution:
                                                    report += "\nError Distribution:\n"
                                                    for error_type, count in self.metrics.error_distribution.items():
                                                        percentage = (count / self.metrics.total_requests) * 100
                                                        report += f"- {error_type}: {count} ({percentage:.1f}%)\n"
                                                
                                                return report
                                            
                                            else:
                                                raise ValueError(f"Unsupported output format: {output_format}")


# Convenience functions
async def run_quick_stress_test(target_urls: List[str],
                                                                   duration: int = 60,
                                                                   max_concurrent: int = 20) -> StressTestMetrics:
    """
    Run a quick stress test with basic configuration.
    
    Args:
                                            target_urls: List of target URLs
                                            duration: Test duration in seconds
                                            max_concurrent: Maximum concurrent requests
                                            
    Returns:
                                            StressTestMetrics with results
    """
    config = StressTestConfig(
                                            max_concurrent=max_concurrent,
                                            duration=duration,
                                            warmup_duration=10
    )
    
    async with StressTester(config) as tester:
                                            target_configs = [{"url": url, "method": "GET"} for url in target_urls]
                                            return await tester.run_stress_test(target_configs)


async def run_exploit_chain_stress_test(exploit_chains: List[List[Dict[str, Any]]],
                                                                           target_urls: List[str],
                                                                           auth_config: Optional[Dict[str, Any]] = None,
                                                                           duration: int = 300) -> StressTestMetrics:
    """
    Run stress test with exploit chains.
    
    Args:
                                            exploit_chains: List of exploit chain configurations
                                            target_urls: List of target URLs
                                            auth_config: Optional authentication configuration
                                            duration: Test duration in seconds
                                            
    Returns:
                                            StressTestMetrics with results
    """
    config = StressTestConfig(
                                            max_concurrent=10,  # Lower for exploit chains
                                            duration=duration,
                                            warmup_duration=30
    )
    
    async with StressTester(config) as tester:
                                            return await tester.run_load_test(target_urls, exploit_chains, auth_config) 