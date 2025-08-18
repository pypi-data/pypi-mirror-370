"""
Request execution engine for LogicPwn Business Logic Exploitation Framework.

This module provides HTTP request execution functionality using authenticated
sessions from the auth module. Designed for exploit chaining and multi-step
security testing workflows.

Key Features:
- Send authenticated requests using sessions from auth module
- Support all HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD)
- Flexible request configuration via dict or RequestConfig object
- Multiple body types (JSON, form data, raw body)
- Request metadata collection (timing, status, etc.)
- Comprehensive error handling with detailed exceptions
- Secure request/response logging without sensitive data
- Middleware integration for extensibility
- Advanced response analysis with RequestResult

Usage::

    # Send authenticated request for exploit chaining
    session = authenticate_session(auth_config)
    response = send_request(session, request_config)
    
    # Use response for subsequent exploit steps
    if response.status_code == 200:
        exploit_data = response.json()
    
    # Use advanced runner with middleware and analysis
    result = send_request_advanced(url="https://target.com/api/data", method="POST")
    if result.has_vulnerabilities():
        print("Security issues detected!")

"""

import requests
import time
import uuid
from typing import Dict, Optional, Any, Union
from loguru import logger
import re

from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestResult, RequestMetadata
from logicpwn.exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from logicpwn.core.config.config_utils import get_timeout, get_max_retries
from logicpwn.core.logging import log_request, log_response, log_error
from logicpwn.core.middleware import (
    middleware_manager, MiddlewareContext, RetryException
)
from logicpwn.core.utils import prepare_request_kwargs, validate_config
from logicpwn.core.performance import monitor_performance, performance_context
from logicpwn.core.cache import response_cache

# Module constants for maintainability and configuration
MAX_RESPONSE_TEXT_LENGTH = 500


def _validate_body_types(data: Optional[Dict[str, Any]], json_data: Optional[Dict[str, Any]], raw_body: Optional[str]) -> None:
    """
    Validate that only one body type is specified per request.
    
    Args:
        data: Form data
        json_data: JSON data
        raw_body: Raw body content
        
    Raises:
        ValidationError: If multiple body types are specified
    """
    body_fields = [data, json_data, raw_body]
    specified_fields = [field for field in body_fields if field is not None]
    
    if len(specified_fields) > 1:
        field_names = []
        if data is not None:
            field_names.append('data (form data)')
        if json_data is not None:
            field_names.append('json_data (JSON data)')
        if raw_body is not None:
            field_names.append('raw_body (raw body content)')
        
        raise ValidationError(
            f"Multiple body types specified: {', '.join(field_names)}. "
            f"Only one body type allowed per request. Use either form data, "
            f"JSON data, or raw body content, but not multiple types."
        )


def _sanitize_url(url: str) -> str:
    """
    Redact sensitive parameters in URLs for safe logging.
    Handles both query parameters and path segments containing sensitive data.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL with sensitive data replaced
    """
    if not url:
        return url
    
    # Redact common sensitive keys in query params
    query_pattern = re.compile(r'(?i)(password|token|key|secret|api_key|access_token)=([^&]+)')
    url = query_pattern.sub(lambda m: f"{m.group(1)}=***", url)
    
    # Redact potential API keys and tokens in path segments
    # Pattern for UUIDs, JWT tokens, and long hex strings that might be sensitive
    path_patterns = [
        (r'/[a-f0-9]{32,}', '/***'),  # Long hex strings (API keys)
        (r'/[A-Za-z0-9_-]{20,}\.', r'/***\.'),  # JWT-like tokens ending with dot
        (r'/[A-Za-z0-9_-]{40,}', '/***'),  # Long base64-like strings
        (r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/***')  # UUIDs
    ]
    
    for pattern, replacement in path_patterns:
        url = re.sub(pattern, replacement, url, flags=re.IGNORECASE)
    
    return url


def _execute_request(session: requests.Session, config: RequestConfig, kwargs: Dict[str, Any]) -> requests.Response:
    """
    Execute HTTP request with error handling and logging.
    
    This function handles the actual request execution with proper
    error handling, timeout management, and response validation.
    
    Args:
        session: Authenticated requests.Session
        config: Request configuration
        kwargs: Request parameters
        
    Returns:
        requests.Response object
        
    Raises:
        RequestExecutionError: If request fails to execute
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
    """
    try:
        # Execute request
        response = session.request(**kwargs)
        # Check for HTTP errors
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timed out after {config.timeout} seconds")
        raise TimeoutError(
            message=f"Request timed out after {config.timeout} seconds",
            timeout_seconds=config.timeout
        ) from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Network connection error: {e}")
        raise NetworkError(
            message="Network error during request execution",
            original_exception=e
        ) from e
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response and hasattr(e.response, 'status_code') else None
        response_text = e.response.text[:MAX_RESPONSE_TEXT_LENGTH] if e.response and hasattr(e.response, 'text') and e.response.text else None
        logger.error(f"HTTP error {status_code}: {e}")
        raise ResponseError(
            message=f"HTTP error {status_code}",
            status_code=status_code,
            response_text=response_text
        ) from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        raise NetworkError(
            message="Network error during request execution",
            original_exception=e
        ) from e


def _log_request_info(config: RequestConfig, response: requests.Response, duration: float) -> None:
    """
    Log request and response information for debugging and monitoring, using centralized logging utilities.
    Args:
        config: Request configuration
        response: HTTP response
        duration: Request duration in seconds
    """
    # Log the request (redacted)
    log_request(
        method=config.method,
        url=config.url,
        headers=config.headers,
        params=config.params,
        body=config.data or config.json_data or config.raw_body,
        timeout=config.timeout
    )
    # Log the response (redacted, with response size)
    log_response(
        status_code=response.status_code,
        headers=dict(response.headers),
        body=response.text if hasattr(response, 'text') else None,
        response_time=duration
    )
    # Additionally log response size for test coverage
    if hasattr(response, 'content'):
        log_response(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=f"Response size: {len(response.content)} bytes",
            response_time=duration
        )


@monitor_performance("request_execution")
def send_request(
    session: requests.Session,
    request_config: Union[RequestConfig, Dict[str, Any]]
) -> requests.Response:
    """Send an HTTP request using the provided authenticated session.
    
    This function validates the request configuration, prepares the request
    parameters, executes the request, and logs the results. It's designed
    for use in exploit chaining workflows where authenticated sessions
    are used for multiple requests.
    
    Args:
        session: Authenticated requests.Session from auth module
        request_config: Request configuration (dict or RequestConfig object)
        
    Returns:
        requests.Response object with full response data
        
    Raises:
        RequestExecutionError: If request fails to execute
        ValidationError: If request configuration is invalid
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
        
    Examples:::

        # Send authenticated GET request
        session = authenticate_session(auth_config)
        response = send_request(session, {
            "url": "https://target.com/admin/panel",
            "method": "GET",
            "headers": {"User-Agent": "LogicPwn/1.0"}
        })
        
        # Send authenticated POST request with JSON
        response = send_request(session, {
            "url": "https://target.com/api/users",
            "method": "POST",
            "json_data": {"username": "test", "role": "admin"},
            "headers": {"Content-Type": "application/json"}
        })
    """
    try:
        # Validate configuration
        config = validate_config(request_config, RequestConfig)
        # Check cache first for GET requests
        if config.method.upper() == "GET":
            cached_response = response_cache.get_response(
                config.url, config.method, config.params, config.headers
            )
            if cached_response:
                logger.debug(f"Cache hit for {config.method} {config.url}")
                return cached_response
        # Prepare request parameters
        kwargs = prepare_request_kwargs(
            method=config.method,
            url=config.url,
            headers=config.headers,
            timeout=config.timeout,
            verify_ssl=config.verify_ssl,
            data=config.data,
            params=config.params,
            json_data=config.json_data,
            raw_body=config.raw_body
        )
        # Execute request with timing
        start_time = time.time()
        response = _execute_request(session, config, kwargs)
        duration = time.time() - start_time
        # Log request information
        _log_request_info(config, response, duration)
        # Cache successful GET responses
        if config.method.upper() == "GET" and response.status_code == 200:
            response_cache.set_response(
                config.url, config.method, response, 
                config.params, config.headers
            )
        return response
    except Exception as e:
        logger.error(f"Request execution failed: {e}")
        raise


@monitor_performance("advanced_request_execution")
def send_request_advanced(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    raw_body: Optional[str] = None,
    timeout: Optional[int] = None,
    verify_ssl: bool = True,
    session: Optional[requests.Session] = None,
    session_data: Optional[Dict[str, Any]] = None
) -> RequestResult:
    """Send an HTTP request with advanced features including middleware and analysis.
    
    This function provides advanced request execution with middleware integration,
    security analysis, and comprehensive response metadata. It's designed for
    security testing and exploit chaining workflows.
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
        headers: Request headers
        params: Query parameters
        data: Form data
        json_data: JSON data
        raw_body: Raw request body
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        session: Optional requests.Session (creates new if not provided)
        session_data: Optional session data for middleware
        
    Returns:
        RequestResult object with response data and security analysis
        
    Raises:
        RequestExecutionError: If request fails to execute
        ValidationError: If request configuration is invalid
        NetworkError: If network issues occur
        TimeoutError: If request times out
        ResponseError: If response indicates an error
        
    Examples:::

        # Send request with security analysis
        result = send_request_advanced(
            url="https://target.com/api/data",
            method="POST",
            json_data={"action": "test"},
            headers={"Authorization": "Bearer token"}
        )
        
        if result.has_vulnerabilities():
            print("Security issues detected!")
            print(f"Error messages: {result.security_analysis.error_messages}")
    """
    # Validate body types - only one should be specified
    _validate_body_types(data, json_data, raw_body)
    
    # Create RequestResult for tracking
    result = RequestResult(url=url, method=method)
    
    # Initialize metadata
    result.metadata = RequestMetadata(
        request_id=str(uuid.uuid4()),
        timestamp=time.time()
    )
    
    # Use provided session or create new one
    if session is None:
        session = requests.Session()
    
    # Create middleware context
    context = MiddlewareContext(
        request_id=str(uuid.uuid4()),
        url=url,
        method=method.upper(),
        headers=headers or {},
        params=params,
        body=data or json_data or raw_body,
        timeout=timeout or get_timeout(),
        session_data=session_data
    )
    
    # Process request through middleware
    try:
        context = middleware_manager.process_request(context)
    except Exception as e:
        log_error(e, {"url": url, "method": method})
        # Continue with request even if middleware fails
    
    # Log request
    log_request(
        method=context.method,
        url=context.url,
        headers=context.headers,
        params=context.params,
        body=context.body,
        timeout=context.timeout
    )
    
    # Prepare request configuration
    request_config = RequestConfig(
        url=context.url,
        method=context.method,
        headers=context.headers,
        params=context.params,
        data=context.body if isinstance(context.body, dict) else None,
        json_data=context.body if isinstance(context.body, dict) else None,
        raw_body=context.body if isinstance(context.body, str) else None,
        timeout=context.timeout,
        verify_ssl=verify_ssl
    )
    
    # Execute request with retry logic
    max_retries = get_max_retries()
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # Execute request
            start_time = time.time()
            response = send_request(session, request_config)
            duration = time.time() - start_time
            
            # Set response data in RequestResult
            result.status_code = response.status_code
            result.headers = dict(response.headers)
            result.body = response.text if response.text else None
            
            # Update metadata with response information
            if result.metadata:
                result.metadata.duration = duration
                result.metadata.status_code = response.status_code
                result.metadata.response_size = len(response.content) if response.content else 0
                result.metadata.headers_count = len(response.headers)
                result.metadata.cookies_count = len(response.cookies) if response.cookies else 0
            
            # Perform security analysis
            result.security_analysis = RequestResult._analyze_security(
                result.body, result.headers, result.status_code
            )
            
            # Log response
            log_response(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text if response.text else None,
                response_time=duration
            )
            
            # Process response through middleware
            try:
                result = middleware_manager.process_response(context, result)
            except RetryException:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.info(f"Retrying request (attempt {retry_count}/{max_retries})")
                    continue
                else:
                    raise RequestExecutionError("Max retries exceeded")
            except Exception as e:
                log_error(e, {"url": url, "method": method})
                # Continue even if middleware fails
            
            return result
            
        except (NetworkError, TimeoutError) as e:
            retry_count += 1
            if retry_count <= max_retries:
                logger.warning(f"Request failed, retrying ({retry_count}/{max_retries}): {e}")
                continue
            else:
                # Set error in result
                if result.metadata:
                    result.metadata.error = str(e)
                log_error(e, {"url": url, "method": method})
                raise
        except Exception as e:
            # Set error in result
            if result.metadata:
                result.metadata.error = str(e)
            log_error(e, {"url": url, "method": method})
            raise
    
    # This should never be reached, but just in case
    raise RequestExecutionError("Unexpected error in request execution") 