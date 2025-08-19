"""
Redaction utilities for LogicPwn logging.
"""
import json
import re
from typing import Any, Dict, List, Union
from urllib.parse import parse_qs, urlencode, urlparse
from logicpwn.core.config.config_utils import (
    get_sensitive_headers,
    get_sensitive_params,
    get_redaction_string,
    get_max_log_body_size
)

class SensitiveDataRedactor:
    """Handles redaction of sensitive data from logs."""
    def __init__(self):
        self.sensitive_headers = get_sensitive_headers()
        self.sensitive_params = get_sensitive_params()
        self.redaction_string = get_redaction_string()
        self.max_body_size = get_max_log_body_size()
    def redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        if not headers:
            return {}
        redacted_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                redacted_headers[key] = self.redaction_string
            else:
                redacted_headers[key] = value
        return redacted_headers
    def redact_url_params(self, url: str) -> str:
        if not url or '?' not in url:
            return url
        parsed = urlparse(url)
        if not parsed.query:
            return url
        params = parse_qs(parsed.query)
        redacted_params = {}
        for key, values in params.items():
            if key.lower() in self.sensitive_params:
                redacted_params[key] = [self.redaction_string]
            else:
                redacted_params[key] = values
        redacted_query = urlencode(redacted_params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{redacted_query}"
    def redact_json_body(self, body: Union[str, Dict, List]) -> str:
        if not body:
            return ""
        try:
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            redacted_data = self._redact_json_recursive(data)
            return json.dumps(redacted_data, indent=2)
        except (json.JSONDecodeError, TypeError):
            return self._redact_string_body(str(body))
    def redact_string_body(self, body: str) -> str:
        return self._redact_string_body(body)
    def _redact_json_recursive(self, data: Any) -> Any:
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if isinstance(key, str) and key.lower() in self.sensitive_params:
                    redacted[key] = self.redaction_string
                else:
                    redacted[key] = self._redact_json_recursive(value)
            return redacted
        elif isinstance(data, list):
            return [self._redact_json_recursive(item) for item in data]
        else:
            return data
    def _redact_string_body(self, body: str) -> str:
        if not body:
            return ""
        if len(body) > self.max_body_size:
            body = body[:self.max_body_size] + "... [TRUNCATED]"
        patterns = [
            r'password["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'key["\']?\s*[:=]\s*["\'][^"\']*["\']',
            r'auth["\']?\s*[:=]\s*["\'][^"\']*["\']',
        ]
        redacted_body = body
        for pattern in patterns:
            redacted_body = re.sub(pattern, lambda m: m.group().split('=')[0] + '=' + f'"{self.redaction_string}"', redacted_body, flags=re.IGNORECASE)
        return redacted_body
    def redact_form_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data:
            return {}
        redacted_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in self.sensitive_params:
                redacted_data[key] = self.redaction_string
            else:
                redacted_data[key] = value
        return redacted_data 