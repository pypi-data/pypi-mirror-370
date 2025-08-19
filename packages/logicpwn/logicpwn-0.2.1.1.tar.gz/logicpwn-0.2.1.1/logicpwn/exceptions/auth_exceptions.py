"""
Custom exceptions for authentication module.

This module defines all authentication-related exceptions used throughout
the LogicPwn framework.
"""


class AuthenticationError(Exception):
    """Base authentication exception.
    
    This is the parent class for all authentication-related exceptions.
    """
    pass


class BaseAuthenticationError(AuthenticationError):
    """Base class for authentication exceptions with additional attributes.
    
    This class provides a common pattern for authentication exceptions
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


class LoginFailedException(BaseAuthenticationError):
    """Login failed with provided credentials.
    
    Raised when authentication attempt fails due to invalid credentials
    or other login-related issues.
    """
    
    def __init__(self, message: str = "Login failed with provided credentials", 
                 response_code: int = None, response_text: str = None):
        super().__init__(message, response_code=response_code, response_text=response_text)


class NetworkError(BaseAuthenticationError):
    """Network-related authentication error.
    
    Raised when network issues prevent authentication from completing,
    such as connection timeouts, DNS failures, or SSL errors.
    """
    
    def __init__(self, message: str = "Network error during authentication", 
                 original_exception: Exception = None):
        super().__init__(message, original_exception=original_exception)


class ValidationError(BaseAuthenticationError):
    """Configuration validation error.
    
    Raised when authentication configuration is invalid or missing
    required fields.
    """
    
    def __init__(self, message: str = "Invalid authentication configuration", 
                 field: str = None, value: str = None):
        super().__init__(message, field=field, value=value)


class SessionError(BaseAuthenticationError):
    """Session management error.
    
    Raised when there are issues with session creation, persistence,
    or cookie handling.
    """
    
    def __init__(self, message: str = "Session error occurred", 
                 session_id: str = None):
        super().__init__(message, session_id=session_id)


class TimeoutError(BaseAuthenticationError):
    """Authentication timeout error.
    
    Raised when authentication requests exceed the configured timeout
    period.
    """
    
    def __init__(self, message: str = "Authentication request timed out", 
                 timeout_seconds: int = None):
        super().__init__(message, timeout_seconds=timeout_seconds) 