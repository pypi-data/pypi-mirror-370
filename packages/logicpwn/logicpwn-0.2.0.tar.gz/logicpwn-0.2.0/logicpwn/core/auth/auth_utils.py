"""
Authentication utilities for LogicPwn.
"""
from typing import Dict
import requests
from loguru import logger
from logicpwn.core.utils import check_indicators
from .auth_models import AuthConfig
from .auth_constants import MAX_RESPONSE_TEXT_LENGTH

def _sanitize_credentials(credentials: Dict[str, str]) -> Dict[str, str]:
    return {key: '*' * len(value) if value else '***' for key, value in credentials.items()}

def _create_session(config: AuthConfig) -> requests.Session:
    session = requests.Session()
    session.verify = config.verify_ssl
    # Note: timeout is passed to individual requests, not set on session
    # Only add non-request-specific headers to session
    if config.headers:
        persistent_headers = {}
        for key, value in config.headers.items():
            # Don't persist Content-Type as it's request-specific
            if key.lower() != 'content-type':
                persistent_headers[key] = value
        if persistent_headers:
            session.headers.update(persistent_headers)
    return session

def _handle_response_indicators(response: requests.Response, config: AuthConfig) -> None:
    response_text = response.text
    failure_match, _ = check_indicators(response_text, config.failure_indicators, "failure")
    if failure_match:
        logger.error("Authentication failed - failure indicators found in response")
        from logicpwn.exceptions import LoginFailedException
        raise LoginFailedException(
            message="Authentication failed - failure indicators detected",
            response_code=response.status_code,
            response_text=response_text[:MAX_RESPONSE_TEXT_LENGTH]
        )
    if config.success_indicators:
        success_match, _ = check_indicators(response_text, config.success_indicators, "success")
        if not success_match:
            logger.error("Authentication failed - no success indicators found")
            from logicpwn.exceptions import LoginFailedException
            raise LoginFailedException(
                message="Authentication failed - no success indicators detected",
                response_code=response.status_code,
                response_text=response_text[:MAX_RESPONSE_TEXT_LENGTH]
            ) 