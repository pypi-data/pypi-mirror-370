"""
LogicPwn - Business Logic Exploitation & Exploit Chaining Automation Tool.

This package provides a comprehensive suite of security testing tools
with a modular design for advanced business logic exploitation and
multi-step attack automation. Built for penetration testing, security
research, and automated vulnerability assessment.

Key Features:
- Advanced authentication with session persistence
- Exploit chaining workflows
- Modular architecture for easy extension
- Enterprise-grade error handling and logging
- Comprehensive testing and validation
- Centralized configuration management
- Sensitive data redaction and secure logging
- Middleware system for extensibility
- Advanced response analysis and security detection
- High-performance async request execution

Example Usage:
    from logicpwn.core.auth import authenticate_session
    from logicpwn.core.runner import send_request, send_request_advanced
    from logicpwn.core.runner import send_request_async, AsyncRequestRunner
    from logicpwn.models import RequestResult
    
    # Synchronous authentication for exploit chaining
    session = authenticate_session(auth_config)
    
    # Chain exploits with persistent session
    response = session.get("https://target.com/admin/panel")
    response = session.post("https://target.com/api/users", data=payload)
    
    # Use advanced request runner with middleware
    result = send_request_advanced(url="https://target.com/api/data", method="POST")
    if result.has_vulnerabilities():
        print("Security issues detected!")
    
    # High-performance async requests
    async with AsyncRequestRunner() as runner:
        results = await runner.send_requests_batch(request_configs)
"""

from logicpwn.core.auth import authenticate_session, validate_session, logout_session, AuthConfig
from logicpwn.core.runner import send_request, send_request_advanced, RequestConfig, AsyncRequestRunner, AsyncSessionManager, send_request_async, send_requests_batch_async, async_session_manager
from logicpwn.core.performance import PerformanceMonitor, PerformanceBenchmark, MemoryProfiler, monitor_performance, performance_context, get_performance_summary
from logicpwn.core.cache import response_cache, session_cache, config_cache, get_cache_stats, clear_all_caches
from logicpwn.core.stress import StressTester, StressTestConfig, StressTestMetrics, run_quick_stress_test, run_exploit_chain_stress_test
from logicpwn.core.utils import check_indicators, prepare_request_kwargs, validate_config
from logicpwn.core.logging import log_info, log_warning, log_error, log_debug, log_request, log_response
from logicpwn.core.config.config_utils import get_timeout, get_max_retries

from .models import (
    RequestConfig,
    RequestResult,
    RequestMetadata,
    SecurityAnalysis
)

from .exceptions import (
    AuthenticationError,
    LoginFailedException,
    NetworkError,
    ValidationError,
    SessionError,
    TimeoutError
)

__version__ = "0.2.0"
__author__ = "LogicPwn Team"

__all__ = [
    # Authentication
    "authenticate_session",
    "validate_session",
    "logout_session",
    "AuthConfig",
    
    # Request Execution
    "send_request",
    "send_request_advanced",
    "RequestConfig",
    
    # Response Validation
    # REMOVED: "validate_response",
    # REMOVED: "extract_from_response",
    # REMOVED: "validate_json_response",
    # REMOVED: "validate_html_response",
    # REMOVED: "chain_validations",
    # REMOVED: "ValidationResult",
    # REMOVED: "ValidationConfig",
    # REMOVED: "ValidationType",
    # REMOVED: "VulnerabilityPatterns",
    
    # Async Execution
    "AsyncRequestRunner",
    "AsyncSessionManager",
    "send_request_async",
    "send_requests_batch_async",
    "async_session_manager",
    
    # Performance & Caching
    "PerformanceMonitor",
    "PerformanceBenchmark",
    "MemoryProfiler",
    "monitor_performance",
    "performance_context",
    "get_performance_summary",
    "response_cache",
    "session_cache",
    "config_cache",
    "get_cache_stats",
    "clear_all_caches",
    
    # Stress Testing
    "StressTester",
    "StressTestConfig",
    "StressTestMetrics",
    "run_quick_stress_test",
    "run_exploit_chain_stress_test",
    
    # Utilities
    "check_indicators",
    "prepare_request_kwargs",
    "validate_config",
    "config",
    "get_timeout",
    "get_max_retries",
    "log_info",
    "log_warning",
    "log_error",
    "log_debug",
    "log_request",
    "log_response"
] 