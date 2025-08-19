"""
Industry-Standard Response Extraction Utility for LogicPwn

This module provides comprehensive response parsing and data extraction capabilities
for security testing workflows. It supports multiple extraction methods including
regex, HTTP headers, status codes, JSON path queries, and custom extractors.

Author: LogicPwn Team
License: MIT
"""

import re
import json
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class ExtractionMethod(Enum):
    """Supported extraction methods"""
    REGEX = "regex"
    HEADERS = "headers"
    STATUS_CODE = "status_code"
    JSON_PATH = "json_path"
    CUSTOM = "custom"


@dataclass
class ExtractionResult:
    """Result of an extraction operation"""
    method: ExtractionMethod
    pattern: str
    matches: List[Any]
    success: bool
    error: Optional[str] = None
    
    @property
    def first_match(self) -> Optional[Any]:
        """Get the first match if available"""
        return self.matches[0] if self.matches else None


class ResponseExtractor:
    """Main response extraction utility"""
    
    def __init__(self):
        self.custom_extractors: Dict[str, Callable] = {}
    
    def _get_response_text(self, response: Any) -> str:
        """Extract text content from various response types"""
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'content'):
            # Handle bytes content
            content = response.content
            if isinstance(content, bytes):
                return content.decode('utf-8', errors='ignore')
            return str(content)
        elif hasattr(response, 'data'):
            data = response.data
            if isinstance(data, bytes):
                return data.decode('utf-8', errors='ignore')
            return str(data)
        elif isinstance(response, (str, bytes)):
            if isinstance(response, bytes):
                return response.decode('utf-8', errors='ignore')
            return response
        else:
            return str(response)
    
    def _get_headers(self, response: Any) -> Dict[str, str]:
        """Extract headers from various response types"""
        if hasattr(response, 'headers'):
            headers = response.headers
            if hasattr(headers, 'items'):
                return dict(headers.items())
            elif isinstance(headers, dict):
                return headers
        elif hasattr(response, 'info'):
            # For urllib responses
            headers = response.info()
            if hasattr(headers, 'items'):
                return dict(headers.items())
        return {}

    def extract_from_response(
        self, 
        response: Any, 
        pattern: str, 
        method: Union[ExtractionMethod, str] = ExtractionMethod.REGEX,
        **kwargs
    ) -> ExtractionResult:
        """Extract data from response using specified method"""
        try:
            if isinstance(method, str):
                method = ExtractionMethod(method)
            
            if method == ExtractionMethod.REGEX:
                return self._extract_regex(response, pattern, **kwargs)
            elif method == ExtractionMethod.HEADERS:
                return self._extract_headers(response, pattern)
            elif method == ExtractionMethod.STATUS_CODE:
                return self._extract_status_code(response)
            elif method == ExtractionMethod.JSON_PATH:
                return self._extract_json_path(response, pattern, **kwargs)
            elif method == ExtractionMethod.CUSTOM:
                return self._extract_custom(response, pattern, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ExtractionResult(
                method=method if 'method' in locals() else ExtractionMethod.REGEX,
                pattern=pattern,
                matches=[],
                success=False,
                error=str(e)
            )
    
    def _extract_regex(self, response: Any, pattern: str, **kwargs) -> ExtractionResult:
        """Extract using regular expressions"""
        try:
            # Get response text
            response_text = self._get_response_text(response)
            
            # Compile regex with flags
            flags = kwargs.get('flags', 0)
            if kwargs.get('case_insensitive', False):
                flags |= re.IGNORECASE
            if kwargs.get('multiline', False):
                flags |= re.MULTILINE | re.DOTALL
            
            compiled_pattern = re.compile(pattern, flags)
            
            # Extract matches
            matches = compiled_pattern.findall(response_text)
            
            return ExtractionResult(
                method=ExtractionMethod.REGEX,
                pattern=pattern,
                matches=matches,
                success=len(matches) > 0
            )
            
        except Exception as e:
            return ExtractionResult(
                method=ExtractionMethod.REGEX,
                pattern=pattern,
                matches=[],
                success=False,
                error=str(e)
            )
    
    def _extract_headers(self, response: Any, pattern: str) -> ExtractionResult:
        """Extract HTTP headers"""
        try:
            headers = self._get_headers(response)
            matches = []
            pattern_lower = pattern.lower()
            
            for header_name, header_value in headers.items():
                if header_name.lower() == pattern_lower:
                    matches.append(header_value)
            
            return ExtractionResult(
                method=ExtractionMethod.HEADERS,
                pattern=pattern,
                matches=matches,
                success=len(matches) > 0
            )
            
        except Exception as e:
            return ExtractionResult(
                method=ExtractionMethod.HEADERS,
                pattern=pattern,
                matches=[],
                success=False,
                error=str(e)
            )
    
    def _extract_status_code(self, response: Any) -> ExtractionResult:
        """Extract status code from response"""
        try:
            if hasattr(response, 'status_code'):
                status_code = response.status_code
            elif hasattr(response, 'status'):
                status_code = response.status
            else:
                status_code = None
            
            return ExtractionResult(
                method=ExtractionMethod.STATUS_CODE,
                pattern="status_code",
                matches=[status_code] if status_code is not None else [],
                success=status_code is not None
            )
        except Exception as e:
            return ExtractionResult(
                method=ExtractionMethod.STATUS_CODE,
                pattern="status_code",
                matches=[],
                success=False,
                error=str(e)
            )
    
    def _extract_json_path(self, response: Any, pattern: str, **kwargs) -> ExtractionResult:
        """Extract using JSON path"""
        try:
            # Get response text and parse as JSON
            response_text = self._get_response_text(response)
            
            try:
                json_data = json.loads(response_text)
            except json.JSONDecodeError:
                return ExtractionResult(
                    method=ExtractionMethod.JSON_PATH,
                    pattern=pattern,
                    matches=[],
                    success=False,
                    error="Invalid JSON response"
                )
            
            # Simple JSON path extraction (supports dot notation)
            matches = []
            keys = pattern.split('.')
            current = json_data
            
            try:
                for key in keys:
                    if isinstance(current, dict):
                        current = current.get(key)
                    elif isinstance(current, list) and key.isdigit():
                        current = current[int(key)]
                    else:
                        current = None
                        break
                
                if current is not None:
                    matches = [current] if not isinstance(current, list) else current
            except (KeyError, IndexError, TypeError):
                pass
            
            return ExtractionResult(
                method=ExtractionMethod.JSON_PATH,
                pattern=pattern,
                matches=matches,
                success=len(matches) > 0
            )
            
        except Exception as e:
            return ExtractionResult(
                method=ExtractionMethod.JSON_PATH,
                pattern=pattern,
                matches=[],
                success=False,
                error=str(e)
            )

    def _extract_custom(self, response: Any, pattern: str, **kwargs) -> ExtractionResult:
        """Extract using custom extractor"""
        try:
            extractor_name = kwargs.get('extractor_name', pattern)
            
            if extractor_name not in self.custom_extractors:
                return ExtractionResult(
                    method=ExtractionMethod.CUSTOM,
                    pattern=pattern,
                    matches=[],
                    success=False,
                    error=f"Custom extractor '{extractor_name}' not found"
                )
            
            extractor_func = self.custom_extractors[extractor_name]
            matches = extractor_func(response, **kwargs)
            
            # Ensure matches is a list
            if not isinstance(matches, list):
                matches = [matches] if matches is not None else []
            
            return ExtractionResult(
                method=ExtractionMethod.CUSTOM,
                pattern=pattern,
                matches=matches,
                success=len(matches) > 0
            )
            
        except Exception as e:
            return ExtractionResult(
                method=ExtractionMethod.CUSTOM,
                pattern=pattern,
                matches=[],
                success=False,
                error=str(e)
            )

    def register_custom_extractor(self, name: str, extractor_func: Callable) -> None:
        """Register a custom extractor function"""
        self.custom_extractors[name] = extractor_func

    def unregister_custom_extractor(self, name: str) -> bool:
        """Unregister a custom extractor function"""
        if name in self.custom_extractors:
            del self.custom_extractors[name]
            return True
        return False


# Global instance for easy access
response_extractor = ResponseExtractor()


# Convenience functions
def extract_from_response(
    response: Any, 
    pattern: str, 
    method: Union[ExtractionMethod, str] = ExtractionMethod.REGEX,
    **kwargs
) -> List[Any]:
    """
    Convenience function for extracting data from response
    
    Returns:
        List of matches (for backward compatibility)
    """
    result = response_extractor.extract_from_response(response, pattern, method, **kwargs)
    return result.matches


def extract_csrf_token(response: Any, patterns: List[str]) -> Optional[str]:
    """
    Convenience function for extracting CSRF tokens using multiple patterns
    
    Args:
        response: The response object to extract from
        patterns: List of regex patterns to try for CSRF token extraction
    
    Returns:
        First CSRF token found or None
    """
    for pattern in patterns:
        result = response_extractor.extract_from_response(response, pattern, ExtractionMethod.REGEX)
        if result.success and result.matches:
            return result.first_match
    
    return None


def extract_session_id(response: Any) -> Optional[str]:
    """
    Convenience function for extracting session IDs
    
    Returns:
        First session ID found or None
    """
    # Try headers first
    header_result = response_extractor.extract_from_response(response, "Set-Cookie", ExtractionMethod.HEADERS)
    if header_result.success:
        for cookie in header_result.matches:
            # Extract session ID from various cookie formats
            session_patterns = [
                r'PHPSESSID=([^;]+)',
                r'JSESSIONID=([^;]+)',
                r'SESSIONID=([^;]+)',
                r'session_id=([^;]+)',
                r'sid=([^;]+)'
            ]
            
            for pattern in session_patterns:
                match = re.search(pattern, cookie, re.IGNORECASE)
                if match:
                    return match.group(1)
    
    # Try response body patterns
    patterns = [
        r'session_id[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
        r'sessionId[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
        r'PHPSESSID[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in patterns:
        result = response_extractor.extract_from_response(response, pattern, ExtractionMethod.REGEX)
        if result.success and result.matches:
            return result.first_match
    
    return None


def extract_json_value(response: Any, json_path: str) -> Optional[Any]:
    """
    Convenience function for extracting JSON values using dot notation
    
    Args:
        response: The response object to extract from
        json_path: JSON path using dot notation (e.g., 'data.user.id')
    
    Returns:
        First JSON value found or None
    """
    result = response_extractor.extract_from_response(response, json_path, ExtractionMethod.JSON_PATH)
    return result.first_match


def extract_header_value(response: Any, header_name: str) -> Optional[str]:
    """
    Convenience function for extracting specific header values
    
    Args:
        response: The response object to extract from
        header_name: Name of the header to extract
    
    Returns:
        Header value or None
    """
    result = response_extractor.extract_from_response(response, header_name, ExtractionMethod.HEADERS)
    return result.first_match


def extract_all_links(response: Any) -> List[str]:
    """
    Convenience function for extracting all links from response
    
    Args:
        response: The response object to extract from
    
    Returns:
        List of URLs found in the response
    """
    link_patterns = [
        r'href=[\'"]([^\'"]+)[\'"]',
        r'src=[\'"]([^\'"]+)[\'"]',
        r'action=[\'"]([^\'"]+)[\'"]',
        r'https?://[^\s<>"\']+',
    ]
    
    all_links = []
    for pattern in link_patterns:
        result = response_extractor.extract_from_response(response, pattern, ExtractionMethod.REGEX)
        if result.success:
            all_links.extend(result.matches)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_links))


def extract_form_inputs(response: Any) -> List[Dict[str, str]]:
    """
    Convenience function for extracting form input fields
    
    Args:
        response: The response object to extract from
    
    Returns:
        List of dictionaries containing input field information
    """
    input_pattern = r'<input[^>]*name=[\'"]([^\'"]+)[\'"][^>]*(?:value=[\'"]([^\'"]*)[\'"])?[^>]*/?>'
    result = response_extractor.extract_from_response(response, input_pattern, ExtractionMethod.REGEX)
    
    inputs = []
    if result.success:
        for match in result.matches:
            if isinstance(match, tuple):
                name, value = match if len(match) >= 2 else (match[0], '')
                inputs.append({'name': name, 'value': value or ''})
            else:
                inputs.append({'name': str(match), 'value': ''})
    
    return inputs
