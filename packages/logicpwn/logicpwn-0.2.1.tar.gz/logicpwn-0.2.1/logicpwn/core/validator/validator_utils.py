"""
Helper functions for LogicPwn response validation.
"""
import re

MAX_RESPONSE_TEXT_LENGTH = 500

def _sanitize_response_text(text: str, max_length: int = MAX_RESPONSE_TEXT_LENGTH) -> str:
    """Sanitize response text for secure logging."""
    if not text:
        return ""
    if len(text) > max_length:
        text = text[:max_length] + "..."
    sensitive_patterns = [
        (r'password["\']?\s*[:=]\s*["\']?[^"\s]+', 'password": "[REDACTED]"'),
        (r'token["\']?\s*[:=]\s*["\']?[^"\s]+', 'token": "[REDACTED]"'),
        (r'key["\']?\s*[:=]\s*["\']?[^"\s]+', 'key": "[REDACTED]"'),
        (r'secret["\']?\s*[:=]\s*["\']?[^"\s]+', 'secret": "[REDACTED]"'),
    ]
    for pattern, replacement in sensitive_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text 