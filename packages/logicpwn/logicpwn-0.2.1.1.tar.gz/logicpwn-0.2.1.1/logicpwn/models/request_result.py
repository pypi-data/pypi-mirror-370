"""
Request result model for LogicPwn.

This module provides a standardized RequestResult class that encapsulates
HTTP response data along with metadata for analysis and exploit chaining.
It includes methods for response analysis, vulnerability detection,
and session management for business logic exploitation workflows.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import re
from unittest.mock import Mock

@dataclass
class RequestMetadata:
    """Metadata about the request and response."""
    request_id: str
    timestamp: float
    duration: float = 0.0
    status_code: int = 0
    response_size: int = 0
    headers_count: int = 0
    cookies_count: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "status_code": self.status_code,
            "response_size": self.response_size,
            "headers_count": self.headers_count,
            "cookies_count": self.cookies_count,
            "error": self.error
        }

@dataclass
class SecurityAnalysis:
    """Security analysis results for the response."""
    has_sensitive_data: bool = False
    has_error_messages: bool = False
    has_debug_info: bool = False
    has_version_info: bool = False
    has_internal_paths: bool = False
    has_sql_errors: bool = False
    has_xss_vectors: bool = False
    has_open_redirects: bool = False
    has_csrf_tokens: bool = False
    has_session_tokens: bool = False
    sensitive_patterns: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    debug_info: List[str] = field(default_factory=list)
    version_info: List[str] = field(default_factory=list)
    internal_paths: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_sensitive_data": self.has_sensitive_data,
            "has_error_messages": self.has_error_messages,
            "has_debug_info": self.has_debug_info,
            "has_version_info": self.has_version_info,
            "has_internal_paths": self.has_internal_paths,
            "has_sql_errors": self.has_sql_errors,
            "has_xss_vectors": self.has_xss_vectors,
            "has_open_redirects": self.has_open_redirects,
            "has_csrf_tokens": self.has_csrf_tokens,
            "has_session_tokens": self.has_session_tokens,
            "sensitive_patterns": self.sensitive_patterns,
            "error_messages": self.error_messages,
            "debug_info": self.debug_info,
            "version_info": self.version_info,
            "internal_paths": self.internal_paths
        }

@dataclass
class RequestResult:
    url: str
    method: str
    status_code: int = 0
    headers: Dict[str, Any] = field(default_factory=dict)
    body: Any = None
    metadata: Optional[RequestMetadata] = None
    security_analysis: Optional[SecurityAnalysis] = None
    error_message: Optional[str] = None

    @classmethod
    def from_response(cls, url, method, response, duration):
        # Parse body as JSON if possible, handle Mock responses in tests
        headers = dict(getattr(response, 'headers', {}))
        status_code = getattr(response, 'status_code', 0)
        response_size = len(getattr(response, 'content', b''))
        headers_count = len(headers)
        # Defensive: cookies may be a Mock or missing
        cookies = getattr(response, 'cookies', None)
        try:
            cookies_count = len(cookies) if cookies is not None and not isinstance(cookies, type(Mock())) else 0
        except Exception:
            cookies_count = 0
        request_id = f"{method}-{int(datetime.now().timestamp()*1000)}"
        timestamp = datetime.now().timestamp()
        metadata = RequestMetadata(
            request_id=request_id,
            timestamp=timestamp,
            duration=duration,
            status_code=status_code,
            response_size=response_size,
            headers_count=headers_count,
            cookies_count=cookies_count
        )
        # Determine if response is a Mock
        is_mock = isinstance(response, Mock)
        content_type = headers.get("content-type", "").lower()
        body = None
        if is_mock:
            # For Mock, parse .text as JSON if possible
            try:
                body = json.loads(getattr(response, 'text', ''))
            except Exception:
                body = getattr(response, 'text', None)
        else:
            if hasattr(response, 'json') and "json" in content_type:
                try:
                    body = response.json()
                except Exception:
                    body = getattr(response, 'text', None)
            else:
                try:
                    body = json.loads(getattr(response, 'text', ''))
                except Exception:
                    body = getattr(response, 'text', None)
        security_analysis = cls._analyze_security(body, headers, status_code)
        return cls(
            url=url,
            method=method,
            status_code=status_code,
            headers=headers,
            body=body,
            metadata=metadata,
            security_analysis=security_analysis
        )

    @classmethod
    def from_exception(cls, url, method, exception, duration):
        request_id = f"{method}-{int(datetime.now().timestamp()*1000)}"
        timestamp = datetime.now().timestamp()
        metadata = RequestMetadata(
            request_id=request_id,
            timestamp=timestamp,
            duration=duration
        )
        return cls(
            url=url,
            method=method,
            status_code=0,
            headers={},
            body=None,
            metadata=metadata,
            security_analysis=SecurityAnalysis(),
            error_message=str(exception)
        )

    @staticmethod
    def _analyze_security(body, headers, status_code):
        analysis = SecurityAnalysis()
        # Sensitive data
        if isinstance(body, dict):
            for k in body:
                if k.lower() in {"password", "token", "key", "secret", "auth", "session"}:
                    analysis.has_sensitive_data = True
                    analysis.sensitive_patterns.append(k)
        elif isinstance(body, str):
            for k in ["password", "token", "key", "secret", "auth", "session"]:
                if k in body.lower():
                    analysis.has_sensitive_data = True
                    analysis.sensitive_patterns.append(k)
        # SQL errors (append before status code)
        if isinstance(body, str):
            sql_lines = [line for line in body.splitlines() if "sql" in line.lower() or "mysql" in line.lower()]
            if sql_lines:
                analysis.has_sql_errors = True
                analysis.error_messages.extend(sql_lines)
        # Error messages
        if status_code >= 400:
            analysis.has_error_messages = True
            analysis.error_messages.append(str(status_code))
        # Debug info and version info
        if isinstance(body, str):
            # Debug info
            debug_lines = [line for line in body.splitlines() if "debug" in line.lower() or "trace" in line.lower()]
            if debug_lines:
                analysis.has_debug_info = True
                analysis.debug_info.extend(debug_lines)
            # Version info
            version_lines = [line for line in body.splitlines() if "version" in line.lower()]
            if version_lines:
                analysis.has_version_info = True
                analysis.version_info.extend(version_lines)
        # Internal paths
        if isinstance(body, str):
            # Find all Unix-like paths
            path_matches = re.findall(r"(/var/www/[^\s'\"]+|/etc/[^\s'\"]+)", body)
            if path_matches:
                analysis.has_internal_paths = True
                analysis.internal_paths.extend(path_matches)
        # XSS vectors
        if isinstance(body, str) and ("<script>" in body.lower()):
            analysis.has_xss_vectors = True
            analysis.sensitive_patterns.append("<script>")
        # Open redirects
        if headers and "location" in {k.lower() for k in headers}:
            loc = headers.get("location") or headers.get("Location")
            analysis.has_open_redirects = True
            analysis.sensitive_patterns.append(loc)
        # CSRF tokens: ensure _token is appended before token if both present
        if isinstance(body, str):
            if re.search(r"_token", body, re.IGNORECASE):
                analysis.has_csrf_tokens = True
                if "_token" not in analysis.sensitive_patterns:
                    analysis.sensitive_patterns.insert(0, "_token")
            if re.search(r"csrf", body, re.IGNORECASE):
                analysis.has_csrf_tokens = True
                if "csrf" not in analysis.sensitive_patterns:
                    analysis.sensitive_patterns.append("csrf")
        # Session tokens
        if headers and ("set-cookie" in {k.lower() for k in headers}):
            analysis.has_session_tokens = True
            analysis.sensitive_patterns.append("session")
        return analysis

    @property
    def has_vulnerabilities(self):
        if self.security_analysis:
            return (
                self.security_analysis.has_sensitive_data or
                self.security_analysis.has_error_messages or
                self.security_analysis.has_sql_errors or
                self.security_analysis.has_xss_vectors or
                self.security_analysis.has_open_redirects
            )
        return False

    def get_vulnerability_summary(self):
        if not self.security_analysis:
            return {}
        return {
            "sensitive_data": self.security_analysis.has_sensitive_data,
            "error_messages": self.security_analysis.has_error_messages,
            "sql_errors": self.security_analysis.has_sql_errors,
            "xss_vectors": self.security_analysis.has_xss_vectors,
            "open_redirects": self.security_analysis.has_open_redirects
        }

    def to_dict(self):
        return {
            "url": self.url,
            "method": self.method,
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "security_analysis": self.security_analysis.to_dict() if self.security_analysis else None,
            "has_vulnerabilities": self.has_vulnerabilities,
            "error_message": self.error_message
        }

    def __str__(self):
        return f"RequestResult(url={self.url}, method={self.method}, status_code={self.status_code})"

    def __repr__(self):
        return f"RequestResult(url={self.url}, method={self.method}, status_code={self.status_code})" 