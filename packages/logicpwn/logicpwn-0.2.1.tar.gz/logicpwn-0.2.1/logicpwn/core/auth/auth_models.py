"""
Authentication models for LogicPwn.
"""
import re
from typing import Dict, Optional, List, Pattern, Callable, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from dataclasses import dataclass, field
from urllib.parse import urlparse

HTTP_METHODS = {"GET", "POST"}


@dataclass
class SessionState:
    """Represents the state of an HTTP session"""
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    csrf_tokens: Dict[str, str] = field(default_factory=dict)  # token_name -> token_value
    auth_data: Dict[str, Any] = field(default_factory=dict)
    last_auth_time: float = 0.0
    is_authenticated: bool = False
    base_url: str = ""


@dataclass 
class CSRFConfig:
    """Configuration for CSRF token handling"""
    enabled: bool = True
    token_patterns: List[Pattern] = field(default_factory=lambda: [
        re.compile(r'name=["\']([^"\']*token[^"\']*)["\'].*?value=["\']([^"\']+)["\']', re.IGNORECASE),
        re.compile(r'name=["\'](_token)["\'].*?value=["\']([^"\']+)["\']', re.IGNORECASE),
        re.compile(r'name=["\']([^"\']*csrf[^"\']*)["\'].*?value=["\']([^"\']+)["\']', re.IGNORECASE),
        re.compile(r'<meta[^>]+name=["\']([^"\']*token[^"\']*)["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE),
    ])
    auto_include: bool = True  # Automatically include tokens in subsequent requests
    refresh_on_failure: bool = True  # Re-fetch tokens if auth fails

class AuthConfig(BaseModel):
    """Enhanced authentication configuration with advanced HTTP client features"""
    url: str = Field(..., description="Login endpoint URL")
    method: str = Field(default="POST", description="HTTP method for login")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Login credentials")
    success_indicators: List[str] = Field(default_factory=list, description="Text indicators of successful login")
    failure_indicators: List[str] = Field(default_factory=list, description="Text indicators of failed login")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional HTTP headers")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    
    # Advanced HTTP client features
    csrf_config: Optional[CSRFConfig] = Field(default=None, description="CSRF token handling configuration")
    session_validation_url: Optional[str] = Field(default=None, description="URL to validate session persistence")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum authentication retry attempts")
    pre_auth_callback: Optional[Callable] = Field(default=None, description="Custom pre-authentication logic")
    post_auth_callback: Optional[Callable] = Field(default=None, description="Custom post-authentication validation")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Callable types

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format - must include scheme and netloc')
        return v

    @field_validator('credentials')
    @classmethod
    def validate_credentials(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError('Credentials cannot be empty')
        return v

    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        v_up = v.upper()
        if v_up not in HTTP_METHODS:
            raise ValueError(f'method must be one of {HTTP_METHODS}')
        return v_up 