"""
Validation presets for common security testing scenarios.
This module provides pre-configured validation rules for typical exploit detection,
making it easier for users to validate responses without manual configuration.

Enhanced with critical vulnerability detection presets including SSRF, Command Injection, and CSRF.
"""
from typing import Dict, List, Any
from .validator_models import ValidationConfig
from .validator_patterns import VulnerabilityPatterns


class ValidationPresets:
    """Pre-configured validation profiles for common security testing scenarios."""
    
    @staticmethod
    def sql_injection_detection() -> ValidationConfig:
        """Validation preset for SQL injection vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "mysql_fetch_array",
                "mysql_num_rows",
                "ORA-",
                "Microsoft JET Database",
                "ODBC SQL Server",
                "SQLite/JDBCDriver",
                "PostgreSQL query failed",
                "SQL syntax error",
                "quoted string not properly terminated"
            ],
            regex_patterns=VulnerabilityPatterns.SQL_INJECTION,
            status_codes=[500],  # Internal server errors often indicate SQL errors
            confidence_threshold=0.4
        )
    
    @staticmethod
    def xss_detection() -> ValidationConfig:
        """Validation preset for Cross-Site Scripting (XSS) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "<script>",
                "javascript:",
                "onerror=",
                "onload=",
                "onclick=",
                "alert(",
                "document.cookie",
                "window.location"
            ],
            regex_patterns=VulnerabilityPatterns.XSS_INDICATORS,
            confidence_threshold=0.3
        )
    
    @staticmethod
    def directory_traversal_detection() -> ValidationConfig:
        """Validation preset for directory traversal vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "root:x:0:0:",
                "[boot loader]",
                "../",
                "..\\",
                "/etc/passwd",
                "C:\\Windows\\",
                "boot.ini",
                "php.ini"
            ],
            regex_patterns=VulnerabilityPatterns.DIRECTORY_TRAVERSAL,
            confidence_threshold=0.5
        )
    
    @staticmethod
    def ssrf_detection() -> ValidationConfig:
        """Validation preset for Server-Side Request Forgery (SSRF) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "localhost",
                "127.0.0.1",
                "metadata.google",
                "169.254.169.254",
                "metadata.azure",
                "kubernetes.default",
                "consul.service",
                "internal-",
                "admin-",
                "file://",
                "dict://",
                "gopher://"
            ],
            regex_patterns=VulnerabilityPatterns.SSRF_INDICATORS,
            status_codes=[200, 301, 302, 400, 403, 500],
            confidence_threshold=0.6,
            response_time_threshold=5.0  # SSRF often causes delays
        )
    
    @staticmethod
    def command_injection_detection() -> ValidationConfig:
        """Validation preset for Command Injection vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "uid=",
                "gid=",
                "whoami",
                "ipconfig",
                "ifconfig",
                "netstat",
                "ps aux",
                "tasklist",
                "command not found",
                "No such file or directory",
                "/bin/bash",
                "cmd.exe",
                "powershell"
            ],
            regex_patterns=VulnerabilityPatterns.COMMAND_INJECTION,
            status_codes=[200, 500],
            confidence_threshold=0.7
        )
    
    @staticmethod
    def csrf_detection() -> ValidationConfig:
        """Validation preset for CSRF token detection and validation."""
        return ValidationConfig(
            success_criteria=[
                "csrf_token",
                "_token",
                "authenticity_token",
                "csrfmiddlewaretoken",
                "__RequestVerificationToken",
                "form_token",
                "security_token",
                "anti_csrf",
                "state_token",
                "nonce"
            ],
            regex_patterns=VulnerabilityPatterns.CSRF_INDICATORS,
            status_codes=[200, 403, 422],
            confidence_threshold=0.4,
            require_all_success=False
        )
    
    @staticmethod
    def lfi_detection() -> ValidationConfig:
        """Validation preset for Local File Inclusion (LFI) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "Warning: include",
                "Warning: require",
                "failed to open stream",
                "No such file or directory",
                "Permission denied"
            ],
            regex_patterns=VulnerabilityPatterns.LFI_INDICATORS,
            status_codes=[200, 500],
            confidence_threshold=0.5
        )
    
    @staticmethod
    def rfi_detection() -> ValidationConfig:
        """Validation preset for Remote File Inclusion (RFI) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "allow_url_include",
                "allow_url_fopen",
                "Warning: URL file-access",
                "failed to open stream: HTTP",
                "getaddrinfo failed",
                "Connection refused"
            ],
            regex_patterns=VulnerabilityPatterns.RFI_INDICATORS,
            status_codes=[200, 500],
            confidence_threshold=0.6
        )
    
    @staticmethod
    def xxe_detection() -> ValidationConfig:
        """Validation preset for XXE (XML External Entity) vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "<!DOCTYPE",
                "<!ENTITY",
                "ENTITY SYSTEM",
                "xml entity",
                "SimpleXML Entity",
                "libxml entity",
                "Entity not defined"
            ],
            regex_patterns=VulnerabilityPatterns.XXE_INDICATORS,
            status_codes=[200, 400, 500],
            confidence_threshold=0.5
        )
    
    @staticmethod
    def open_redirect_detection() -> ValidationConfig:
        """Validation preset for Open Redirect vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "Location: http",
                "Location: //",
                "window.location",
                "document.location"
            ],
            regex_patterns=VulnerabilityPatterns.OPEN_REDIRECT,
            status_codes=[301, 302, 303, 307, 308],
            confidence_threshold=0.4
        )
    
    @staticmethod
    def timing_attack_detection() -> ValidationConfig:
        """Validation preset for Timing Attack vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "sleep(",
                "benchmark(",
                "waitfor delay",
                "pg_sleep(",
                "dbms_pipe.receive_message",
                "setTimeout(",
                "time.sleep("
            ],
            regex_patterns=VulnerabilityPatterns.TIMING_ATTACK,
            status_codes=[200, 500],
            confidence_threshold=0.6,
            response_time_threshold=2.0  # Look for artificial delays
        )
    
    @staticmethod
    def business_logic_detection() -> ValidationConfig:
        """Validation preset for Business Logic vulnerability detection."""
        return ValidationConfig(
            failure_criteria=[
                "negative price",
                "invalid quantity",
                "insufficient funds",
                "credit limit exceeded",
                "out of stock",
                "inventory error",
                "payment failed",
                "transaction declined",
                "order limit exceeded",
                "discount invalid"
            ],
            regex_patterns=VulnerabilityPatterns.BUSINESS_LOGIC,
            status_codes=[200, 400, 402, 422],
            confidence_threshold=0.5
        )
    
    @staticmethod
    def authentication_bypass() -> ValidationConfig:
        """Validation preset for authentication bypass detection."""
        return ValidationConfig(
            success_criteria=[
                "admin panel",
                "administrator",
                "privileged access",
                "dashboard",
                "control panel",
                "management interface",
                "admin console"
            ],
            failure_criteria=[
                "access denied",
                "unauthorized",
                "login required",
                "authentication failed",
                "insufficient privileges"
            ],
            status_codes=[200, 302],
            confidence_threshold=0.6
        )
    
    @staticmethod
    def information_disclosure() -> ValidationConfig:
        """Validation preset for information disclosure detection."""
        return ValidationConfig(
            failure_criteria=[
                "stack trace",
                "debug information",
                "internal error",
                "version",
                "build number",
                "database error",
                "exception",
                "traceback",
                "Exception at",
                "Traceback most recent",
                "Fatal error in",
                "Warning in line",
                "Notice in line"
            ],
            regex_patterns=VulnerabilityPatterns.INFO_DISCLOSURE,
            confidence_threshold=0.3
        )
    
    @staticmethod
    def api_success_validation() -> ValidationConfig:
        """Validation preset for successful API responses."""
        return ValidationConfig(
            success_criteria=[
                "success",
                "ok",
                "completed",
                "accepted"
            ],
            status_codes=[200, 201, 202, 204],
            headers_criteria={"content-type": "application/json"},
            confidence_threshold=0.4
        )
    
    @staticmethod
    def login_success_validation() -> ValidationConfig:
        """Validation preset for successful login attempts."""
        return ValidationConfig(
            success_criteria=[
                "welcome",
                "dashboard",
                "logged in",
                "authentication successful",
                "login successful"
            ],
            status_codes=[200, 302],
            headers_criteria={"set-cookie": "session"},
            confidence_threshold=0.5
        )
    
    @staticmethod
    def error_page_detection() -> ValidationConfig:
        """Validation preset for error page detection."""
        return ValidationConfig(
            failure_criteria=[
                "404",
                "not found",
                "page not found",
                "error",
                "exception",
                "internal server error"
            ],
            status_codes=[404, 500, 503],
            confidence_threshold=0.3
        )
    
    @staticmethod
    def custom_preset(
        success_patterns: List[str] = None,
        failure_patterns: List[str] = None,
        status_codes: List[int] = None,
        confidence_threshold: float = 0.3
    ) -> ValidationConfig:
        """Create a custom validation preset with specified parameters."""
        return ValidationConfig(
            success_criteria=success_patterns or [],
            failure_criteria=failure_patterns or [],
            status_codes=status_codes or [],
            confidence_threshold=confidence_threshold
        )


# Enhanced convenience dictionary with critical vulnerability presets
VALIDATION_PRESETS = {
    # Core web vulnerabilities
    'sql_injection': ValidationPresets.sql_injection_detection,
    'xss': ValidationPresets.xss_detection,
    'directory_traversal': ValidationPresets.directory_traversal_detection,
    
    # Critical missing presets (FIXED)
    'ssrf': ValidationPresets.ssrf_detection,
    'command_injection': ValidationPresets.command_injection_detection,
    'csrf': ValidationPresets.csrf_detection,
    
    # File inclusion vulnerabilities
    'lfi': ValidationPresets.lfi_detection,
    'rfi': ValidationPresets.rfi_detection,
    
    # Advanced vulnerabilities
    'xxe': ValidationPresets.xxe_detection,
    'open_redirect': ValidationPresets.open_redirect_detection,
    'timing_attack': ValidationPresets.timing_attack_detection,
    
    # Business logic and access control
    'business_logic': ValidationPresets.business_logic_detection,
    'auth_bypass': ValidationPresets.authentication_bypass,
    'info_disclosure': ValidationPresets.information_disclosure,
    
    # Functional validation
    'api_success': ValidationPresets.api_success_validation,
    'login_success': ValidationPresets.login_success_validation,
    'error_page': ValidationPresets.error_page_detection
}


def get_preset(preset_name: str) -> ValidationConfig:
    """
    Get a validation preset by name.
    
    Args:
        preset_name: Name of the preset to retrieve
        
    Returns:
        ValidationConfig object for the specified preset
        
    Raises:
        ValueError: If preset name is not found
    """
    if preset_name not in VALIDATION_PRESETS:
        available = ', '.join(VALIDATION_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available presets: {available}")
    
    return VALIDATION_PRESETS[preset_name]()


def list_critical_presets() -> List[str]:
    """List critical vulnerability detection presets."""
    return [
        'sql_injection', 'xss', 'ssrf', 'command_injection', 
        'csrf', 'lfi', 'rfi', 'xxe', 'auth_bypass'
    ]


def list_all_presets() -> List[str]:
    """List all available validation presets."""
    return list(VALIDATION_PRESETS.keys())
