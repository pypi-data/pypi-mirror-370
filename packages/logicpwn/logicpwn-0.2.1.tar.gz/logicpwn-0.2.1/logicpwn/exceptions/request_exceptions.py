"""
Custom exceptions for request execution module.

This module defines all request execution-related exceptions used throughout
the LogicPwn framework.
"""


class RequestExecutionError(Exception):
    """Base request execution exception.
    
    This is the parent class for all request execution-related exceptions.
    """
    pass


class BaseRequestError(RequestExecutionError):
    """Base class for request exceptions with additional attributes.
    
    This class provides a common pattern for request exceptions
    that need to store additional context information.
    """
    
    def __init__(self, message: str, **kwargs):
        """Initialize exception with message and additional attributes.
        
        Args:
            message: Error message
            **kwargs: Additional attributes to store with the exception
        """
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(self.message)


class NetworkError(BaseRequestError):
    """Network-related request error.
    
    Raised when network issues prevent request execution from completing,
    such as connection timeouts, DNS failures, or SSL errors.
    """
    
    def __init__(self, message: str = "Network error during request execution", 
                 original_exception: Exception = None):
        super().__init__(message, original_exception=original_exception)


class ValidationError(BaseRequestError):
    """Request configuration validation error.
    
    Raised when request configuration is invalid or missing
    required fields.
    """
    
    def __init__(self, message: str = "Invalid request configuration", 
                 field: str = None, value: str = None):
        super().__init__(message, field=field, value=value)


class TimeoutError(BaseRequestError):
    """Request timeout error.
    
    Raised when requests exceed the configured timeout period.
    """
    
    def __init__(self, message: str = "Request timed out", 
                 timeout_seconds: int = None):
        super().__init__(message, timeout_seconds=timeout_seconds)


class ResponseError(BaseRequestError):
    """HTTP response error.
    
    Raised when requests return error status codes or unexpected
    response content.
    """
    
    def __init__(self, message: str = "Request returned error response", 
                 status_code: int = None, response_text: str = None):
        super().__init__(message, status_code=status_code, response_text=response_text) 