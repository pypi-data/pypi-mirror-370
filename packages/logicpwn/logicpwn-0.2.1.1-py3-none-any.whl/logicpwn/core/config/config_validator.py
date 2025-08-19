"""
Configuration validation utilities for LogicPwn.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from logicpwn.core.config.config_models import Config

@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    level: str  # "error", "warning", "info"
    category: str  # "security", "performance", "functionality"
    message: str
    field: str
    suggestion: Optional[str] = None

class ConfigValidator:
    """Validate configuration values for consistency and security."""
    
    def __init__(self):
        self.issues = []
    
    def validate_config(self, config: Config) -> List[ValidationIssue]:
        """Validate configuration and return list of issues."""
        self.issues = []
        
        self._validate_request_defaults(config.request_defaults)
        self._validate_security_defaults(config.security_defaults)
        self._validate_logging_defaults(config.logging_defaults)
        self._validate_auth_defaults(config.auth_defaults)
        self._validate_cross_module_consistency(config)
        
        return self.issues
    
    def _validate_request_defaults(self, request_defaults):
        """Validate request configuration."""
        # Timeout validation
        if request_defaults.TIMEOUT < 1:
            self._add_issue("error", "functionality", 
                          "Request timeout must be at least 1 second",
                          "request_defaults.TIMEOUT",
                          "Set timeout to at least 5 seconds for reliable requests")
        elif request_defaults.TIMEOUT < 5:
            self._add_issue("warning", "performance",
                          "Request timeout is very low, may cause premature timeouts",
                          "request_defaults.TIMEOUT",
                          "Consider increasing to 10-30 seconds")
        elif request_defaults.TIMEOUT > 300:
            self._add_issue("warning", "performance",
                          "Request timeout is very high, may cause long waits",
                          "request_defaults.TIMEOUT",
                          "Consider reducing to under 60 seconds")
        
        # Retry validation
        if request_defaults.MAX_RETRIES < 0:
            self._add_issue("error", "functionality",
                          "Max retries cannot be negative",
                          "request_defaults.MAX_RETRIES")
        elif request_defaults.MAX_RETRIES > 10:
            self._add_issue("warning", "performance",
                          "Very high retry count may cause excessive delays",
                          "request_defaults.MAX_RETRIES",
                          "Consider reducing to 3-5 retries")
        
        # Retry delay validation
        if request_defaults.RETRY_DELAY < 0:
            self._add_issue("error", "functionality",
                          "Retry delay cannot be negative",
                          "request_defaults.RETRY_DELAY")
        elif request_defaults.RETRY_DELAY > 60:
            self._add_issue("warning", "performance",
                          "Very high retry delay may cause long test durations",
                          "request_defaults.RETRY_DELAY")
        
        # Backoff factor validation
        if request_defaults.BACKOFF_FACTOR < 1:
            self._add_issue("warning", "functionality",
                          "Backoff factor less than 1 will decrease retry delays",
                          "request_defaults.BACKOFF_FACTOR",
                          "Use values >= 1.5 for proper exponential backoff")
        elif request_defaults.BACKOFF_FACTOR > 5:
            self._add_issue("warning", "performance",
                          "Very high backoff factor may cause excessive delays",
                          "request_defaults.BACKOFF_FACTOR")
    
    def _validate_security_defaults(self, security_defaults):
        """Validate security configuration."""
        # Sensitive headers validation
        if not security_defaults.SENSITIVE_HEADERS:
            self._add_issue("warning", "security",
                          "No sensitive headers configured - credentials may be logged",
                          "security_defaults.SENSITIVE_HEADERS",
                          "Add common headers like 'authorization', 'cookie', 'x-api-key'")
        
        # Check for common missing headers
        expected_headers = {'authorization', 'cookie', 'x-api-key', 'x-auth-token'}
        missing_headers = expected_headers - {h.lower() for h in security_defaults.SENSITIVE_HEADERS}
        if missing_headers:
            self._add_issue("info", "security",
                          f"Consider adding common sensitive headers: {', '.join(missing_headers)}",
                          "security_defaults.SENSITIVE_HEADERS")
        
        # Sensitive params validation
        if not security_defaults.SENSITIVE_PARAMS:
            self._add_issue("warning", "security",
                          "No sensitive parameters configured - credentials may be logged",
                          "security_defaults.SENSITIVE_PARAMS",
                          "Add common params like 'password', 'token', 'key', 'secret'")
        
        # Log body size validation
        if security_defaults.MAX_LOG_BODY_SIZE < 0:
            self._add_issue("error", "functionality",
                          "Max log body size cannot be negative",
                          "security_defaults.MAX_LOG_BODY_SIZE")
        elif security_defaults.MAX_LOG_BODY_SIZE > 10240:  # 10KB
            self._add_issue("warning", "performance",
                          "Very large log body size may impact performance",
                          "security_defaults.MAX_LOG_BODY_SIZE",
                          "Consider reducing to 1024-2048 bytes")
        elif security_defaults.MAX_LOG_BODY_SIZE < 100:
            self._add_issue("warning", "functionality",
                          "Very small log body size may truncate important data",
                          "security_defaults.MAX_LOG_BODY_SIZE")
    
    def _validate_logging_defaults(self, logging_defaults):
        """Validate logging configuration."""
        # Log level validation
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if logging_defaults.LOG_LEVEL.upper() not in valid_log_levels:
            self._add_issue("error", "functionality",
                          f"Invalid log level: {logging_defaults.LOG_LEVEL}",
                          "logging_defaults.LOG_LEVEL",
                          f"Use one of: {', '.join(valid_log_levels)}")
        
        # Production logging recommendations
        if logging_defaults.LOG_LEVEL.upper() == "DEBUG":
            self._add_issue("warning", "performance",
                          "DEBUG logging may impact performance in production",
                          "logging_defaults.LOG_LEVEL",
                          "Consider using INFO or WARNING for production")
        
        # Logging feature validation
        if not any([logging_defaults.ENABLE_REQUEST_LOGGING,
                   logging_defaults.ENABLE_RESPONSE_LOGGING,
                   logging_defaults.ENABLE_ERROR_LOGGING]):
            self._add_issue("warning", "functionality",
                          "All logging is disabled - debugging will be difficult",
                          "logging_defaults",
                          "Enable at least error logging")
    
    def _validate_auth_defaults(self, auth_defaults):
        """Validate authentication configuration."""
        # Session timeout validation
        if auth_defaults.SESSION_TIMEOUT < 60:
            self._add_issue("warning", "security",
                          "Very short session timeout may cause frequent re-authentication",
                          "auth_defaults.SESSION_TIMEOUT",
                          "Consider at least 300 seconds (5 minutes)")
        elif auth_defaults.SESSION_TIMEOUT > 86400:  # 24 hours
            self._add_issue("warning", "security",
                          "Very long session timeout may pose security risk",
                          "auth_defaults.SESSION_TIMEOUT",
                          "Consider reducing to 1-8 hours")
        
        # Max sessions validation
        if auth_defaults.MAX_SESSIONS < 1:
            self._add_issue("error", "functionality",
                          "Max sessions must be at least 1",
                          "auth_defaults.MAX_SESSIONS")
        elif auth_defaults.MAX_SESSIONS > 100:
            self._add_issue("warning", "performance",
                          "Very high max sessions may impact memory usage",
                          "auth_defaults.MAX_SESSIONS",
                          "Consider reducing to 10-50 sessions")
        
        # Cleanup interval validation
        if auth_defaults.SESSION_CLEANUP_INTERVAL < 60:
            self._add_issue("warning", "performance",
                          "Very frequent cleanup may impact performance",
                          "auth_defaults.SESSION_CLEANUP_INTERVAL")
        elif auth_defaults.SESSION_CLEANUP_INTERVAL > auth_defaults.SESSION_TIMEOUT:
            self._add_issue("warning", "functionality",
                          "Cleanup interval longer than session timeout may leave stale sessions",
                          "auth_defaults.SESSION_CLEANUP_INTERVAL",
                          "Set cleanup interval to half of session timeout")
    
    def _validate_cross_module_consistency(self, config):
        """Validate consistency across modules."""
        # Request timeout vs auth session timeout
        if config.request_defaults.TIMEOUT > config.auth_defaults.SESSION_TIMEOUT:
            self._add_issue("warning", "functionality",
                          "Request timeout is longer than session timeout",
                          "cross_module",
                          "Ensure session timeout is longer than request timeout")
        
        # Logging and security consistency
        if (config.logging_defaults.ENABLE_REQUEST_LOGGING and 
            not config.security_defaults.SENSITIVE_HEADERS):
            self._add_issue("warning", "security",
                          "Request logging enabled but no sensitive headers configured",
                          "cross_module",
                          "Configure sensitive headers to prevent credential leakage")
    
    def _add_issue(self, level: str, category: str, message: str, field: str, 
                   suggestion: Optional[str] = None):
        """Add a validation issue to the list."""
        self.issues.append(ValidationIssue(
            level=level,
            category=category,
            message=message,
            field=field,
            suggestion=suggestion
        ))
    
    def get_issues_by_level(self, level: str) -> List[ValidationIssue]:
        """Get issues filtered by level."""
        return [issue for issue in self.issues if issue.level == level]
    
    def get_issues_by_category(self, category: str) -> List[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.level == "error" for issue in self.issues)
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of issues by level."""
        summary = {"error": 0, "warning": 0, "info": 0}
        for issue in self.issues:
            summary[issue.level] += 1
        return summary

def validate_config_with_report(config: Config) -> Dict[str, Any]:
    """Validate configuration and return detailed report."""
    validator = ConfigValidator()
    issues = validator.validate_config(config)
    
    return {
        "valid": not validator.has_errors(),
        "summary": validator.get_summary(),
        "issues": [
            {
                "level": issue.level,
                "category": issue.category,
                "message": issue.message,
                "field": issue.field,
                "suggestion": issue.suggestion
            }
            for issue in issues
        ],
        "recommendations": [
            issue.suggestion for issue in issues 
            if issue.suggestion and issue.level in ["error", "warning"]
        ]
    }
