"""
Environment variable loading and reloading for LogicPwn config.
"""
import os
from .config_models import Config

def load_env_vars(config: Config) -> None:
    try:
        if os.getenv("LOGICPWN_TIMEOUT"):
            config.request_defaults.TIMEOUT = int(os.getenv("LOGICPWN_TIMEOUT"))
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_MAX_RETRIES"):
            config.request_defaults.MAX_RETRIES = int(os.getenv("LOGICPWN_MAX_RETRIES"))
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_VERIFY_SSL"):
            config.request_defaults.VERIFY_SSL = os.getenv("LOGICPWN_VERIFY_SSL").lower() == "true"
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_REDACTION_STRING"):
            config.security_defaults.REDACTION_STRING = os.getenv("LOGICPWN_REDACTION_STRING")
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_MAX_LOG_BODY_SIZE"):
            config.security_defaults.MAX_LOG_BODY_SIZE = int(os.getenv("LOGICPWN_MAX_LOG_BODY_SIZE"))
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_LOG_LEVEL"):
            config.logging_defaults.LOG_LEVEL = os.getenv("LOGICPWN_LOG_LEVEL")
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_ENABLE_REQUEST_LOGGING"):
            config.logging_defaults.ENABLE_REQUEST_LOGGING = os.getenv("LOGICPWN_ENABLE_REQUEST_LOGGING").lower() == "true"
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_SESSION_TIMEOUT"):
            config.auth_defaults.SESSION_TIMEOUT = int(os.getenv("LOGICPWN_SESSION_TIMEOUT"))
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_MAX_SESSIONS"):
            config.auth_defaults.MAX_SESSIONS = int(os.getenv("LOGICPWN_MAX_SESSIONS"))
    except Exception:
        pass
    try:
        if os.getenv("LOGICPWN_ENABLE_SESSION_PERSISTENCE"):
            config.auth_defaults.ENABLE_SESSION_PERSISTENCE = os.getenv("LOGICPWN_ENABLE_SESSION_PERSISTENCE").lower() == "true"
    except Exception:
        pass

def reload_env_vars(config: Config) -> None:
    load_env_vars(config) 