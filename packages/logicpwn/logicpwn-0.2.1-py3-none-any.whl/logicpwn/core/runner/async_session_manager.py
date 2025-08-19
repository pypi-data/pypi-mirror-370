"""
Async session management for LogicPwn with enhanced error handling and type safety.
"""
import asyncio
from typing import Dict, Optional, Any, List, Union
import aiohttp
from loguru import logger
from logicpwn.models.request_result import RequestResult
from logicpwn.exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)
from logicpwn.core.config.config_utils import get_timeout
from logicpwn.core.logging import log_info, log_error, log_warning

class AsyncSessionManager:
    """Async session manager for persistent authentication and exploit chaining."""
    def __init__(self, auth_config: Optional[Dict[str, Any]] = None, max_concurrent: int = 10, timeout: Optional[int] = None):
        """
        Initialize async session manager.
        Args:
            auth_config: Authentication configuration
            max_concurrent: Maximum concurrent requests
            timeout: Default timeout in seconds
        """
        import aiohttp
        self.auth_config = auth_config
        self.max_concurrent = max_concurrent
        self.timeout = timeout or get_timeout()
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookies: Dict[str, str] = {}
        self.headers: Dict[str, str] = {}
        self._session_closed = False

    @property
    def session_closed(self) -> bool:
        """Check if the session was properly closed."""
        return self._session_closed

    async def __aenter__(self):
        import aiohttp
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent
        )
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout_config
        )
        if self.auth_config:
            await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        if self.session:
            try:
                await self.session.close()
                # Keep a reference to check if it was closed, but mark it as closed
                self._session_closed = True
            except Exception as e:
                log_error(e, {"component": "AsyncSessionManager", "action": "session_cleanup"})
                self._session_closed = False
            finally:
                self.session = None
        else:
            self._session_closed = False

    async def authenticate(self) -> bool:
        """
        Authenticate using the provided configuration.
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            ValidationError: If no authentication configuration provided
        """
        if not self.auth_config:
            raise ValidationError("No authentication configuration provided")
        
        try:
            auth_url = self.auth_config['url']
            method = self.auth_config.get('method', 'POST')
            credentials = self.auth_config.get('credentials', {})
            headers = self.auth_config.get('headers', {})
            
            request_data = credentials.copy()
            
            async with self.session.request(
                method=method,
                url=auth_url,
                data=request_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    # Update cookies and headers from successful auth
                    if hasattr(response.cookies, 'items'):
                        # Handle dictionary-like cookie objects (for mocks)
                        for key, value in response.cookies.items():
                            self.cookies[key] = value
                    else:
                        # Handle real aiohttp cookie objects
                        for cookie in response.cookies:
                            try:
                                if hasattr(cookie, 'key') and hasattr(cookie, 'value'):
                                    # aiohttp cookie object
                                    self.cookies[cookie.key] = cookie.value
                                elif hasattr(cookie, 'name') and hasattr(cookie, 'value'):
                                    # requests-style cookie
                                    self.cookies[cookie.name] = cookie.value
                                else:
                                    # Handle as string (for mocks)
                                    cookie_str = str(cookie)
                                    if '=' in cookie_str:
                                        key, value = cookie_str.split('=', 1)
                                        self.cookies[key] = value
                            except (AttributeError, ValueError) as e:
                                log_warning(f"Failed to parse cookie: {cookie}, error: {e}")
                            
                    self.headers.update(headers)
                    log_info("Authentication successful", {'url': auth_url, 'status': response.status})
                    return True
                else:
                    log_error(NetworkError(f"Authentication failed: {response.status}"), {
                        'url': auth_url, 'status': response.status
                    })
                    return False
                    
        except aiohttp.ClientError as e:
            log_error(NetworkError(f"Authentication network error: {str(e)}"), {
                'url': self.auth_config.get('url', 'unknown')
            })
            return False
        except Exception as e:
            log_error(RequestExecutionError(f"Authentication error: {str(e)}"), {
                'url': self.auth_config.get('url', 'unknown')
            })
            return False

    async def get(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request('POST', url, **kwargs)

    async def put(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request('PUT', url, **kwargs)

    async def delete(self, url: str, **kwargs) -> RequestResult:
        return await self._send_authenticated_request('DELETE', url, **kwargs)

    async def _send_authenticated_request(self, method: str, url: str, **kwargs) -> RequestResult:
        headers = kwargs.get('headers', {}).copy()
        headers.update(self.headers)
        cookies = kwargs.get('cookies', {}).copy()
        cookies.update(self.cookies)
        import aiohttp
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': headers,
            'cookies': cookies,
            **{k: v for k, v in kwargs.items() if k not in ['headers', 'cookies']}
        }
        async with self.session.request(**request_kwargs) as response:
            self.cookies.update(response.cookies)
            content = await response.read()
            text = content.decode('utf-8', errors='ignore')
            try:
                if 'application/json' in response.headers.get('content-type', ''):
                    body = await response.json()
                else:
                    body = text
            except Exception:
                body = text
            return RequestResult.from_response(
                url=url,
                method=method,
                response=type('MockResponse', (), {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'text': text,
                    'content': content,
                    'json': lambda: body if isinstance(body, dict) else None
                })(),
                duration=0.0
            )

    async def execute_exploit_chain(self, exploit_configs: List[Dict[str, Any]]) -> List[RequestResult]:
        results = []
        for config in exploit_configs:
            method = config.get('method', 'GET')
            url = config['url']
            data = config.get('data')
            headers = config.get('headers', {})
            if method.upper() == 'GET':
                result = await self.get(url, headers=headers)
            elif method.upper() == 'POST':
                result = await self.post(url, data=data, headers=headers)
            elif method.upper() == 'PUT':
                result = await self.put(url, data=data, headers=headers)
            elif method.upper() == 'DELETE':
                result = await self.delete(url, headers=headers)
            else:
                raise ValidationError(f"Unsupported HTTP method: {method}")
            results.append(result)
            if result.status_code >= 400:
                log_warning(f"Exploit step failed: {url}", {
                    'status_code': result.status_code,
                    'method': method
                })
        return results 