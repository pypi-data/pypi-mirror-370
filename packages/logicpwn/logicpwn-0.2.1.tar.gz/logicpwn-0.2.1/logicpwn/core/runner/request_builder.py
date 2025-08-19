"""
Request builder utilities for LogicPwn runner module.
Provides convenient methods for building common request types.
"""
from typing import Dict, Optional, Any, List, Union
from logicpwn.models.request_config import RequestConfig
from logicpwn.exceptions import ValidationError


class RequestBuilder:
    """Builder class for constructing RequestConfig objects with fluent API."""
    
    def __init__(self, url: str):
        """
        Initialize request builder with target URL.
        
        Args:
            url: Target URL for the request
        """
        self.config = {
            'url': url,
            'method': 'GET',
            'headers': {},
            'params': {},
            'data': None,
            'json_data': None,
            'raw_body': None,
            'timeout': 30,
            'verify_ssl': True
        }
    
    def method(self, method: str) -> 'RequestBuilder':
        """Set HTTP method."""
        self.config['method'] = method.upper()
        return self
    
    def get(self) -> 'RequestBuilder':
        """Set method to GET."""
        return self.method('GET')
    
    def post(self) -> 'RequestBuilder':
        """Set method to POST."""
        return self.method('POST')
    
    def put(self) -> 'RequestBuilder':
        """Set method to PUT."""
        return self.method('PUT')
    
    def delete(self) -> 'RequestBuilder':
        """Set method to DELETE."""
        return self.method('DELETE')
    
    def patch(self) -> 'RequestBuilder':
        """Set method to PATCH."""
        return self.method('PATCH')
    
    def head(self) -> 'RequestBuilder':
        """Set method to HEAD."""
        return self.method('HEAD')
    
    def header(self, key: str, value: str) -> 'RequestBuilder':
        """Add a single header."""
        self.config['headers'][key] = value
        return self
    
    def headers(self, headers: Dict[str, str]) -> 'RequestBuilder':
        """Add multiple headers."""
        self.config['headers'].update(headers)
        return self
    
    def auth_header(self, token: str, auth_type: str = 'Bearer') -> 'RequestBuilder':
        """Add authorization header."""
        self.config['headers']['Authorization'] = f'{auth_type} {token}'
        return self
    
    def content_type(self, content_type: str) -> 'RequestBuilder':
        """Set Content-Type header."""
        return self.header('Content-Type', content_type)
    
    def json_content(self) -> 'RequestBuilder':
        """Set Content-Type to application/json."""
        return self.content_type('application/json')
    
    def form_content(self) -> 'RequestBuilder':
        """Set Content-Type to application/x-www-form-urlencoded."""
        return self.content_type('application/x-www-form-urlencoded')
    
    def param(self, key: str, value: Any) -> 'RequestBuilder':
        """Add a single query parameter."""
        self.config['params'][key] = value
        return self
    
    def params(self, params: Dict[str, Any]) -> 'RequestBuilder':
        """Add multiple query parameters."""
        self.config['params'].update(params)
        return self
    
    def form_data(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set form data body."""
        if self.config['json_data'] is not None or self.config['raw_body'] is not None:
            raise ValidationError("Cannot set form data when JSON or raw body is already set")
        self.config['data'] = data
        return self
    
    def json_data(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set JSON data body."""
        if self.config['data'] is not None or self.config['raw_body'] is not None:
            raise ValidationError("Cannot set JSON data when form data or raw body is already set")
        self.config['json_data'] = data
        return self.json_content()
    
    def raw_body(self, body: str) -> 'RequestBuilder':
        """Set raw body content."""
        if self.config['data'] is not None or self.config['json_data'] is not None:
            raise ValidationError("Cannot set raw body when form data or JSON data is already set")
        self.config['raw_body'] = body
        return self
    
    def timeout(self, seconds: int) -> 'RequestBuilder':
        """Set request timeout."""
        self.config['timeout'] = seconds
        return self
    
    def verify_ssl(self, verify: bool = True) -> 'RequestBuilder':
        """Set SSL verification."""
        self.config['verify_ssl'] = verify
        return self
    
    def user_agent(self, user_agent: str) -> 'RequestBuilder':
        """Set User-Agent header."""
        return self.header('User-Agent', user_agent)
    
    def build(self) -> RequestConfig:
        """Build the final RequestConfig object."""
        return RequestConfig(**self.config)


class CommonRequests:
    """Factory class for creating common request types."""
    
    @staticmethod
    def get(url: str, **kwargs) -> RequestConfig:
        """Create a simple GET request."""
        return RequestBuilder(url).get().headers(kwargs.get('headers', {})).params(kwargs.get('params', {})).build()
    
    @staticmethod
    def post_json(url: str, data: Dict[str, Any], **kwargs) -> RequestConfig:
        """Create a POST request with JSON data."""
        builder = RequestBuilder(url).post().json_data(data)
        if 'headers' in kwargs:
            builder.headers(kwargs['headers'])
        return builder.build()
    
    @staticmethod
    def post_form(url: str, data: Dict[str, Any], **kwargs) -> RequestConfig:
        """Create a POST request with form data."""
        builder = RequestBuilder(url).post().form_data(data).form_content()
        if 'headers' in kwargs:
            builder.headers(kwargs['headers'])
        return builder.build()
    
    @staticmethod
    def authenticated_get(url: str, token: str, auth_type: str = 'Bearer', **kwargs) -> RequestConfig:
        """Create an authenticated GET request."""
        return (RequestBuilder(url)
                .get()
                .auth_header(token, auth_type)
                .headers(kwargs.get('headers', {}))
                .params(kwargs.get('params', {}))
                .build())
    
    @staticmethod
    def authenticated_post_json(url: str, data: Dict[str, Any], token: str, auth_type: str = 'Bearer', **kwargs) -> RequestConfig:
        """Create an authenticated POST request with JSON data."""
        return (RequestBuilder(url)
                .post()
                .json_data(data)
                .auth_header(token, auth_type)
                .headers(kwargs.get('headers', {}))
                .build())
    
    @staticmethod
    def api_request(url: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, 
                   api_key: Optional[str] = None, **kwargs) -> RequestConfig:
        """Create a generic API request."""
        builder = RequestBuilder(url).method(method)
        
        if api_key:
            builder.header('X-API-Key', api_key)
        
        if data and method.upper() in ['POST', 'PUT', 'PATCH']:
            builder.json_data(data)
        elif 'params' in kwargs:
            builder.params(kwargs['params'])
        
        if 'headers' in kwargs:
            builder.headers(kwargs['headers'])
            
        return builder.build()


# Convenience functions for quick request building
def build_request(url: str) -> RequestBuilder:
    """Start building a request with the given URL."""
    return RequestBuilder(url)


def quick_get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> RequestConfig:
    """Quickly create a GET request."""
    return CommonRequests.get(url, headers=headers or {}, params=params or {})


def quick_post_json(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> RequestConfig:
    """Quickly create a POST request with JSON data."""
    return CommonRequests.post_json(url, data, headers=headers or {})


def quick_post_form(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> RequestConfig:
    """Quickly create a POST request with form data."""
    return CommonRequests.post_form(url, data, headers=headers or {})
