"""
Centralized configuration for LogicPwn.

This module contains all constants, default values, and configuration settings
used throughout the codebase. It provides a single source of truth for
all configuration values and makes it easy to modify behavior across the
entire application.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
from logicpwn.core.cache import config_cache


class HTTPMethod(Enum):
    """HTTP methods supported by the request runner."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class BodyType(Enum):
    """Supported body types for requests."""
    JSON = "json"
    FORM = "form"
    RAW = "raw"
    MULTIPART = "multipart"


@dataclass
class RequestDefaults:
    """Default values for request configuration."""
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    BACKOFF_FACTOR: float = 2.0
    MAX_BACKOFF: float = 60.0
    VERIFY_SSL: bool = True
    ALLOW_REDIRECTS: bool = True
    FOLLOW_REDIRECTS: bool = True
    MAX_REDIRECTS: int = 5

    def __init__(self, TIMEOUT: int = 30, MAX_RETRIES: int = 3, RETRY_DELAY: float = 1.0, BACKOFF_FACTOR: float = 2.0, MAX_BACKOFF: float = 60.0, VERIFY_SSL: bool = True, ALLOW_REDIRECTS: bool = True, FOLLOW_REDIRECTS: bool = True, MAX_REDIRECTS: int = 5, **kwargs):
                                            self.TIMEOUT = TIMEOUT
                                            self.MAX_RETRIES = MAX_RETRIES
                                            self.RETRY_DELAY = RETRY_DELAY
                                            self.BACKOFF_FACTOR = BACKOFF_FACTOR
                                            self.MAX_BACKOFF = MAX_BACKOFF
                                            self.VERIFY_SSL = VERIFY_SSL
                                                # Keep ALLOW_REDIRECTS and FOLLOW_REDIRECTS in sync
                                            self.ALLOW_REDIRECTS = ALLOW_REDIRECTS if 'ALLOW_REDIRECTS' in kwargs or 'ALLOW_REDIRECTS' in locals() else FOLLOW_REDIRECTS
                                            self.FOLLOW_REDIRECTS = FOLLOW_REDIRECTS if 'FOLLOW_REDIRECTS' in kwargs or 'FOLLOW_REDIRECTS' in locals() else ALLOW_REDIRECTS
                                            self.MAX_REDIRECTS = MAX_REDIRECTS


@dataclass
class SecurityDefaults:
    """Default security-related settings."""
    SENSITIVE_HEADERS: set = field(default_factory=lambda: {
                                            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
                                            'x-csrf-token', 'x-session-id', 'x-access-token'
    })
    SENSITIVE_PARAMS: set = field(default_factory=lambda: {
                                            'password', 'token', 'key', 'secret', 'auth', 'session'
    })
    REDACTION_STRING: str = "[REDACTED]"
    MAX_LOG_BODY_SIZE: int = 1024  # bytes


@dataclass
class LoggingDefaults:
    """Default logging configuration."""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_RESPONSE_LOGGING: bool = True
    ENABLE_ERROR_LOGGING: bool = True


@dataclass
class AuthDefaults:
    """Default authentication settings."""
    SESSION_TIMEOUT: int = 3600  # 1 hour
    MAX_SESSIONS: int = 10
    SESSION_CLEANUP_INTERVAL: int = 300  # 5 minutes
    DEFAULT_AUTH_TYPE: str = "basic"
    ENABLE_SESSION_PERSISTENCE: bool = True

    def __init__(self, SESSION_TIMEOUT: int = 3600, MAX_SESSIONS: int = 10, SESSION_CLEANUP_INTERVAL: int = 300, DEFAULT_AUTH_TYPE: str = "basic", ENABLE_SESSION_PERSISTENCE: bool = True, **kwargs):
                                            self.SESSION_TIMEOUT = SESSION_TIMEOUT
                                            self.MAX_SESSIONS = MAX_SESSIONS
                                            self.SESSION_CLEANUP_INTERVAL = SESSION_CLEANUP_INTERVAL
                                            self.DEFAULT_AUTH_TYPE = DEFAULT_AUTH_TYPE
                                            self.ENABLE_SESSION_PERSISTENCE = ENABLE_SESSION_PERSISTENCE


class Config:
    """Centralized configuration manager for LogicPwn."""
    
    def __init__(self):
                                            self.request_defaults = RequestDefaults()
                                            self.security_defaults = SecurityDefaults()
                                            self.logging_defaults = LoggingDefaults()
                                            self.auth_defaults = AuthDefaults()
                                            
                                                # Load environment variables
                                            self._load_env_vars()
    
    def reload_env_vars(self):
                                            """Reload configuration from environment variables (for test isolation)."""
                                            self._load_env_vars()
    
    def _load_env_vars(self):
                                            """Load configuration from environment variables."""
                                                # Request defaults
                                            try:
                                                if os.getenv("LOGICPWN_TIMEOUT"):
                                                    self.request_defaults.TIMEOUT = int(os.getenv("LOGICPWN_TIMEOUT"))
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_MAX_RETRIES"):
                                                    self.request_defaults.MAX_RETRIES = int(os.getenv("LOGICPWN_MAX_RETRIES"))
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_VERIFY_SSL"):
                                                    self.request_defaults.VERIFY_SSL = os.getenv("LOGICPWN_VERIFY_SSL").lower() == "true"
                                            except Exception:
                                                pass
                                                # Security defaults
                                            try:
                                                if os.getenv("LOGICPWN_REDACTION_STRING"):
                                                    self.security_defaults.REDACTION_STRING = os.getenv("LOGICPWN_REDACTION_STRING")
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_MAX_LOG_BODY_SIZE"):
                                                    self.security_defaults.MAX_LOG_BODY_SIZE = int(os.getenv("LOGICPWN_MAX_LOG_BODY_SIZE"))
                                            except Exception:
                                                pass
                                                # Logging defaults
                                            try:
                                                if os.getenv("LOGICPWN_LOG_LEVEL"):
                                                    self.logging_defaults.LOG_LEVEL = os.getenv("LOGICPWN_LOG_LEVEL")
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_ENABLE_REQUEST_LOGGING"):
                                                    self.logging_defaults.ENABLE_REQUEST_LOGGING = os.getenv("LOGICPWN_ENABLE_REQUEST_LOGGING").lower() == "true"
                                            except Exception:
                                                pass
                                                # Auth defaults
                                            try:
                                                if os.getenv("LOGICPWN_SESSION_TIMEOUT"):
                                                    self.auth_defaults.SESSION_TIMEOUT = int(os.getenv("LOGICPWN_SESSION_TIMEOUT"))
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_MAX_SESSIONS"):
                                                    self.auth_defaults.MAX_SESSIONS = int(os.getenv("LOGICPWN_MAX_SESSIONS"))
                                            except Exception:
                                                pass
                                            try:
                                                if os.getenv("LOGICPWN_ENABLE_SESSION_PERSISTENCE"):
                                                    self.auth_defaults.ENABLE_SESSION_PERSISTENCE = os.getenv("LOGICPWN_ENABLE_SESSION_PERSISTENCE").lower() == "true"
                                            except Exception:
                                                pass
    
    def get_request_defaults(self) -> RequestDefaults:
                                            """Get request default configuration."""
                                            return self.request_defaults
    
    def get_security_defaults(self) -> SecurityDefaults:
                                            """Get security default configuration."""
                                            return self.security_defaults
    
    def get_logging_defaults(self) -> LoggingDefaults:
                                            """Get logging default configuration."""
                                            return self.logging_defaults
    
    def get_auth_defaults(self) -> AuthDefaults:
                                            """Get authentication default configuration."""
                                            return self.auth_defaults
    
    def update_config(self, **kwargs):
                                            """Update configuration values."""
                                            for key, value in kwargs.items():
                                                if hasattr(self.request_defaults, key):
                                                    setattr(self.request_defaults, key, value)
                                                elif hasattr(self.security_defaults, key):
                                                    setattr(self.security_defaults, key, value)
                                                elif hasattr(self.logging_defaults, key):
                                                    setattr(self.logging_defaults, key, value)
                                                elif hasattr(self.auth_defaults, key):
                                                    setattr(self.auth_defaults, key, value)
                                                else:
                                                    raise ValueError(f"Unknown configuration key: {key}")


# Global configuration instance
config = Config()


# Convenience functions for accessing configuration
def get_timeout() -> int:
    """Get request timeout from configuration."""
    cached_timeout = config_cache.get("timeout")
    if cached_timeout is not None:
                                            return cached_timeout
    
    timeout = config.get_request_defaults().TIMEOUT
    config_cache.set("timeout", timeout, ttl=600)  # Cache for 10 minutes
    return timeout


def get_max_retries() -> int:
    """Get maximum retries from configuration."""
    cached_retries = config_cache.get("max_retries")
    if cached_retries is not None:
                                            return cached_retries
    
    retries = config.get_request_defaults().MAX_RETRIES
    config_cache.set("max_retries", retries, ttl=600)  # Cache for 10 minutes
    return retries


def get_sensitive_headers() -> set:
    """Get sensitive headers from configuration."""
    cached_headers = config_cache.get("sensitive_headers")
    if cached_headers is not None:
                                            return cached_headers
    
    headers = config.get_security_defaults().SENSITIVE_HEADERS
    config_cache.set("sensitive_headers", headers, ttl=600)  # Cache for 10 minutes
    return headers


def get_sensitive_params() -> set:
    """Get sensitive parameters from configuration."""
    cached_params = config_cache.get("sensitive_params")
    if cached_params is not None:
                                            return cached_params
    
    params = config.get_security_defaults().SENSITIVE_PARAMS
    config_cache.set("sensitive_params", params, ttl=600)  # Cache for 10 minutes
    return params


def get_redaction_string() -> str:
    """Get redaction string from configuration."""
    cached_string = config_cache.get("redaction_string")
    if cached_string is not None:
                                            return cached_string
    
    redaction = config.get_security_defaults().REDACTION_STRING
    config_cache.set("redaction_string", redaction, ttl=600)  # Cache for 10 minutes
    return redaction


def get_max_log_body_size() -> int:
    """Get maximum log body size from configuration."""
    cached_size = config_cache.get("max_log_body_size")
    if cached_size is not None:
                                            return cached_size
    
    size = config.get_security_defaults().MAX_LOG_BODY_SIZE
    config_cache.set("max_log_body_size", size, ttl=600)  # Cache for 10 minutes
    return size


def get_log_level() -> str:
    """Get log level from configuration."""
    cached_level = config_cache.get("log_level")
    if cached_level is not None:
                                            return cached_level
    
    level = config.get_logging_defaults().LOG_LEVEL
    config_cache.set("log_level", level, ttl=600)  # Cache for 10 minutes
    return level


def is_request_logging_enabled() -> bool:
    """Check if request logging is enabled."""
    cached_enabled = config_cache.get("request_logging_enabled")
    if cached_enabled is not None:
                                            return cached_enabled
    
    enabled = config.get_logging_defaults().ENABLE_REQUEST_LOGGING
    config_cache.set("request_logging_enabled", enabled, ttl=600)  # Cache for 10 minutes
    return enabled


def is_response_logging_enabled() -> bool:
    """Check if response logging is enabled."""
    cached_enabled = config_cache.get("response_logging_enabled")
    if cached_enabled is not None:
                                            return cached_enabled
    
    enabled = config.get_logging_defaults().ENABLE_RESPONSE_LOGGING
    config_cache.set("response_logging_enabled", enabled, ttl=600)  # Cache for 10 minutes
    return enabled


def is_error_logging_enabled() -> bool:
    """Check if error logging is enabled."""
    cached_enabled = config_cache.get("error_logging_enabled")
    if cached_enabled is not None:
                                            return cached_enabled
    
    enabled = config.get_logging_defaults().ENABLE_ERROR_LOGGING
    config_cache.set("error_logging_enabled", enabled, ttl=600)  # Cache for 10 minutes
    return enabled


def get_session_timeout() -> int:
    """Get session timeout from configuration."""
    cached_timeout = config_cache.get("session_timeout")
    if cached_timeout is not None:
                                            return cached_timeout
    
    timeout = config.get_auth_defaults().SESSION_TIMEOUT
    config_cache.set("session_timeout", timeout, ttl=600)  # Cache for 10 minutes
    return timeout


def get_max_sessions() -> int:
    """Get maximum sessions from configuration."""
    cached_sessions = config_cache.get("max_sessions")
    if cached_sessions is not None:
                                            return cached_sessions
    
    sessions = config.get_auth_defaults().MAX_SESSIONS
    config_cache.set("max_sessions", sessions, ttl=600)  # Cache for 10 minutes
    return sessions


def get_logging_defaults() -> LoggingDefaults:
    """Get logging default configuration."""
    return config.get_logging_defaults() 


def reload_config_env_vars():
    """Reload the global config from environment variables (for test isolation)."""
    config.reload_env_vars() 

# Add this function for test isolation
_config_singleton = [config]

def reset_config_singleton():
    """Reset the global config singleton for test isolation."""
    global config
    config = Config()
    _config_singleton[0] = config 