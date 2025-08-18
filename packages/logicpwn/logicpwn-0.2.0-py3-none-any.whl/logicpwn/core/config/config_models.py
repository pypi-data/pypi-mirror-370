"""
Configuration models and enums for LogicPwn.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import os

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class BodyType(Enum):
    JSON = "json"
    FORM = "form"
    RAW = "raw"
    MULTIPART = "multipart"

@dataclass
class RequestDefaults:
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
        self.ALLOW_REDIRECTS = ALLOW_REDIRECTS if 'ALLOW_REDIRECTS' in kwargs or 'ALLOW_REDIRECTS' in locals() else FOLLOW_REDIRECTS
        self.FOLLOW_REDIRECTS = FOLLOW_REDIRECTS if 'FOLLOW_REDIRECTS' in kwargs or 'FOLLOW_REDIRECTS' in locals() else ALLOW_REDIRECTS
        self.MAX_REDIRECTS = MAX_REDIRECTS

@dataclass
class SecurityDefaults:
    SENSITIVE_HEADERS: set = field(default_factory=lambda: {
        'authorization', 'cookie', 'x-api-key', 'x-auth-token',
        'x-csrf-token', 'x-session-id', 'x-access-token'
    })
    SENSITIVE_PARAMS: set = field(default_factory=lambda: {
        'password', 'token', 'key', 'secret', 'auth', 'session'
    })
    REDACTION_STRING: str = "[REDACTED]"
    MAX_LOG_BODY_SIZE: int = 1024

@dataclass
class LoggingDefaults:
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_RESPONSE_LOGGING: bool = True
    ENABLE_ERROR_LOGGING: bool = True

@dataclass
class AuthDefaults:
    SESSION_TIMEOUT: int = 3600
    MAX_SESSIONS: int = 10
    SESSION_CLEANUP_INTERVAL: int = 300
    DEFAULT_AUTH_TYPE: str = "basic"
    ENABLE_SESSION_PERSISTENCE: bool = True
    def __init__(self, SESSION_TIMEOUT: int = 3600, MAX_SESSIONS: int = 10, SESSION_CLEANUP_INTERVAL: int = 300, DEFAULT_AUTH_TYPE: str = "basic", ENABLE_SESSION_PERSISTENCE: bool = True, **kwargs):
        self.SESSION_TIMEOUT = SESSION_TIMEOUT
        self.MAX_SESSIONS = MAX_SESSIONS
        self.SESSION_CLEANUP_INTERVAL = SESSION_CLEANUP_INTERVAL
        self.DEFAULT_AUTH_TYPE = DEFAULT_AUTH_TYPE
        self.ENABLE_SESSION_PERSISTENCE = ENABLE_SESSION_PERSISTENCE

@dataclass
class Config:
    request_defaults: RequestDefaults = field(default_factory=RequestDefaults)
    security_defaults: SecurityDefaults = field(default_factory=SecurityDefaults)
    logging_defaults: LoggingDefaults = field(default_factory=LoggingDefaults)
    auth_defaults: AuthDefaults = field(default_factory=AuthDefaults)
    def __init__(self):
        self.request_defaults = RequestDefaults()
        self.security_defaults = SecurityDefaults()
        self.logging_defaults = LoggingDefaults()
        self.auth_defaults = AuthDefaults()
        self._load_env_vars()
    def reload_env_vars(self):
        self._load_env_vars()
    def _load_env_vars(self):
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