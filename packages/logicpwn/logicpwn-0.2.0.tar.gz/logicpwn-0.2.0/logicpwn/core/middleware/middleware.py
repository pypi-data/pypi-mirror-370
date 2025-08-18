"""
Middleware system for LogicPwn.

This module provides a flexible middleware system that allows for
request/response processing hooks. It enables extensibility and custom
processing logic for authentication, logging, retry logic, and other
business logic exploitation workflows.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from logicpwn.core.logging import log_info, log_debug, log_error
from logicpwn.core.config.config_utils import get_timeout, get_max_retries


@dataclass
class MiddlewareContext:
    """Context passed to middleware hooks."""
    request_id: str
    url: str
    method: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    timeout: Optional[int] = None
    session_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseMiddleware(ABC):
    """Base class for all middleware."""
    
    def __init__(self, name: str):
                                            self.name = name
                                            self.enabled = True
    
    @abstractmethod
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Process request before it's sent."""
                                            pass
    
    @abstractmethod
    def process_response(self, context: MiddlewareContext, 
                                                           response: Any) -> Any:
                                            """Process response after it's received."""
                                            pass
    
    def enable(self):
                                            """Enable the middleware."""
                                            self.enabled = True
                                            log_debug(f"Middleware '{self.name}' enabled")
    
    def disable(self):
                                            """Disable the middleware."""
                                            self.enabled = False
                                            log_debug(f"Middleware '{self.name}' disabled")


class AuthenticationMiddleware(BaseMiddleware):
    """Middleware for handling authentication."""
    
    def __init__(self, auth_manager=None):
                                            super().__init__("Authentication")
                                            self.auth_manager = auth_manager
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Add authentication headers to request."""
                                            if not self.enabled or not self.auth_manager:
                                                return context
                                            
                                            try:
                                                # Get session data for the URL
                                                session_data = self.auth_manager.get_session_data(context.url)
                                                if session_data and session_data.get('headers'):
                                                    context.headers.update(session_data['headers'])
                                                    log_debug(f"Added auth headers for {context.url}")
                                            except Exception as e:
                                                log_error(e, {"middleware": self.name, "url": context.url})
                                            
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Process authentication-related response data."""
                                            if not self.enabled or not self.auth_manager:
                                                return response
                                            
                                            try:
                                                # Extract and store session data from response
                                                if hasattr(response, 'get_cookies'):
                                                    cookies = response.get_cookies()
                                                    if cookies:
                                                        self.auth_manager.update_session_data(
                                                            context.url, {'cookies': cookies}
                                                        )
                                                        log_debug(f"Updated session cookies for {context.url}")
                                            except Exception as e:
                                                log_error(e, {"middleware": self.name, "url": context.url})
                                            
                                            return response


class LoggingMiddleware(BaseMiddleware):
    """Middleware for request/response logging."""
    
    def __init__(self):
                                            super().__init__("Logging")
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Log request details."""
                                            if not self.enabled:
                                                return context
                                            
                                            log_info("Request", {
                                                "method": context.method,
                                                "url": context.url,
                                                "headers": context.headers,
                                                "params": context.params,
                                                "body": context.body,
                                                "timeout": context.timeout
                                            })
                                            
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Log response details."""
                                            if not self.enabled:
                                                return response
                                            
                                            if hasattr(response, 'status_code') and hasattr(response, 'headers'):
                                                log_info("Response", {
                                                    "status_code": response.status_code,
                                                    "headers": response.headers,
                                                    "body": getattr(response, 'body', None),
                                                    "url": context.url
                                                })
                                            
                                            return response


class RetryMiddleware(BaseMiddleware):
    """Middleware for handling retries and backoff."""
    
    def __init__(self, max_retries: Optional[int] = None, 
                                                     backoff_factor: float = 2.0):
                                            super().__init__("Retry")
                                            self.max_retries = max_retries or get_max_retries()
                                            self.backoff_factor = backoff_factor
                                            self.retry_count = 0
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Add retry information to context."""
                                            if not self.enabled:
                                                return context
                                            
                                            context.metadata = context.metadata or {}
                                            context.metadata['retry_count'] = self.retry_count
                                            context.metadata['max_retries'] = self.max_retries
                                            
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Handle retry logic based on response."""
                                            if not self.enabled:
                                                return response
                                            
                                                # Check if retry is needed
                                            if self._should_retry(response):
                                                self.retry_count += 1
                                                if self.retry_count <= self.max_retries:
                                                    log_info(f"Retrying request (attempt {self.retry_count}/{self.max_retries})", {
                                                        "url": context.url,
                                                        "status_code": getattr(response, 'status_code', None)
                                                    })
                                                    # This would trigger a retry in the main request loop
                                                    raise RetryException(f"Retry needed for {context.url}")
                                            
                                                # Reset retry count on success
                                            self.retry_count = 0
                                            return response
    
    def _should_retry(self, response: Any) -> bool:
                                            """Determine if request should be retried."""
                                            if not response:
                                                return True
                                            
                                            status_code = getattr(response, 'status_code', None)
                                            if not status_code:
                                                return True
                                            
                                                # Retry on 5xx errors and some 4xx errors
                                            retry_status_codes = {408, 429, 500, 502, 503, 504}
                                            return status_code in retry_status_codes


class SecurityMiddleware(BaseMiddleware):
    """Middleware for security analysis and validation."""
    
    def __init__(self):
                                            super().__init__("Security")
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Validate request for security issues."""
                                            if not self.enabled:
                                                return context
                                            
                                                # Check for potentially dangerous patterns
                                            self._validate_request_security(context)
                                            
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Analyze response for security issues."""
                                            if not self.enabled:
                                                return response
                                            
                                                # Security analysis is handled by RequestResult
                                            if hasattr(response, 'has_vulnerabilities') and response.has_vulnerabilities():
                                                log_info("Security issues detected", {
                                                    "url": context.url,
                                                    "vulnerabilities": response.security_analysis.to_dict()
                                                })
                                            
                                            return response
    
    def _validate_request_security(self, context: MiddlewareContext):
                                            """Validate request for security issues."""
                                                # Check for potentially dangerous headers
                                            dangerous_headers = ['x-forwarded-for', 'x-real-ip', 'x-forwarded-host']
                                            for header in dangerous_headers:
                                                if header in context.headers:
                                                    log_debug(f"Potentially dangerous header detected: {header}")
                                            
                                                # Check for potentially dangerous parameters
                                            if context.params:
                                                dangerous_params = ['eval', 'exec', 'system', 'shell']
                                                for param in context.params:
                                                    if any(dangerous in param.lower() for dangerous in dangerous_params):
                                                        log_debug(f"Potentially dangerous parameter detected: {param}")


class SessionMiddleware(BaseMiddleware):
    """Middleware for session management."""
    
    def __init__(self):
                                            super().__init__("Session")
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Add session data to request."""
                                            if not self.enabled:
                                                return context
                                            
                                                # Add session cookies if available
                                            if context.session_data and context.session_data.get('cookies'):
                                                cookie_header = '; '.join([
                                                    f"{k}={v}" for k, v in context.session_data['cookies'].items()
                                                ])
                                                if cookie_header:
                                                    context.headers['Cookie'] = cookie_header
                                            
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Extract session data from response."""
                                            if not self.enabled:
                                                return response
                                            
                                                # Session data extraction is handled by RequestResult
                                            return response


class MiddlewareManager:
    """Manages middleware execution order and lifecycle."""
    
    def __init__(self):
                                            self.middleware: List[BaseMiddleware] = []
                                            self.enabled_middleware: List[BaseMiddleware] = []
    
    def add_middleware(self, middleware: BaseMiddleware):
                                            """Add middleware to the chain."""
                                            self.middleware.append(middleware)
                                            if middleware.enabled:
                                                self.enabled_middleware.append(middleware)
                                            log_info(f"Added middleware: {middleware.name}")
    
    def remove_middleware(self, name: str):
                                            """Remove middleware by name."""
                                            self.middleware = [m for m in self.middleware if m.name != name]
                                            self.enabled_middleware = [m for m in self.enabled_middleware if m.name != name]
                                            log_info(f"Removed middleware: {name}")
    
    def enable_middleware(self, name: str):
                                            """Enable middleware by name."""
                                            for middleware in self.middleware:
                                                if middleware.name == name:
                                                    middleware.enable()
                                                    if middleware not in self.enabled_middleware:
                                                        self.enabled_middleware.append(middleware)
                                                    break
    
    def disable_middleware(self, name: str):
                                            """Disable middleware by name."""
                                            for middleware in self.middleware:
                                                if middleware.name == name:
                                                    middleware.disable()
                                                    if middleware in self.enabled_middleware:
                                                        self.enabled_middleware.remove(middleware)
                                                    break
    
    def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
                                            """Process request through all enabled middleware."""
                                            for middleware in self.enabled_middleware:
                                                try:
                                                    context = middleware.process_request(context)
                                                except Exception as e:
                                                    log_error(e, {
                                                        "middleware": middleware.name,
                                                        "url": context.url,
                                                        "method": context.method
                                                    })
                                                    # Continue with other middleware
                                            return context
    
    def process_response(self, context: MiddlewareContext, response: Any) -> Any:
                                            """Process response through all enabled middleware (in reverse order)."""
                                            for middleware in reversed(self.enabled_middleware):
                                                try:
                                                    response = middleware.process_response(context, response)
                                                except Exception as e:
                                                    log_error(e, {
                                                        "middleware": middleware.name,
                                                        "url": context.url,
                                                        "method": context.method
                                                    })
                                                    # Continue with other middleware
                                            return response
    
    def get_middleware(self, name: str) -> Optional[BaseMiddleware]:
                                            """Get middleware by name."""
                                            for middleware in self.middleware:
                                                if middleware.name == name:
                                                    return middleware
                                            return None
    
    def list_middleware(self) -> List[Dict[str, Any]]:
                                            """List all middleware with their status."""
                                            return [
                                                {
                                                    "name": m.name,
                                                    "enabled": m.enabled,
                                                    "type": type(m).__name__
                                                }
                                                for m in self.middleware
                                            ]


class RetryException(Exception):
    """Exception raised when a request should be retried."""
    def __init__(self, message, original_exception=None, retries=None):
                                            super().__init__(message)
                                            self.original_exception = original_exception
                                            self.retries = retries
    def __str__(self):
                                            return str(self.args[0]) if self.args else ""
    @property
    def retry_count(self):
                                            return self.retries


# Global middleware manager instance
middleware_manager = MiddlewareManager()


# Convenience functions for middleware management
def add_middleware(middleware: BaseMiddleware):
    """Add middleware to the global manager."""
    middleware_manager.add_middleware(middleware)


def remove_middleware(name: str):
    """Remove middleware from the global manager."""
    middleware_manager.remove_middleware(name)


def enable_middleware(name: str):
    """Enable middleware in the global manager."""
    middleware_manager.enable_middleware(name)


def disable_middleware(name: str):
    """Disable middleware in the global manager."""
    middleware_manager.disable_middleware(name)


def get_middleware(name: str) -> Optional[BaseMiddleware]:
    """Get middleware from the global manager."""
    return middleware_manager.get_middleware(name)


def list_middleware() -> List[Dict[str, Any]]:
    """List all middleware in the global manager."""
    return middleware_manager.list_middleware() 