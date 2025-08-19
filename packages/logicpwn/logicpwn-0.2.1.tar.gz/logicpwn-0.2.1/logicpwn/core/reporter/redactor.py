import re
from typing import List
from logicpwn.core.reporter.models import RedactionRule
from logicpwn.core.logging.redactor import SensitiveDataRedactor

class AdvancedRedactor(SensitiveDataRedactor):
    """
    Redactor that supports custom regex-based redaction rules in addition to global sensitive patterns.
    Inherits from SensitiveDataRedactor and applies user-defined RedactionRule patterns.
    """
    def __init__(self, custom_rules: List[RedactionRule] = None):
        """
        Initialize the redactor with optional custom regex rules.
        :param custom_rules: List of RedactionRule objects for custom redaction.
        """
        super().__init__()
        self.custom_rules = custom_rules or []

    def redact_string_body(self, content: str) -> str:
        """
        Redact sensitive data from a string using both built-in and custom rules.
        :param content: The string content to redact.
        :return: Redacted string.
        """
        redacted = super().redact_string_body(content)
        for rule in self.custom_rules:
            redacted = re.sub(rule.pattern, rule.replacement, redacted, flags=re.IGNORECASE)
        return redacted 