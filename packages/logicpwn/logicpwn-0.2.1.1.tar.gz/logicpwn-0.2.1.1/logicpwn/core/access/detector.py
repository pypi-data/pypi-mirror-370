from typing import List, Union, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from logicpwn.core.performance.performance_monitor import monitor_performance
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner
from logicpwn.core.reliability import AdaptiveRateLimiter, RateLimitConfig, rate_limiter_registry
from logicpwn.core.reliability import record_security_event, SecurityEventType, SecuritySeverity
import asyncio
import copy
import threading
import time
from .models import AccessTestResult, AccessDetectorConfig
from .utils import (
    _validate_inputs, _sanitize_test_id, _test_single_id, _test_single_id_async, _test_single_id_with_baselines, _test_single_id_with_baselines_async
)

def _get_request_config_for_id(config: AccessDetectorConfig, test_id: Union[str, int]) -> dict:
    """Helper to get method and request data for a given test ID."""
    method = config.method or "GET"
    data = None
    if config.request_data_map and test_id in config.request_data_map:
        data = config.request_data_map[test_id]
    return {"method": method, "data": data}

def _create_thread_safe_session(base_session: requests.Session) -> requests.Session:
    """
    Create a thread-safe copy of a session for concurrent use.
    
    Each thread gets its own session instance to prevent race conditions
    while preserving authentication state and configuration.
    """
    # Create a new session instance
    thread_session = requests.Session()
    
    # Copy authentication and configuration from the base session
    thread_session.cookies.update(base_session.cookies)
    thread_session.headers.update(base_session.headers)
    thread_session.auth = base_session.auth
    thread_session.proxies = base_session.proxies.copy()
    thread_session.verify = base_session.verify
    thread_session.cert = base_session.cert
    thread_session.trust_env = base_session.trust_env
    thread_session.max_redirects = base_session.max_redirects
    
    # Copy adapters for connection pooling configuration
    for prefix, adapter in base_session.adapters.items():
        # Create new adapter instance to avoid sharing connection pools
        new_adapter = requests.adapters.HTTPAdapter(
            pool_connections=getattr(adapter, 'config', {}).get('pool_connections', 10),
            pool_maxsize=getattr(adapter, 'config', {}).get('pool_maxsize', 10)
        )
        thread_session.mount(prefix, new_adapter)
    
    return thread_session

def _test_single_id_with_rate_limiting(
    session: requests.Session, 
    url: str, 
    test_id: Union[str, int],
    method: str,
    request_data: Optional[dict],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig,
    rate_limiter: AdaptiveRateLimiter
) -> AccessTestResult:
    """
    Execute single ID test with adaptive rate limiting.
    
    This wrapper adds rate limiting around the core testing logic
    to prevent overwhelming target servers and adapt to response patterns.
    """
    # Apply rate limiting delay if needed
    delay_applied = rate_limiter.wait_if_needed()
    
    # Record start time for response time measurement
    start_time = time.time()
    
    try:
        # Execute the actual test
        result = _test_single_id_with_baselines(
            session, url, test_id, method, request_data,
            success_indicators, failure_indicators, request_timeout, config
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record request metrics for rate limiter adaptation
        rate_limiter.record_request(
            response_time=response_time,
            status_code=result.status_code,
            exception=None if result.error_message is None else Exception(result.error_message)
        )
        
        return result
        
    except Exception as e:
        # Record failed request for rate limiter adaptation
        response_time = time.time() - start_time
        rate_limiter.record_request(
            response_time=response_time,
            status_code=0,
            exception=e
        )
        raise
    """
    Create a thread-safe copy of a session for concurrent use.
    
    Each thread gets its own session instance to prevent race conditions
    while preserving authentication state and configuration.
    """
    # Create a new session instance
    thread_session = requests.Session()
    
    # Copy authentication and configuration from the base session
    thread_session.cookies.update(base_session.cookies)
    thread_session.headers.update(base_session.headers)
    thread_session.auth = base_session.auth
    thread_session.proxies = base_session.proxies.copy()
    thread_session.verify = base_session.verify
    thread_session.cert = base_session.cert
    thread_session.trust_env = base_session.trust_env
    thread_session.max_redirects = base_session.max_redirects
    
    # Copy adapters for connection pooling configuration
    for prefix, adapter in base_session.adapters.items():
        # Create new adapter instance to avoid sharing connection pools
        new_adapter = requests.adapters.HTTPAdapter(
            pool_connections=getattr(adapter, 'config', {}).get('pool_connections', 10),
            pool_maxsize=getattr(adapter, 'config', {}).get('pool_maxsize', 10)
        )
        thread_session.mount(prefix, new_adapter)
    
    return thread_session

def _test_single_id_with_rate_limiting(
    session: requests.Session, 
    url: str, 
    test_id: Union[str, int],
    method: str,
    request_data: Optional[dict],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig,
    rate_limiter: AdaptiveRateLimiter
) -> AccessTestResult:
    """
    Execute single ID test with adaptive rate limiting.
    
    This wrapper adds rate limiting around the core testing logic
    to prevent overwhelming target servers and adapt to response patterns.
    """
    # Apply rate limiting delay if needed
    delay_applied = rate_limiter.wait_if_needed()
    
    # Record start time for response time measurement
    start_time = time.time()
    
    try:
        # Execute the actual test
        result = _test_single_id_with_baselines(
            session, url, test_id, method, request_data,
            success_indicators, failure_indicators, request_timeout, config
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record request metrics for rate limiter adaptation
        rate_limiter.record_request(
            response_time=response_time,
            status_code=result.status_code,
            exception=None if result.error_message is None else Exception(result.error_message)
        )
        
        return result
        
    except Exception as e:
        # Record failed request for rate limiter adaptation
        response_time = time.time() - start_time
        rate_limiter.record_request(
            response_time=response_time,
            status_code=0,
            exception=e
        )
        raise

@monitor_performance("idor_detection_batch")
def detect_idor_flaws(
    session: requests.Session,
    endpoint_template: str,
    test_ids: List[Union[str, int]],
    success_indicators: List[str],
    failure_indicators: List[str],
    config: Optional[AccessDetectorConfig] = None
) -> List[AccessTestResult]:
    """
    Run IDOR/access control tests for a list of IDs, supporting custom HTTP methods, per-ID data, and multiple baselines.
    
    THREAD SAFETY: Creates isolated session copies for each worker thread to prevent race conditions.
    ADAPTIVE RATE LIMITING: Automatically adjusts request delays based on server response patterns.
    """
    config = config or AccessDetectorConfig()
    _validate_inputs(endpoint_template, test_ids, success_indicators, failure_indicators)
    results: List[AccessTestResult] = []
    
    # Initialize adaptive rate limiter
    rate_limit_config = RateLimitConfig(
        base_delay=config.rate_limit or 0.1,
        max_delay=30.0,
        min_delay=0.01,
        backoff_multiplier=2.0,
        recovery_factor=0.8
    )
    rate_limiter = rate_limiter_registry.get_limiter(
        f"idor_detection_{endpoint_template.replace('/', '_')}", 
        rate_limit_config
    )
    
    with ThreadPoolExecutor(max_workers=config.max_concurrent_requests) as executor:
        futures = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            req_cfg = _get_request_config_for_id(config, test_id)
            
            # Create thread-safe session copy for each worker
            thread_safe_session = _create_thread_safe_session(session)
            
            # Use rate-limited testing function
            futures.append(executor.submit(
                _test_single_id_with_rate_limiting,
                thread_safe_session,  # Use thread-safe session copy
                url,
                sanitized_id,
                req_cfg["method"],
                req_cfg["data"],
                success_indicators,
                failure_indicators,
                config.request_timeout,
                config,
                rate_limiter  # Pass rate limiter instance
            ))
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)                # Record security events for detected vulnerabilities
            if result.is_vulnerable:
                record_security_event(
                    SecurityEventType.IDOR_VULNERABILITY,
                    SecuritySeverity.HIGH,
                    f"IDOR vulnerability detected: {result.id_tested} - {getattr(result, 'vulnerability_evidence', 'N/A')[:200]}...",
                    metadata={
                        "test_id": result.id_tested,
                        "url": result.endpoint_url,
                        "status_code": result.status_code,
                        "evidence": getattr(result, 'vulnerability_evidence', 'N/A')[:500],  # Limit evidence size
                        "detection_method": "batch_detection"
                    },
                    source_module="idor_detector"
                )
            elif result.error_message:
                record_security_event(
                    SecurityEventType.SUSPICIOUS_REQUEST,
                    SecuritySeverity.MEDIUM,
                    f"IDOR test error for {result.id_tested}: {result.error_message[:100]}",
                    metadata={
                        "test_id": result.id_tested,
                        "url": result.endpoint_url,
                        "error": result.error_message
                    },
                    source_module="idor_detector"
                )
    
    # Check for potential memory leaks with large result sets
    if len(results) > 1000:
        record_security_event(
            SecurityEventType.MEMORY_LEAK_WARNING,
            SecuritySeverity.MEDIUM,
            f"Large IDOR result set detected: {len(results)} results may consume significant memory",
            metadata={
                "result_count": len(results),
                "endpoint_template": endpoint_template,
                "test_id_count": len(test_ids)
            },
            source_module="idor_detector"
        )
    
    # Log rate limiter metrics after completion
    from logicpwn.core.logging import log_info
    rl_metrics = rate_limiter.get_metrics()
    log_info(f"IDOR detection rate limiting metrics", rl_metrics)
    
    return results

async def detect_idor_flaws_async(
    endpoint_template: str,
    test_ids: List[Union[str, int]],
    success_indicators: List[str],
    failure_indicators: List[str],
    config: Optional[AccessDetectorConfig] = None
) -> List[AccessTestResult]:
    """
    Async version of IDOR/access control tests, supporting custom HTTP methods, per-ID data, and multiple baselines.
    """
    config = config or AccessDetectorConfig()
    _validate_inputs(endpoint_template, test_ids, success_indicators, failure_indicators)
    results: List[AccessTestResult] = []
    async with AsyncRequestRunner(max_concurrent=config.max_concurrent_requests, timeout=config.request_timeout) as runner:
        tasks = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            req_cfg = _get_request_config_for_id(config, test_id)
            tasks.append(_test_single_id_with_baselines_async(
                runner,
                url,
                sanitized_id,
                req_cfg["method"],
                req_cfg["data"],
                success_indicators,
                failure_indicators,
                config.request_timeout,
                config
            ))
        results = await asyncio.gather(*tasks)
    return results 