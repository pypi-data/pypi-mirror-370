"""
Custom exceptions for LogicPwn Business Logic Exploitation Framework.

This package contains all custom exceptions used throughout the framework
for authentication, request execution, and other modules.
"""

from .auth_exceptions import (
    AuthenticationError,
    LoginFailedException,
    NetworkError as AuthNetworkError,
    ValidationError as AuthValidationError,
    SessionError,
    TimeoutError as AuthTimeoutError
)

from .request_exceptions import (
    RequestExecutionError,
    NetworkError,
    ValidationError,
    TimeoutError,
    ResponseError
)

__all__ = [
    # Authentication exceptions
    'AuthenticationError',
    'LoginFailedException',
    'AuthNetworkError',
    'AuthValidationError',
    'SessionError',
    'AuthTimeoutError',
    # Request execution exceptions
    'RequestExecutionError',
    'NetworkError',
    'ValidationError',
    'TimeoutError',
    'ResponseError'
] 