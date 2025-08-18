from typing import List, Union, Optional
import requests
from logicpwn.core.cache.cache_utils import cached
from logicpwn.core.utils import check_indicators
from logicpwn.core.logging import log_warning
from .models import AccessTestResult, AccessDetectorConfig

def _get_unauth_baseline(endpoint_url: str, id_value: Union[str, int], request_timeout: int) -> Optional[requests.Response]:
    """
    Get the unauthenticated baseline response for a given endpoint and ID.
    
    Enhanced with better error handling and resource management.
    """
    session = None
    try:
        session = requests.Session()
        # Remove any existing authentication headers
        session.headers.clear()
        
        response = session.request(
            method="GET",
            url=endpoint_url,
            timeout=request_timeout,
            allow_redirects=False  # Don't follow redirects for baseline
        )
        return response
        
    except requests.exceptions.Timeout:
        log_warning(f"Baseline request timeout for {endpoint_url}")
        return None
    except requests.exceptions.ConnectionError:
        log_warning(f"Baseline connection error for {endpoint_url}")
        return None
    except requests.exceptions.RequestException as e:
        log_warning(f"Baseline request failed for {endpoint_url}: {e}")
        return None
    except Exception as e:
        log_warning(f"Unexpected error in baseline request for {endpoint_url}: {e}")
        return None
    finally:
        if session:
            session.close()

@cached(ttl=600, key_func=lambda endpoint_url, id_value, timeout: f"{endpoint_url}|{id_value}|{timeout}")
def get_cached_unauth_baseline(endpoint_url: str, id_value: Union[str, int], request_timeout: int) -> Optional[requests.Response]:
    return _get_unauth_baseline(endpoint_url, id_value, request_timeout)

def _check_unauthenticated_baseline(
    result: AccessTestResult,
    success_indicators: List[str],
    failure_indicators: List[str],
    config: AccessDetectorConfig
) -> AccessTestResult:
    """
    Compare the result to the unauthenticated baseline and update vulnerability status if needed.
    """
    if not config.compare_unauthenticated:
        return result
    try:
        unauth_response = get_cached_unauth_baseline(
            result.endpoint_url,
            result.id_tested,
            config.request_timeout
        )
        if unauth_response is not None:
            is_success, matched = check_indicators(unauth_response.text, success_indicators)
            is_failure, failed = check_indicators(unauth_response.text, failure_indicators)
            if is_success and not is_failure:
                result.vulnerability_detected = True
                result.error_message = (result.error_message or "") + " | Unauthenticated access possible"
        else:
            log_warning(f"No unauth baseline for {result.endpoint_url}")
    except Exception as e:
        log_warning(f"Failed to get unauth baseline for {result.endpoint_url}: {e}")
    return result 