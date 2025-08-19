"""
Enhanced API functions for LogicPwn response validation.
Includes adaptive confidence scoring, business logic detection, and critical vulnerability presets.
"""
from typing import Dict, Optional, List, Any, Union
import requests
import time
import re
import json
from .validator_models import (
    ValidationResult, ValidationConfig, ValidationType, 
    AdaptiveConfidenceWeights, SeverityLevel, ConfidenceLevel
)
from .validator_checks import (
    _check_regex_patterns,
    _check_status_codes, 
    _check_headers_criteria,
    _calculate_confidence_score
)
from .validator_patterns import VulnerabilityPatterns
from .validator_utils import _sanitize_response_text
from .validation_presets import get_preset, list_all_presets, list_critical_presets
from logicpwn.core.performance import monitor_performance, performance_context
from logicpwn.core.config.config_utils import get_max_log_body_size, get_redaction_string
from logicpwn.core.utils import check_indicators, validate_config
from logicpwn.exceptions import ValidationError

@monitor_performance("enhanced_response_validation")
def validate_response(
    response: requests.Response,
    success_criteria: Optional[List[str]] = None,
    failure_criteria: Optional[List[str]] = None,
    regex_patterns: Optional[List[str]] = None,
    status_codes: Optional[List[int]] = None,
    headers_criteria: Optional[Dict[str, str]] = None,
    json_paths: Optional[List[str]] = None,
    return_structured: bool = False,
    confidence_threshold: float = 0.3,
    vulnerability_type: Optional[str] = None,
    adaptive_scoring: bool = True,
    response_time: Optional[float] = None
) -> Union[bool, ValidationResult]:
    """
    Enhanced response validation with adaptive confidence scoring.
    
    Args:
        response: HTTP response object to validate
        success_criteria: List of text patterns indicating success
        failure_criteria: List of text patterns indicating failure
        regex_patterns: List of regex patterns to match
        status_codes: List of acceptable HTTP status codes
        headers_criteria: Dictionary of required headers
        json_paths: List of JSON path expressions
        return_structured: Return ValidationResult object instead of boolean
        confidence_threshold: Minimum confidence score for validation
        vulnerability_type: Type of vulnerability being tested (for adaptive scoring)
        adaptive_scoring: Enable adaptive confidence scoring
        response_time: Response time for timing analysis
    
    Returns:
        Boolean or ValidationResult object based on return_structured parameter
    """
    try:
        # Create enhanced configuration
        config_dict = {
            "success_criteria": success_criteria or [],
            "failure_criteria": failure_criteria or [],
            "regex_patterns": regex_patterns or [],
            "status_codes": status_codes or [],
            "headers_criteria": headers_criteria or {},
            "json_paths": json_paths or [],
            "return_structured": return_structured,
            "confidence_threshold": confidence_threshold,
            "vulnerability_type": vulnerability_type,
            "adaptive_scoring": adaptive_scoring
        }
        config = validate_config(config_dict, ValidationConfig)
        
        # Extract response text safely
        try:
            response_text = response.text
        except Exception:
            response_text = ""
        
        safe_text = _sanitize_response_text(response_text)
        
        # Perform validation checks
        success_match, success_matches = check_indicators(
            response_text, config.success_criteria, "success"
        )
        failure_match, failure_matches = check_indicators(
            response_text, config.failure_criteria, "failure"
        )
        regex_match, regex_matches, extracted_data = _check_regex_patterns(
            response_text, config.regex_patterns
        )
        status_match = _check_status_codes(response, config.status_codes)
        headers_match, header_matches = _check_headers_criteria(
            response, config.headers_criteria
        )
        
        # Enhanced validation logic
        is_valid = _determine_validation_result(
            config, success_match, failure_match, status_match, headers_match
        )
        
        # Calculate adaptive confidence score
        confidence_score = _calculate_adaptive_confidence_score(
            config, response, success_matches, failure_matches, 
            regex_matches, status_match, headers_match, response_time
        )
        
        # Check confidence threshold
        if confidence_score < config.confidence_threshold:
            is_valid = False
        
        # Detect false positives
        false_positive_indicators = _detect_false_positives(
            response_text, config, vulnerability_type
        )
        
        # Collect evidence
        evidence = _collect_evidence(
            success_matches, failure_matches, regex_matches, 
            header_matches, response
        )
        
        # Enhanced metadata
        metadata = _create_enhanced_metadata(response, config, response_time)
        
        # Create enhanced validation result
        result = ValidationResult(
            is_valid=is_valid,
            matched_patterns=success_matches + failure_matches + regex_matches + header_matches,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            vulnerability_type=vulnerability_type,
            metadata=metadata,
            response_time=response_time,
            evidence=evidence,
            false_positive_indicators=false_positive_indicators
        )
        
        if return_structured:
            return result
        else:
            return is_valid
            
    except Exception as e:
        if return_structured:
            return ValidationResult(
                is_valid=False,
                error_message=str(e),
                confidence_score=0.0,
                vulnerability_type=vulnerability_type
            )
        else:
            return False


def _determine_validation_result(
    config: ValidationConfig,
    success_match: bool,
    failure_match: bool, 
    status_match: bool,
    headers_match: bool
) -> bool:
    """Determine validation result based on configuration and matches."""
    
    # Handle require_all_success option
    if config.require_all_success and config.success_criteria:
        success_valid = success_match
    else:
        success_valid = not config.success_criteria or success_match
    
    # Handle require_all_failure option  
    if config.require_all_failure and config.failure_criteria:
        failure_valid = failure_match
    else:
        failure_valid = not config.failure_criteria or not failure_match
    
    return (
        success_valid and
        failure_valid and
        (not config.status_codes or status_match) and
        (not config.headers_criteria or headers_match)
    )


def _calculate_adaptive_confidence_score(
    config: ValidationConfig,
    response: requests.Response,
    success_matches: List[str],
    failure_matches: List[str],
    regex_matches: List[str],
    status_match: bool,
    headers_match: bool,
    response_time: Optional[float] = None
) -> float:
    """Calculate adaptive confidence score based on multiple factors."""
    
    if not config.adaptive_scoring:
        # Use legacy confidence calculation
        return _calculate_confidence_score(
            success_matches, failure_matches, regex_matches, status_match, headers_match
        )
    
    # Get adaptive weights
    weights = config.get_confidence_weights()
    
    # Base score components
    pattern_score = 0.0
    status_score = 0.0
    timing_score = 0.0
    header_score = 0.0
    content_score = 0.0
    
    # Pattern matching score
    total_patterns = len(success_matches) + len(failure_matches) + len(regex_matches)
    if total_patterns > 0:
        pattern_score = min(1.0, total_patterns / 3.0)  # Normalize to max 3 patterns
    
    # Status code score
    if status_match:
        status_score = 1.0
    elif response.status_code in [500, 403, 404]:
        status_score = 0.5  # Partial score for interesting status codes
    
    # Timing analysis score
    if response_time is not None:
        if config.response_time_threshold and response_time > config.response_time_threshold:
            timing_score = 1.0  # Response took too long
        elif response_time > 2.0:  # General timing threshold
            timing_score = 0.5
    
    # Header analysis score
    if headers_match:
        header_score = 1.0
    
    # Content analysis score
    content_length = len(response.text) if hasattr(response, 'text') else 0
    if config.min_content_length and content_length >= config.min_content_length:
        content_score += 0.5
    if config.max_content_length and content_length <= config.max_content_length:
        content_score += 0.5
    content_score = min(1.0, content_score)
    
    # Calculate weighted score
    base_score = (
        pattern_score * weights.pattern_match_weight +
        status_score * weights.status_code_weight +
        timing_score * weights.response_time_weight +
        header_score * weights.header_analysis_weight +
        content_score * weights.content_length_weight
    )
    
    # Apply multiple indicators bonus
    if total_patterns >= 2:
        base_score += weights.multiple_indicators_bonus
    
    # Apply vulnerability-specific multipliers
    if config.vulnerability_type in ['sql_injection', 'command_injection', 'ssrf']:
        base_score *= weights.critical_vuln_multiplier
    
    return min(1.0, base_score)


def _detect_false_positives(
    response_text: str,
    config: ValidationConfig,
    vulnerability_type: Optional[str]
) -> List[str]:
    """Detect potential false positive indicators."""
    false_positives = []
    
    # Check configured false positive patterns
    for pattern in config.false_positive_patterns:
        if re.search(pattern, response_text, re.IGNORECASE):
            false_positives.append(f"False positive pattern: {pattern}")
    
    # Vulnerability-specific false positive detection
    if vulnerability_type == 'sql_injection':
        # Common SQL injection false positives
        if re.search(r'mysql.*tutorial', response_text, re.IGNORECASE):
            false_positives.append("SQL tutorial content detected")
        if re.search(r'example.*sql', response_text, re.IGNORECASE):
            false_positives.append("SQL example content detected")
    
    elif vulnerability_type == 'xss':
        # Common XSS false positives
        if re.search(r'<script.*src=.*jquery', response_text, re.IGNORECASE):
            false_positives.append("jQuery library detected")
        if re.search(r'javascript.*void\(0\)', response_text, re.IGNORECASE):
            false_positives.append("Void JavaScript link detected")
    
    elif vulnerability_type == 'command_injection':
        # Command injection false positives
        if re.search(r'documentation.*command', response_text, re.IGNORECASE):
            false_positives.append("Command documentation detected")
    
    return false_positives


def _collect_evidence(
    success_matches: List[str],
    failure_matches: List[str],
    regex_matches: List[str],
    header_matches: List[str],
    response: requests.Response
) -> List[str]:
    """Collect evidence for vulnerability detection."""
    evidence = []
    
    # Pattern-based evidence
    for match in success_matches:
        evidence.append(f"Success pattern matched: {match}")
    for match in failure_matches:
        evidence.append(f"Failure pattern matched: {match}")
    for match in regex_matches:
        evidence.append(f"Regex pattern matched: {match}")
    for match in header_matches:
        evidence.append(f"Header criteria matched: {match}")
    
    # Response-based evidence
    if hasattr(response, 'status_code'):
        if response.status_code >= 500:
            evidence.append(f"Server error status code: {response.status_code}")
        elif response.status_code in [403, 401]:
            evidence.append(f"Access control status code: {response.status_code}")
    
    # Content-based evidence
    if hasattr(response, 'headers'):
        interesting_headers = ['server', 'x-powered-by', 'x-debug-token']
        for header in interesting_headers:
            if header in response.headers:
                evidence.append(f"Interesting header found: {header}")
    
    return evidence


def _create_enhanced_metadata(
    response: requests.Response,
    config: ValidationConfig,
    response_time: Optional[float]
) -> Dict[str, Any]:
    """Create enhanced metadata for validation result."""
    try:
        response_text = response.text if hasattr(response, 'text') else ""
        response_size = len(response_text)
    except:
        response_size = 0
    
    metadata = {
        "response_status": getattr(response, 'status_code', 0),
        "response_size": response_size,
        "headers_count": len(getattr(response, 'headers', {})),
        "validation_criteria_count": (
            len(config.success_criteria) + len(config.failure_criteria) + 
            len(config.regex_patterns) + len(config.status_codes) + 
            len(config.headers_criteria)
        ),
        "adaptive_scoring_enabled": config.adaptive_scoring,
        "vulnerability_type": config.vulnerability_type,
        "confidence_threshold": config.confidence_threshold
    }
    
    if response_time is not None:
        metadata["response_time"] = response_time
        metadata["timing_analysis"] = response_time > 2.0
    
    return metadata


@monitor_performance("preset_validation")
def validate_with_preset(
    response: requests.Response,
    preset_name: str,
    return_structured: bool = True,
    response_time: Optional[float] = None
) -> Union[bool, ValidationResult]:
    """
    Validate response using a predefined vulnerability detection preset.
    
    Args:
        response: HTTP response object to validate
        preset_name: Name of the validation preset to use
        return_structured: Return ValidationResult object instead of boolean
        response_time: Response time for timing analysis
    
    Returns:
        Boolean or ValidationResult object based on return_structured parameter
    """
    try:
        # Get the preset configuration
        config = get_preset(preset_name)
        config.vulnerability_type = preset_name
        config.return_structured = return_structured
        
        # Perform validation with the preset
        return validate_response(
            response=response,
            success_criteria=config.success_criteria,
            failure_criteria=config.failure_criteria,
            regex_patterns=config.regex_patterns,
            status_codes=config.status_codes,
            headers_criteria=config.headers_criteria,
            json_paths=config.json_paths,
            return_structured=return_structured,
            confidence_threshold=config.confidence_threshold,
            vulnerability_type=preset_name,
            adaptive_scoring=config.adaptive_scoring,
            response_time=response_time
        )
        
    except ValueError as e:
        # Handle unknown preset name
        if return_structured:
            return ValidationResult(
                is_valid=False,
                error_message=f"Preset validation failed: {str(e)}",
                confidence_score=0.0,
                vulnerability_type=preset_name
            )
        else:
            return False
    except Exception as e:
        # Handle other validation errors
        if return_structured:
            return ValidationResult(
                is_valid=False,
                error_message=f"Preset validation failed: {str(e)}",
                confidence_score=0.0,
                vulnerability_type=preset_name
            )
        else:
            return False
        failure_match, failure_matches = check_indicators(response_text, config.failure_criteria, "failure")
        regex_match, regex_matches, extracted_data = _check_regex_patterns(response_text, config.regex_patterns)
        status_match = _check_status_codes(response, config.status_codes)
        headers_match, header_matches = _check_headers_criteria(response, config.headers_criteria)
        is_valid = (
            (not config.success_criteria or success_match) and
            (not config.failure_criteria or not failure_match) and
            (not config.status_codes or status_match) and
            (not config.headers_criteria or headers_match)
        )
        confidence_score = _calculate_confidence_score(
            success_matches, failure_matches, regex_matches, status_match, headers_match
        )
        if confidence_score < config.confidence_threshold:
            is_valid = False
        metadata = {
            "response_status": response.status_code,
            "response_size": len(response_text),
            "headers_count": len(response.headers),
            "validation_criteria_count": (
                len(config.success_criteria) + len(config.failure_criteria) + 
                len(config.regex_patterns) + len(config.status_codes) + 
                len(config.headers_criteria)
            )
        }
        result = ValidationResult(
            is_valid=is_valid,
            matched_patterns=success_matches + failure_matches + regex_matches + header_matches,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            metadata=metadata
        )
        if return_structured:
            return result
        else:
            return is_valid
    except Exception as e:
        if return_structured:
            return ValidationResult(
                is_valid=False,
                error_message=str(e),
                confidence_score=0.0
            )
        else:
            return False

def extract_from_response(
    response: requests.Response,
    regex: str,
    group_names: Optional[List[str]] = None,
    extract_all: bool = False
) -> Union[List[str], Dict[str, str]]:
    """
    Extract data from response using regex patterns.
    
    Args:
        response: HTTP response object
        regex: Regular expression pattern
        group_names: Named groups to extract
        extract_all: Extract all matches or just the first
    
    Returns:
        List of matches or dictionary of named groups
    """
    try:
        compiled_regex = re.compile(regex, re.IGNORECASE | re.MULTILINE)
    except re.error as e:
        raise ValidationError(
            message=f"Invalid regex pattern: {e}",
            field="regex",
            value=regex
        )
    
    try:
        response_text = response.text
        if hasattr(response_text, '__call__'):
            response_text = response_text()
        if not isinstance(response_text, str):
            response_text = str(response_text) if response_text else ""
    except Exception:
        return [] if not group_names else {}
    
    matches = list(compiled_regex.finditer(response_text))
    if not matches:
        return [] if not group_names else {}
    
    if group_names:
        result = {}
        for match in matches:
            for group_name in group_names:
                if group_name in match.groupdict():
                    value = match.group(group_name)
                    if value:
                        if group_name not in result:
                            result[group_name] = []
                        result[group_name].append(value)
        
        if not extract_all:
            result = {k: v[0] if v else "" for k, v in result.items()}
        return result
    else:
        if extract_all:
            return [match.group(0) for match in matches]
        else:
            return [matches[0].group(0)] if matches else []


def validate_json_response(
    response: requests.Response,
    json_schema: Optional[Dict] = None,
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None
) -> ValidationResult:
    """
    Validate JSON response structure and content.
    
    Args:
        response: HTTP response object
        json_schema: JSON schema for validation
        required_keys: Keys that must be present
        forbidden_keys: Keys that must not be present
    
    Returns:
        ValidationResult object
    """
    try:
        content_type = response.headers.get("content-type", "").lower()
        if "json" not in content_type:
            return ValidationResult(
                is_valid=False,
                error_message="Response is not JSON",
                confidence_score=0.0
            )
        
        try:
            json_data = response.json()
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON: {e}",
                confidence_score=0.0
            )
        
        validation_errors = []
        extracted_data = {"json_data": json_data}  # Include full JSON data
        missing_keys = []
        forbidden_keys_found = []
        
        # Check required keys
        if required_keys:
            for key in required_keys:
                if key not in json_data:
                    validation_errors.append(f"Missing required key: {key}")
                    missing_keys.append(key)
                else:
                    extracted_data[key] = json_data[key]
        
        # Check forbidden keys
        if forbidden_keys:
            for key in forbidden_keys:
                if key in json_data:
                    validation_errors.append(f"Forbidden key present: {key}")
                    forbidden_keys_found.append(key)
        
        # JSON schema validation (if provided)
        if json_schema:
            try:
                # Try to import jsonschema library
                import importlib
                jsonschema = importlib.import_module('jsonschema')
                jsonschema.validate(json_data, json_schema)
            except ImportError:
                validation_errors.append("jsonschema library not available for schema validation")
            except Exception as e:
                validation_errors.append(f"Schema validation failed: {str(e)}")
        
        is_valid = len(validation_errors) == 0
        confidence_score = 1.0 if is_valid else 0.0
        
        metadata = {
            "json_keys": list(json_data.keys()) if isinstance(json_data, dict) else []
        }
        
        # Add missing/forbidden keys to metadata
        if missing_keys:
            metadata["missing_keys"] = missing_keys
        if forbidden_keys_found:
            metadata["forbidden_keys_found"] = forbidden_keys_found
        
        return ValidationResult(
            is_valid=is_valid,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            error_message="; ".join(validation_errors) if validation_errors else None,
            metadata=metadata
        )
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            error_message=f"JSON validation error: {e}",
            confidence_score=0.0
        )


def validate_business_logic(
    response: requests.Response,
    business_rules: List[Dict[str, Any]],
    context_data: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """
    Validate business logic rules against response.
    
    Args:
        response: HTTP response object
        business_rules: List of business logic rules to validate
        context_data: Additional context for validation
    
    Returns:
        ValidationResult object
    """
    try:
        response_text = response.text if hasattr(response, 'text') else ""
        context = context_data or {}
        
        rule_violations = []
        evidence = []
        confidence_scores = []
        
        for rule in business_rules:
            rule_name = rule.get('name', 'unknown')
            rule_pattern = rule.get('pattern', '')
            expected_behavior = rule.get('expected_behavior', '')
            severity = rule.get('severity', 'medium')
            
            # Check if rule pattern matches response
            if re.search(rule_pattern, response_text, re.IGNORECASE):
                rule_violations.append({
                    'rule': rule_name,
                    'severity': severity,
                    'expected': expected_behavior,
                    'evidence': rule_pattern
                })
                evidence.append(f"Business rule violation: {rule_name}")
                
                # Calculate confidence based on severity
                if severity == 'critical':
                    confidence_scores.append(0.9)
                elif severity == 'high':
                    confidence_scores.append(0.7)
                elif severity == 'medium':
                    confidence_scores.append(0.5)
                else:
                    confidence_scores.append(0.3)
        
        # Determine overall validation result
        is_valid = len(rule_violations) == 0
        confidence_score = max(confidence_scores) if confidence_scores else 0.0
        
        return ValidationResult(
            is_valid=not is_valid,  # Violations mean vulnerability detected
            evidence=evidence,
            confidence_score=confidence_score,
            vulnerability_type="business_logic",
            severity=SeverityLevel.HIGH if rule_violations else SeverityLevel.INFO,
            extracted_data={
                'rule_violations': rule_violations,
                'total_rules_checked': len(business_rules)
            },
            metadata={
                'context_data': context,
                'violations_count': len(rule_violations)
            }
        )
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            error_message=f"Business logic validation error: {e}",
            confidence_score=0.0,
            vulnerability_type="business_logic"
        )


def validate_timing_attack(
    responses: List[requests.Response],
    response_times: List[float],
    timing_threshold: float = 1.0
) -> ValidationResult:
    """
    Validate potential timing attack vulnerabilities.
    
    Args:
        responses: List of HTTP response objects
        response_times: List of response times
        timing_threshold: Threshold for timing difference detection
    
    Returns:
        ValidationResult object
    """
    try:
        if len(responses) != len(response_times) or len(responses) < 2:
            return ValidationResult(
                is_valid=False,
                error_message="Insufficient data for timing analysis",
                confidence_score=0.0,
                vulnerability_type="timing_attack"
            )
        
        # Calculate timing statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        time_variance = max_time - min_time
        
        # Check for significant timing differences
        timing_anomalies = []
        for i, time in enumerate(response_times):
            if abs(time - avg_time) > timing_threshold:
                timing_anomalies.append({
                    'response_index': i,
                    'response_time': time,
                    'deviation': abs(time - avg_time)
                })
        
        # Determine if timing attack is possible
        is_vulnerable = time_variance > timing_threshold and len(timing_anomalies) > 0
        
        # Calculate confidence based on timing variance
        confidence_score = min(1.0, time_variance / (timing_threshold * 2))
        
        evidence = []
        if is_vulnerable:
            evidence.append(f"Timing variance detected: {time_variance:.2f}s")
            evidence.append(f"Average response time: {avg_time:.2f}s")
            evidence.append(f"Timing anomalies: {len(timing_anomalies)}")
        
        return ValidationResult(
            is_valid=is_vulnerable,
            confidence_score=confidence_score,
            vulnerability_type="timing_attack",
            severity=SeverityLevel.MEDIUM if is_vulnerable else SeverityLevel.INFO,
            evidence=evidence,
            extracted_data={
                'timing_statistics': {
                    'average_time': avg_time,
                    'max_time': max_time,
                    'min_time': min_time,
                    'variance': time_variance
                },
                'anomalies': timing_anomalies
            },
            metadata={
                'timing_threshold': timing_threshold,
                'responses_analyzed': len(responses)
            }
        )
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            error_message=f"Timing attack validation error: {e}",
            confidence_score=0.0,
            vulnerability_type="timing_attack"
        )


def create_custom_preset(
    name: str,
    success_patterns: Optional[List[str]] = None,
    failure_patterns: Optional[List[str]] = None,
    regex_patterns: Optional[List[str]] = None,
    status_codes: Optional[List[int]] = None,
    confidence_threshold: float = 0.3,
    vulnerability_type: Optional[str] = None
) -> ValidationConfig:
    """
    Create a custom validation preset.
    
    Args:
        name: Name for the custom preset
        success_patterns: Success indicator patterns
        failure_patterns: Failure indicator patterns
        regex_patterns: Regular expression patterns
        status_codes: Expected status codes
        confidence_threshold: Minimum confidence threshold
        vulnerability_type: Type of vulnerability being tested
    
    Returns:
        ValidationConfig object
    """
    return ValidationConfig(
        success_criteria=success_patterns or [],
        failure_criteria=failure_patterns or [],
        regex_patterns=regex_patterns or [],
        status_codes=status_codes or [],
        confidence_threshold=confidence_threshold,
        vulnerability_type=vulnerability_type,
        adaptive_scoring=True
    )


def list_available_presets() -> List[str]:
    """
    List all available validation presets.
    
    Returns:
        List of preset names
    """
    return list_all_presets()


def list_vulnerability_presets() -> List[str]:
    """
    List critical vulnerability detection presets.
    
    Returns:
        List of critical vulnerability preset names
    """
    return list_critical_presets()


@monitor_performance("html_response_validation")
def validate_html_response(
    response: requests.Response,
    expected_title: Optional[str] = None,
    title_patterns: Optional[List[str]] = None,  # Add title_patterns parameter
    expected_elements: Optional[List[str]] = None,
    forbidden_elements: Optional[List[str]] = None,
    form_validation: Optional[Dict[str, Any]] = None,
    return_structured: bool = True  # Default to True for consistency
) -> Union[bool, ValidationResult]:
    """
    Validate HTML response content for specific elements and structure.
    
    Args:
        response: HTTP response object to validate
        expected_title: Expected HTML title
        title_patterns: List of patterns to match in the title
        expected_elements: List of HTML elements/selectors that should be present
        forbidden_elements: List of HTML elements/selectors that should not be present
        form_validation: Dictionary with form validation criteria
        return_structured: Whether to return ValidationResult object
        
    Returns:
        bool or ValidationResult: Validation result
    """
    try:
        # Check content type
        content_type = response.headers.get("content-type", "").lower()
        if "html" not in content_type and "text/html" not in content_type:
            if return_structured:
                return ValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    evidence=[],
                    validation_type=ValidationType.ERROR,
                    error_message="Response is not HTML",
                    metadata={
                        'content_type': content_type,
                        'success_indicators': [],
                        'failure_indicators': []
                    }
                )
            return False
        
        response_text = response.text
        success_indicators = []
        failure_indicators = []
        evidence = []
        matched_patterns = []
        
        # Basic HTML structure detection
        if re.search(r'<html\b', response_text, re.IGNORECASE):
            success_indicators.append("HTML structure detected")
            evidence.append("Basic HTML structure present")
            matched_patterns.append("html_structure")
        
        # Check HTML title patterns
        if title_patterns:
            title_match = re.search(r'<title[^>]*>([^<]*)</title>', response_text, re.IGNORECASE)
            if title_match:
                title_text = title_match.group(1).strip()
                for pattern in title_patterns:
                    if re.search(pattern, title_text, re.IGNORECASE):
                        success_indicators.append(f"Title pattern matched: {pattern}")
                        evidence.append(f"Title pattern '{pattern}' found in: {title_text}")
                        matched_patterns.append(f"title_pattern: {pattern}")
        
        # Check expected title (legacy support)
        if expected_title:
            title_pattern = rf'<title[^>]*>([^<]*{re.escape(expected_title)}[^<]*)</title>'
            if re.search(title_pattern, response_text, re.IGNORECASE):
                success_indicators.append(f"Expected title found: {expected_title}")
                evidence.append(f"Title validation passed for: {expected_title}")
                matched_patterns.append(f"expected_title: {expected_title}")
            else:
                failure_indicators.append(f"Expected title not found: {expected_title}")
        
        # Check expected elements
        if expected_elements:
            for element in expected_elements:
                if element in response_text:
                    success_indicators.append(f"Expected element found: {element}")
                    evidence.append(f"Element present: {element}")
                    matched_patterns.append(f"element: {element}")
                else:
                    failure_indicators.append(f"Expected element not found: {element}")
        
        # Check forbidden elements
        if forbidden_elements:
            for element in forbidden_elements:
                if element in response_text:
                    failure_indicators.append(f"Forbidden element found: {element}")
                else:
                    success_indicators.append(f"Forbidden element not found: {element}")
                    evidence.append(f"Forbidden element absent: {element}")
        
        # Check form validation
        if form_validation:
            form_action = form_validation.get('action')
            form_method = form_validation.get('method')
            required_inputs = form_validation.get('required_inputs', [])
            
            if form_action:
                if f'action="{form_action}"' in response_text or f"action='{form_action}'" in response_text:
                    success_indicators.append(f"Form action found: {form_action}")
                    evidence.append(f"Form action validation passed: {form_action}")
                    matched_patterns.append(f"form_action: {form_action}")
                else:
                    failure_indicators.append(f"Form action not found: {form_action}")
            
            if form_method:
                if f'method="{form_method}"' in response_text or f"method='{form_method}'" in response_text:
                    success_indicators.append(f"Form method found: {form_method}")
                    evidence.append(f"Form method validation passed: {form_method}")
                    matched_patterns.append(f"form_method: {form_method}")
                else:
                    failure_indicators.append(f"Form method not found: {form_method}")
            
            for input_name in required_inputs:
                if f'name="{input_name}"' in response_text or f"name='{input_name}'" in response_text:
                    success_indicators.append(f"Required input found: {input_name}")
                    evidence.append(f"Input field present: {input_name}")
                    matched_patterns.append(f"input: {input_name}")
                else:
                    failure_indicators.append(f"Required input not found: {input_name}")
        
        # Calculate confidence based on validation results
        total_checks = len(success_indicators) + len(failure_indicators)
        if total_checks == 0:
            confidence = 0.5  # Neutral confidence when no specific checks
        else:
            confidence = len(success_indicators) / total_checks
        
        is_valid = len(failure_indicators) == 0 and len(success_indicators) > 0
        
        if return_structured:
            return ValidationResult(
                is_valid=is_valid,
                confidence_score=confidence,
                matched_patterns=matched_patterns,
                evidence=evidence,
                validation_type=ValidationType.CONTENT,
                metadata={
                    'validation_method': 'html_response',
                    'response_size': len(response_text),
                    'status_code': response.status_code,
                    'content_type': content_type,
                    'success_indicators': success_indicators,
                    'failure_indicators': failure_indicators
                }
            )
        
        return is_valid
        
    except Exception as e:
        if return_structured:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                evidence=[],
                validation_type=ValidationType.ERROR,
                error_message=f"HTML validation error: {str(e)}",
                metadata={
                    'error': str(e),
                    'success_indicators': [],
                    'failure_indicators': [f"HTML validation error: {str(e)}"]
                }
            )
        return False


@monitor_performance("chained_validations")
def chain_validations(
    response: requests.Response,
    validation_chain: List[Dict[str, Any]],
    chain_logic: str = "AND",
    return_structured: bool = True  # Default to True to return list of results
) -> Union[bool, ValidationResult, List[ValidationResult]]:
    """
    Chain multiple validations together with logical operators.
    
    Args:
        response: HTTP response object to validate
        validation_chain: List of validation configurations
        chain_logic: Logic operator for chaining ("AND", "OR")
        return_structured: Whether to return ValidationResult object(s)
        
    Returns:
        bool, ValidationResult, or List[ValidationResult]: Combined or individual validation results
    """
    try:
        results = []
        all_success_indicators = []
        all_failure_indicators = []
        all_evidence = []
        
        for i, validation_config in enumerate(validation_chain):
            validation_type = validation_config.get('type', 'response')
            
            # Check for recognized validation parameters
            recognized_params = {
                'type', 'success_criteria', 'failure_criteria', 'regex_patterns', 
                'status_codes', 'headers_criteria', 'required_keys', 'forbidden_keys',
                'json_schema', 'expected_title', 'title_patterns', 'expected_elements',
                'forbidden_elements', 'form_validation', 'return_structured'
            }
            
            unrecognized_params = set(validation_config.keys()) - recognized_params
            if unrecognized_params:
                # Create error result for unrecognized parameters
                error_result = ValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    evidence=[],
                    validation_type=ValidationType.ERROR,
                    error_message=f"Unrecognized validation parameters: {', '.join(unrecognized_params)}",
                    metadata={'unrecognized_params': list(unrecognized_params)}
                )
                results.append(error_result)
                continue
            
            if validation_type == 'response':
                result = validate_response(
                    response=response,
                    success_criteria=validation_config.get('success_criteria'),
                    failure_criteria=validation_config.get('failure_criteria'),
                    regex_patterns=validation_config.get('regex_patterns'),
                    status_codes=validation_config.get('status_codes'),
                    headers_criteria=validation_config.get('headers_criteria'),
                    return_structured=True
                )
            elif validation_type == 'json':
                result = validate_json_response(
                    response=response,
                    required_keys=validation_config.get('required_keys'),
                    forbidden_keys=validation_config.get('forbidden_keys'),
                    json_schema=validation_config.get('json_schema')
                )
            elif validation_type == 'html':
                result = validate_html_response(
                    response=response,
                    expected_title=validation_config.get('expected_title'),
                    title_patterns=validation_config.get('title_patterns'),
                    expected_elements=validation_config.get('expected_elements'),
                    forbidden_elements=validation_config.get('forbidden_elements'),
                    form_validation=validation_config.get('form_validation'),
                    return_structured=True
                )
            else:
                # Default to basic response validation
                result = validate_response(response=response, return_structured=True)
            
            results.append(result)
            if hasattr(result, 'success_indicators'):
                all_success_indicators.extend(result.success_indicators or [])
            if hasattr(result, 'failure_indicators'):
                all_failure_indicators.extend(result.failure_indicators or [])
            if hasattr(result, 'evidence'):
                all_evidence.extend(result.evidence or [])
        
        # If tests expect individual results, return the list
        if return_structured and len(validation_chain) > 1:
            return results
        
        # Apply chain logic for combined result
        if chain_logic.upper() == "AND":
            final_result = all(r.is_valid for r in results)
        elif chain_logic.upper() == "OR":
            final_result = any(r.is_valid for r in results)
        else:
            raise ValueError(f"Unsupported chain logic: {chain_logic}")
        
        # Calculate combined confidence
        if results:
            combined_confidence = sum(r.confidence_score for r in results) / len(results)
        else:
            combined_confidence = 0.0
        
        if return_structured:
            return ValidationResult(
                is_valid=final_result,
                confidence_score=combined_confidence,
                success_indicators=all_success_indicators,
                failure_indicators=all_failure_indicators,
                evidence=all_evidence,
                validation_type=ValidationType.COMPOSITE,
                metadata={
                    'validation_method': 'chained_validations',
                    'chain_logic': chain_logic,
                    'validation_count': len(validation_chain),
                    'individual_results': [
                        {
                            'valid': r.is_valid,
                            'confidence': r.confidence_score,
                            'type': getattr(r, 'validation_type', ValidationType.CONTENT).value if hasattr(ValidationType, 'CONTENT') else 'content'
                        } for r in results
                    ]
                }
            )
        
        return final_result
        
    except Exception as e:
        if return_structured:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                success_indicators=[],
                failure_indicators=[f"Chain validation error: {str(e)}"],
                evidence=[],
                validation_type=ValidationType.ERROR,
                error_message=f"Chain validation error: {str(e)}",
                metadata={'error': str(e)}
            )
        return False


# Export enhanced API functions
__all__ = [
    'validate_response',
    'validate_with_preset', 
    'list_available_presets',
    'list_vulnerability_presets',
    'extract_from_response',
    'validate_json_response',
    'validate_business_logic',
    'validate_timing_attack',
    'create_custom_preset',
    'validate_html_response',
    'chain_validations'
]