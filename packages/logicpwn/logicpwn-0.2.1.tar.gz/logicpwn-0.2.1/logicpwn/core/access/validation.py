from typing import List, Union
from urllib.parse import urlparse
import re

def _validate_endpoint_template(template: str) -> None:
    """
    Validate that the endpoint template is a valid HTTP/HTTPS URL with an {id} placeholder.
    """
    try:
        parsed = urlparse(template.format(id='test'))
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS schemes allowed in endpoint_template")
    except Exception:
        raise ValueError("Invalid endpoint_template or URL format")

def _validate_inputs(endpoint_template: str, test_ids: List[Union[str, int]], success_indicators: List[str], failure_indicators: List[str]):
    """
    Validate all required inputs for the access detector.
    
    Enhanced validation with better error messages and edge case handling.
    """
    # Validate endpoint template
    if not endpoint_template:
        raise ValueError("endpoint_template cannot be empty or None")
    
    if '{id}' not in endpoint_template:
        raise ValueError("endpoint_template must contain '{id}' placeholder")
    
    try:
        _validate_endpoint_template(endpoint_template)
    except ValueError as e:
        raise ValueError(f"Invalid endpoint_template: {e}")
    
    # Validate test_ids
    if not test_ids:
        raise ValueError("test_ids cannot be empty")
    
    if not isinstance(test_ids, list):
        raise TypeError("test_ids must be a list")
    
    # Check for valid ID types
    for i, test_id in enumerate(test_ids):
        if not isinstance(test_id, (str, int)):
            raise TypeError(f"test_ids[{i}] must be str or int, got {type(test_id)}")
        if isinstance(test_id, str) and not test_id.strip():
            raise ValueError(f"test_ids[{i}] cannot be empty string")
    
    # Validate indicators
    if not success_indicators:
        raise ValueError("success_indicators cannot be empty")
    
    if not failure_indicators:
        raise ValueError("failure_indicators cannot be empty")
    
    if not isinstance(success_indicators, list):
        raise TypeError("success_indicators must be a list")
    
    if not isinstance(failure_indicators, list):
        raise TypeError("failure_indicators must be a list")
    
    # Check for empty indicators
    for i, indicator in enumerate(success_indicators):
        if not isinstance(indicator, str) or not indicator.strip():
            raise ValueError(f"success_indicators[{i}] must be non-empty string")
    
    for i, indicator in enumerate(failure_indicators):
        if not isinstance(indicator, str) or not indicator.strip():
            raise ValueError(f"failure_indicators[{i}] must be non-empty string")

def _sanitize_test_id(test_id: Union[str, int]) -> Union[str, int]:
    """
    Sanitize the test ID to remove unsafe characters.
    """
    if isinstance(test_id, str):
        return re.sub(r'[^a-zA-Z0-9_-]', '', test_id)
    return test_id 