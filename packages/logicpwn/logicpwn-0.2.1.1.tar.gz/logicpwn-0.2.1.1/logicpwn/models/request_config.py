"""
Request configuration model for LogicPwn Business Logic Exploitation Framework.

This module provides the RequestConfig model for validating and storing
HTTP request configuration parameters. Designed to support various
request types for exploit chaining and security testing workflows.
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from urllib.parse import urlparse


class RequestConfig(BaseModel):
    """Request configuration model for HTTP requests in exploit chaining workflows.
    
    This model validates and stores HTTP request configuration parameters
    including URL, method, headers, and body content. Designed to support
    various request types for different target applications and APIs.
    """
    
    url: str = Field(..., description="Target URL for the request")
    method: str = Field(default="GET", description="HTTP method for the request")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP headers")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Form data for POST requests")
    json_data: Optional[Dict[str, Any]] = Field(default=None, description="JSON body for requests")
    raw_body: Optional[str] = Field(default=None, description="Raw body content")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format for request endpoints."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format - must include scheme and netloc')
        return v
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method for requests."""
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}
        v_up = v.upper()
        if v_up not in valid_methods:
            raise ValueError(f'method must be one of {valid_methods}')
        return v_up
    
    @model_validator(mode='after')
    def validate_body_types(self) -> 'RequestConfig':
        """Ensure only one body type is specified per request.
        
        This validator prevents conflicts between different body types:
        - data: Form data for POST requests
        - json_data: JSON body for API requests  
        - raw_body: Raw body content for custom formats
        
        Only one of these fields should be specified per request to avoid
        ambiguity in request processing.
        """
        body_fields = ['data', 'json_data', 'raw_body']
        specified_fields = [field for field in body_fields if getattr(self, field) is not None]
        
        if len(specified_fields) > 1:
            field_descriptions = {
                'data': 'form data',
                'json_data': 'JSON data', 
                'raw_body': 'raw body content'
            }
            descriptions = [field_descriptions[field] for field in specified_fields]
            raise ValueError(
                f"Multiple body types specified: {', '.join(descriptions)}. "
                f"Only one body type allowed per request. Use either form data, "
                f"JSON data, or raw body content, but not multiple types."
            )
        
        return self 