"""
Configuration utility functions for LogicPwn.
"""
from .config_models import Config, LoggingDefaults
from .config_env import reload_env_vars

# Global configuration instance
config = Config()

# Convenience functions for accessing configuration
def get_timeout() -> int:
    return config.request_defaults.TIMEOUT

def get_max_retries() -> int:
    return config.request_defaults.MAX_RETRIES

def get_sensitive_headers() -> set:
    return config.security_defaults.SENSITIVE_HEADERS

def get_sensitive_params() -> set:
    return config.security_defaults.SENSITIVE_PARAMS

def get_redaction_string() -> str:
    return config.security_defaults.REDACTION_STRING

def get_max_log_body_size() -> int:
    return config.security_defaults.MAX_LOG_BODY_SIZE

def get_log_level() -> str:
    return config.logging_defaults.LOG_LEVEL

def is_request_logging_enabled() -> bool:
    return config.logging_defaults.ENABLE_REQUEST_LOGGING

def is_response_logging_enabled() -> bool:
    return config.logging_defaults.ENABLE_RESPONSE_LOGGING

def is_error_logging_enabled() -> bool:
    return config.logging_defaults.ENABLE_ERROR_LOGGING

def get_session_timeout() -> int:
    return config.auth_defaults.SESSION_TIMEOUT

def get_max_sessions() -> int:
    return config.auth_defaults.MAX_SESSIONS

def get_logging_defaults() -> LoggingDefaults:
    return config.logging_defaults

def reload_config_env_vars():
    reload_env_vars(config)

def reset_config_singleton():
    global config
    config = Config() 