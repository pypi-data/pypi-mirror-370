"""
Logger class for LogicPwn with sensitive data redaction.
"""
import logging
import json
from typing import Any, Dict, Optional
from logicpwn.core.config.config_utils import config, get_log_level
from .redactor import SensitiveDataRedactor

class LogicPwnLogger:
    """Centralized logger for LogicPwn with sensitive data redaction."""
    def __init__(self, name: str = "logicpwn"):
        self.logger = logging.getLogger(name)
        self.redactor = SensitiveDataRedactor()
        self.logging_enabled = True
        self._setup_logger()
    def _setup_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                config.logging_defaults.LOG_FORMAT,
                datefmt=config.logging_defaults.LOG_DATE_FORMAT
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, get_log_level().upper()))
    def log_request(self, method: str, url: str, headers: Optional[Dict] = None,
                   params: Optional[Dict] = None, body: Optional[Any] = None,
                   timeout: Optional[int] = None):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_REQUEST_LOGGING:
            return
        redacted_url = self.redactor.redact_url_params(url)
        redacted_headers = self.redactor.redact_headers(headers or {})
        log_data = {
            "method": method,
            "url": redacted_url,
            "headers": redacted_headers,
            "timeout": timeout
        }
        if params:
            log_data["params"] = self.redactor.redact_form_data(params)
        if body:
            if isinstance(body, dict):
                log_data["body"] = self.redactor.redact_form_data(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[:self.redactor.max_body_size]
        self.logger.info(f"Request: {json.dumps(log_data, indent=2)}")
    def log_response(self, status_code: int, headers: Optional[Dict] = None,
                    body: Optional[Any] = None, response_time: Optional[float] = None):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_RESPONSE_LOGGING:
            return
        redacted_headers = self.redactor.redact_headers(headers or {})
        log_data = {
            "status_code": status_code,
            "headers": redacted_headers,
            "response_time": response_time
        }
        if body:
            if isinstance(body, (dict, list)):
                log_data["body"] = self.redactor.redact_json_body(body)
            elif isinstance(body, str):
                log_data["body"] = self.redactor._redact_string_body(body)
            else:
                log_data["body"] = str(body)[:self.redactor.max_body_size]
        self.logger.info(f"Response: {json.dumps(log_data, indent=2)}")
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        if not self.logging_enabled:
            return
        if not config.logging_defaults.ENABLE_ERROR_LOGGING:
            return
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        if context:
            redacted_context = {}
            for key, value in context.items():
                if isinstance(value, dict):
                    redacted_context[key] = self.redactor.redact_form_data(value)
                elif isinstance(value, str) and key.lower() in self.redactor.sensitive_params:
                    redacted_context[key] = self.redactor.redaction_string
                else:
                    redacted_context[key] = value
            log_data["context"] = redacted_context
        self.logger.error(f"Error: {json.dumps(log_data, indent=2)}")
    def log_info(self, message: str, data: Optional[Dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.info(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.info(message)
    def log_debug(self, message: str, data: Optional[Dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.debug(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.debug(message)
    def log_warning(self, message: str, data: Optional[Dict] = None):
        if not self.logging_enabled:
            return
        if data:
            redacted_data = self.redactor.redact_form_data(data)
            self.logger.warning(f"{message}: {json.dumps(redacted_data, indent=2)}")
        else:
            self.logger.warning(message) 