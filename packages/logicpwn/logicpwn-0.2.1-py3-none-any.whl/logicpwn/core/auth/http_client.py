"""
Native HTTP client for LogicPwn authentication with advanced session management and CSRF handling.
This module provides the HTTP transport layer for the auth system with deep integration.
"""
import asyncio
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import aiohttp
import requests
from loguru import logger

from logicpwn.models.request_result import RequestResult
from logicpwn.exceptions import (
    NetworkError, 
    AuthenticationError, 
    ValidationError,
    TimeoutError as LogicPwnTimeoutError
)
from logicpwn.core.cache import session_cache
from logicpwn.core.middleware.middleware import middleware_manager, MiddlewareContext
from .auth_models import AuthConfig, SessionState, CSRFConfig


class LogicPwnHTTPClient:
    """
    Native HTTP client for LogicPwn authentication with advanced session management.
    
    Features:
    - Dynamic CSRF token handling
    - Session state persistence 
    - Automatic authentication retry
    - Middleware integration
    - Caching with intelligent cache keys
    - Application-specific session validation
    """
    
    def __init__(self, base_url: str = "", verify_ssl: bool = True, timeout: int = 30):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session_state = SessionState(base_url=base_url)
        self._requests_session: Optional[requests.Session] = None
        self._aiohttp_session: Optional[aiohttp.ClientSession] = None
        
    @property
    def requests_session(self) -> requests.Session:
        """Get or create requests session for synchronous operations"""
        if self._requests_session is None:
            self._requests_session = requests.Session()
            self._requests_session.verify = self.verify_ssl
            # Apply session state
            self._requests_session.cookies.update(self.session_state.cookies)
            self._requests_session.headers.update(self.session_state.headers)
        return self._requests_session
    
    async def get_aiohttp_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session for async operations"""
        if self._aiohttp_session is None:
            connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            # Convert cookies to aiohttp format
            jar = aiohttp.CookieJar()
            for name, value in self.session_state.cookies.items():
                jar.update_cookies({name: value})
            
            self._aiohttp_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.session_state.headers,
                cookie_jar=jar
            )
        return self._aiohttp_session
    
    def extract_csrf_tokens(self, html_content: str, csrf_config: CSRFConfig) -> Dict[str, str]:
        """Extract CSRF tokens from HTML content using configured patterns"""
        tokens = {}
        
        if not csrf_config or not csrf_config.enabled:
            return tokens
            
        for pattern in csrf_config.token_patterns:
            matches = pattern.findall(html_content)
            for match in matches:
                if len(match) == 2:
                    token_name, token_value = match
                    tokens[token_name] = token_value
                    logger.debug(f"Extracted CSRF token: {token_name}={token_value[:10]}...")
        
        return tokens
    
    def generate_session_cache_key(self, auth_config: AuthConfig) -> str:
        """Generate cache key excluding dynamic tokens"""
        stable_creds = {k: v for k, v in auth_config.credentials.items() 
                       if not self._is_dynamic_token(k)}
        
        # Include URL, method, and stable credentials only
        key_data = {
            'url': auth_config.url,
            'method': auth_config.method,
            'credentials': stable_creds,
            'base_url': self.base_url
        }
        
        return f"logicpwn_session_{hash(str(sorted(key_data.items())))}"
    
    def _is_dynamic_token(self, field_name: str) -> bool:
        """Check if a field name represents a dynamic token"""
        dynamic_patterns = [
            'token', 'csrf', '_token', 'authenticity_token', 
            'user_token', 'form_token', 'security_token',
            'nonce', 'state', 'challenge'
        ]
        field_lower = field_name.lower()
        return any(pattern in field_lower for pattern in dynamic_patterns)
    
    def authenticate(self, auth_config: AuthConfig) -> bool:
        """
        Authenticate using the native HTTP client with advanced features
        """
        cache_key = self.generate_session_cache_key(auth_config)
        
        # Check for cached session first
        if self._try_use_cached_session(cache_key, auth_config):
            return True
            
        # Perform fresh authentication
        return self._perform_fresh_authentication(auth_config, cache_key)
    
    def _try_use_cached_session(self, cache_key: str, auth_config: AuthConfig) -> bool:
        """Try to use a cached session if available and valid"""
        cached_state = session_cache.get_session(cache_key)
        if not cached_state:
            return False
            
        # Restore session state
        self.session_state = cached_state
        self._requests_session = None  # Force recreation with new state
        
        # Validate session is still active
        if auth_config.session_validation_url:
            if self._validate_session(auth_config.session_validation_url):
                logger.info(f"Using cached session for {auth_config.url}")
                return True
            else:
                logger.debug("Cached session invalid, performing fresh auth")
                session_cache.invalidate_session(cache_key)
        else:
            # No validation URL, assume cached session is good
            logger.info(f"Using cached session for {auth_config.url} (no validation)")
            return True
            
        return False
    
    def _validate_session(self, validation_url: str) -> bool:
        """Validate that the current session is still authenticated"""
        try:
            response = self.requests_session.get(validation_url, timeout=10, allow_redirects=False)
            
            # Check for redirects to login
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    return False
            
            # Check response content for login indicators
            if response.status_code == 200:
                content = response.text.lower()
                login_indicators = ['login', 'sign in', 'authenticate', 'username', 'password']
                return not any(indicator in content for indicator in login_indicators)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"Session validation failed: {e}")
            return False
    
    def _perform_fresh_authentication(self, auth_config: AuthConfig, cache_key: str) -> bool:
        """Perform fresh authentication with CSRF handling"""
        try:
            # Step 1: Pre-authentication callback
            if auth_config.pre_auth_callback:
                auth_config.pre_auth_callback(self, auth_config)
            
            # Step 2: Get authentication page and extract CSRF tokens
            csrf_tokens = {}
            if auth_config.csrf_config and auth_config.csrf_config.enabled:
                csrf_tokens = self._fetch_csrf_tokens(auth_config)
                
            # Step 3: Prepare authentication request
            auth_data = auth_config.credentials.copy()
            
            # Auto-include CSRF tokens if enabled
            if auth_config.csrf_config and auth_config.csrf_config.auto_include:
                auth_data.update(csrf_tokens)
            
            # Step 4: Perform authentication request
            auth_response = self.requests_session.request(
                method=auth_config.method,
                url=auth_config.url,
                data=auth_data if auth_config.method.upper() == 'POST' else None,
                params=auth_data if auth_config.method.upper() == 'GET' else None,
                headers=auth_config.headers,
                timeout=auth_config.timeout,
                allow_redirects=True
            )
            
            auth_response.raise_for_status()
            
            # Step 5: Validate authentication success
            if not self._check_auth_success(auth_response, auth_config):
                if (auth_config.csrf_config and 
                    auth_config.csrf_config.refresh_on_failure and csrf_tokens):
                    # Retry with fresh CSRF tokens
                    logger.info("Authentication failed, retrying with fresh CSRF tokens")
                    return self._retry_auth_with_fresh_tokens(auth_config, cache_key)
                else:
                    raise AuthenticationError("Authentication failed - success indicators not found")
            
            # Step 6: Update session state
            self._update_session_state(auth_response, csrf_tokens)
            
            # Step 7: Post-authentication callback
            if auth_config.post_auth_callback:
                auth_config.post_auth_callback(self, auth_config, auth_response)
            
            # Step 8: Cache the session state
            session_cache.set_session(cache_key, self.session_state)
            
            logger.info(f"Authentication successful to {auth_config.url}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _fetch_csrf_tokens(self, auth_config: AuthConfig) -> Dict[str, str]:
        """Fetch CSRF tokens from the authentication page"""
        try:
            # Get the page that contains CSRF tokens (usually the login page)
            csrf_response = self.requests_session.get(
                auth_config.url, 
                timeout=auth_config.timeout
            )
            csrf_response.raise_for_status()
            
            tokens = self.extract_csrf_tokens(csrf_response.text, auth_config.csrf_config)
            self.session_state.csrf_tokens.update(tokens)
            
            logger.debug(f"Fetched {len(tokens)} CSRF tokens")
            return tokens
            
        except Exception as e:
            logger.warning(f"Failed to fetch CSRF tokens: {e}")
            return {}
    
    def _check_auth_success(self, response: requests.Response, auth_config: AuthConfig) -> bool:
        """Check if authentication was successful based on indicators"""
        content = response.text
        
        # Check failure indicators first
        for failure_indicator in auth_config.failure_indicators:
            if failure_indicator.lower() in content.lower():
                logger.debug(f"Found failure indicator: {failure_indicator}")
                return False
        
        # Check success indicators
        if auth_config.success_indicators:
            for success_indicator in auth_config.success_indicators:
                if success_indicator.lower() in content.lower():
                    logger.debug(f"Found success indicator: {success_indicator}")
                    return True
            return False  # No success indicators found
        else:
            # No specific indicators, assume success if no failures
            return True
    
    def _retry_auth_with_fresh_tokens(self, auth_config: AuthConfig, cache_key: str) -> bool:
        """Retry authentication with freshly fetched CSRF tokens"""
        fresh_tokens = self._fetch_csrf_tokens(auth_config)
        if fresh_tokens:
            # Update credentials with fresh tokens
            updated_config = AuthConfig(
                url=auth_config.url,
                method=auth_config.method,
                credentials={**auth_config.credentials, **fresh_tokens},
                headers=auth_config.headers,
                success_indicators=auth_config.success_indicators,
                failure_indicators=auth_config.failure_indicators,
                csrf_config=auth_config.csrf_config,
                session_validation_url=auth_config.session_validation_url,
                timeout=auth_config.timeout,
                verify_ssl=auth_config.verify_ssl
            )
            return self._perform_fresh_authentication(updated_config, cache_key)
        return False
    
    def _update_session_state(self, response: requests.Response, csrf_tokens: Dict[str, str]):
        """Update session state after successful authentication"""
        # Update cookies
        for cookie in response.cookies:
            self.session_state.cookies[cookie.name] = cookie.value
        
        # Update CSRF tokens
        self.session_state.csrf_tokens.update(csrf_tokens)
        
        # Mark as authenticated
        self.session_state.is_authenticated = True
        self.session_state.last_auth_time = time.time()
        
        # Force recreation of sessions with new state
        if self._requests_session:
            self._requests_session.cookies.update(self.session_state.cookies)
    
    def request(self, method: str, url: str, **kwargs) -> RequestResult:
        """
        Make an HTTP request using the native client with middleware integration
        """
        # Resolve relative URLs
        if self.base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(self.base_url, url)
        
        # Apply middleware preprocessing
        context = MiddlewareContext(
            request_id=f"auth_request_{id(self)}",
            url=url,
            method=method,
            headers=kwargs.get('headers', {}),
            body=kwargs.get('data'),
            params=kwargs.get('params'),
            session_data=self.session_state.__dict__
        )
        
        # Process through middleware
        context = middleware_manager.process_request(context)
        
        # Update request parameters from middleware
        kwargs['headers'] = context.headers
        if context.body:
            kwargs['data'] = context.body
        if context.params:
            kwargs['params'] = context.params
        
        # Make the actual request
        try:
            response = self.requests_session.request(method, url, **kwargs)
            
            # Update session state from response
            for cookie in response.cookies:
                self.session_state.cookies[cookie.name] = cookie.value
            
            # Create RequestResult
            result = RequestResult.from_response(url, method, response, 0.0)
            
            # Process through middleware
            result = middleware_manager.process_response(context, result)
            
            return result
            
        except requests.exceptions.Timeout as e:
            raise LogicPwnTimeoutError(f"Request timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}")
        except Exception as e:
            raise NetworkError(f"Request failed: {e}")
    
    def get(self, url: str, **kwargs) -> RequestResult:
        """GET request"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> RequestResult:
        """POST request"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> RequestResult:
        """PUT request"""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> RequestResult:
        """DELETE request"""
        return self.request('DELETE', url, **kwargs)
    
    def close(self):
        """Clean up resources"""
        if self._requests_session:
            self._requests_session.close()
        if self._aiohttp_session and not self._aiohttp_session.closed:
            asyncio.create_task(self._aiohttp_session.close())


def create_authenticated_client(auth_config: Union[AuthConfig, Dict[str, Any]], base_url: str = "") -> LogicPwnHTTPClient:
    """Create an authenticated HTTP client"""
    if isinstance(auth_config, dict):
        auth_config = AuthConfig(**auth_config)
    
    client = LogicPwnHTTPClient(base_url=base_url)
    
    if client.authenticate(auth_config):
        return client
    else:
        raise AuthenticationError("Failed to authenticate client")
