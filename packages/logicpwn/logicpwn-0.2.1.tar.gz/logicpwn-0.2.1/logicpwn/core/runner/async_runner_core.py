"""
Core async request runner logic for LogicPwn.
"""
import asyncio
import aiohttp
from typing import Dict, Optional, Any, Union, List
from dataclasses import dataclass
from loguru import logger
from logicpwn.models.request_config import RequestConfig
from logicpwn.models.request_result import RequestResult
from logicpwn.exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from logicpwn.core.config.config_utils import get_timeout
from logicpwn.core.logging import log_request, log_response, log_error, log_info, log_warning


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

@dataclass
class AsyncRequestContext:
    """Context for async request execution."""
    request_id: str
    url: str
    method: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    timeout: Optional[int] = None
    session_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AsyncRequestRunner:
    """High-performance async request runner for concurrent security testing."""
    def __init__(self, max_concurrent: int = 10, rate_limit: Optional[float] = None, timeout: Optional[int] = None, verify_ssl: bool = True):
        """
        Initialize async request runner.
        Args:
            max_concurrent: Maximum concurrent requests
            rate_limit: Requests per second limit
            timeout: Default timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.timeout = timeout or get_timeout()
        self.verify_ssl = verify_ssl
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent,
            verify_ssl=self.verify_ssl
        )
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def send_request(self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, raw_body: Optional[str] = None, timeout: Optional[int] = None) -> RequestResult:
        """
        Send a single async HTTP request.
        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Form data
            json_data: JSON body
            raw_body: Raw body content
            timeout: Request timeout
        Returns:
            RequestResult with response analysis
        """
        # Validate body types - only one should be specified
        _validate_body_types(data, json_data, raw_body)
        async with self.semaphore:
            return await self._execute_request(
                url=url,
                method=method,
                headers=headers or {},
                params=params or {},
                data=data,
                json_data=json_data,
                raw_body=raw_body,
                timeout=timeout or self.timeout
            )

    async def send_requests_batch(self, request_configs: List[Union[Dict[str, Any], RequestConfig]], max_concurrent: Optional[int] = None) -> List[RequestResult]:
        """
        Send multiple requests concurrently.
        Args:
            request_configs: List of request configurations
            max_concurrent: Override max concurrent requests
        Returns:
            List of RequestResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent or self.max_concurrent)
        async def execute_with_semaphore(config):
            async with semaphore:
                if isinstance(config, dict):
                    return await self.send_request(**config)
                else:
                    return await self.send_request(
                        url=config.url,
                        method=config.method,
                        headers=config.headers,
                        params=config.params,
                        data=config.data,
                        json_data=config.json_data,
                        raw_body=config.raw_body,
                        timeout=config.timeout
                    )
        tasks = [execute_with_semaphore(config) for config in request_configs]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_request(self, url: str, method: str, headers: Dict[str, str], params: Dict[str, Any], data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, raw_body: Optional[str] = None, timeout: Optional[int] = None) -> RequestResult:
        """Execute a single async request with comprehensive error handling."""
        import uuid
        import time
        request_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            # Prepare request data
            request_kwargs = {
                'headers': headers,
                'params': params,
                'timeout': aiohttp.ClientTimeout(total=timeout or self.timeout)
            }
            if data:
                request_kwargs['data'] = data
            elif json_data:
                request_kwargs['json'] = json_data
            elif raw_body:
                request_kwargs['data'] = raw_body
            # Log request
            log_request(method, url, headers, data or json_data or raw_body)
            # Add specific logging for HEAD requests
            if method.upper() == "HEAD":
                log_info(f"HEAD request to {url} - will return headers only, no body expected")
            # Execute request
            async with self.session.request(method, url, **request_kwargs) as response:
                duration = time.time() - start_time
                
                # Read response content safely
                try:
                    content = await response.read()
                    text = content.decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    # Fallback for problematic encodings
                    text = content.decode('latin-1', errors='ignore')
                except Exception as e:
                    logger.warning(f"Failed to read response content: {e}")
                    content = b""
                    text = ""
                
                # Parse response body
                body = text
                try:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/json' in content_type:
                        body = await response.json()
                except (aiohttp.ContentTypeError, ValueError, TypeError) as e:
                    # JSON parsing failed, keep as text
                    logger.debug(f"JSON parsing failed, keeping as text: {e}")
                    body = text
                except Exception as e:
                    logger.warning(f"Unexpected error parsing response body: {e}")
                    body = text
                # Create RequestResult
                result = RequestResult.from_response(
                    url=url,
                    method=method,
                    response=type('MockResponse', (), {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'text': text,
                        'content': content,
                        'json': lambda: body if isinstance(body, dict) else None
                    })(),
                    duration=duration
                )
                # Log response
                log_response(response.status, dict(response.headers), body, duration)
                # Add specific logging for HEAD response
                if method.upper() == "HEAD":
                    log_info(f"HEAD response headers: {dict(response.headers)}")
                return result
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_error(TimeoutError(f"Request timeout after {timeout or self.timeout}s"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=TimeoutError(f"Request timeout after {timeout or self.timeout}s"),
                duration=duration
            )
        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            log_error(NetworkError(f"Network error: {str(e)}"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=NetworkError(f"Network error: {str(e)}"),
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            log_error(RequestExecutionError(f"Request execution error: {str(e)}"), {
                'url': url, 'method': method, 'duration': duration
            })
            return RequestResult.from_exception(
                url=url,
                method=method,
                exception=RequestExecutionError(f"Request execution error: {str(e)}"),
                duration=duration
            ) 