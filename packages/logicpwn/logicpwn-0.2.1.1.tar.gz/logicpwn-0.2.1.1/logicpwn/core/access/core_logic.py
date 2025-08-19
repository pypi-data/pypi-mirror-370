from typing import List, Union, Optional, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from .models import AccessTestResult, AccessDetectorConfig
from logicpwn.core.runner.runner import send_request
from logicpwn.core.utils import check_indicators
from logicpwn.core.logging import log_info, log_warning, log_error
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner
from .baseline import _check_unauthenticated_baseline
import datetime
import json

def _determine_vulnerability(id_tested: Union[str, int], access_granted: bool, config: AccessDetectorConfig) -> bool:
    """
    Determine if a vulnerability exists for the tested ID.
    
    Fixed bugs:
    - Handle type inconsistencies between string and int IDs
    - Fix logic for conflicting configurations
    - Provide proper fallback for empty configurations
    """
    if not access_granted:
        return False
    
    # Normalize IDs to handle type inconsistencies
    def normalize_id(id_val):
        if isinstance(id_val, (str, int)):
            return str(id_val)
        return id_val
    
    normalized_tested = normalize_id(id_tested)
    
    # Check authorized_ids first (most specific)
    if config.authorized_ids is not None:
        normalized_authorized = [normalize_id(aid) for aid in config.authorized_ids]
        is_authorized = normalized_tested in normalized_authorized
        
        # Check for conflicting configuration
        if config.unauthorized_ids is not None:
            normalized_unauthorized = [normalize_id(uid) for uid in config.unauthorized_ids]
            is_unauthorized = normalized_tested in normalized_unauthorized
            
            if is_authorized and is_unauthorized:
                # Log conflict and prioritize unauthorized (more secure)
                log_warning(f"Conflicting configuration: ID {id_tested} in both authorized and unauthorized lists. Treating as unauthorized.")
                return True
        
        return not is_authorized
    
    # Check current_user_id
    if config.current_user_id is not None:
        normalized_current = normalize_id(config.current_user_id)
        return normalized_tested != normalized_current
    
    # Check unauthorized_ids
    if config.unauthorized_ids is not None:
        normalized_unauthorized = [normalize_id(uid) for uid in config.unauthorized_ids]
        return normalized_tested in normalized_unauthorized
    
    # Empty configuration - assume vulnerability exists if access is granted
    # This is more secure than returning False
    log_warning(f"Empty access control configuration detected. Assuming vulnerability for ID {id_tested}.")
    return True

def _should_have_access(id_tested: Union[str, int], config: AccessDetectorConfig) -> bool:
    """
    Determine if the tested ID should have access according to config.
    
    Fixed bugs:
    - Handle type inconsistencies between string and int IDs
    - Fix logic for conflicting configurations
    - Provide proper fallback for empty configurations
    """
    # Normalize IDs to handle type inconsistencies
    def normalize_id(id_val):
        if isinstance(id_val, (str, int)):
            return str(id_val)
        return id_val
    
    normalized_tested = normalize_id(id_tested)
    
    # Check authorized_ids first (most specific)
    if config.authorized_ids is not None:
        normalized_authorized = [normalize_id(aid) for aid in config.authorized_ids]
        is_authorized = normalized_tested in normalized_authorized
        
        # Check for conflicting configuration
        if config.unauthorized_ids is not None:
            normalized_unauthorized = [normalize_id(uid) for uid in config.unauthorized_ids]
            is_unauthorized = normalized_tested in normalized_unauthorized
            
            if is_authorized and is_unauthorized:
                # Log conflict and prioritize unauthorized (more secure)
                log_warning(f"Conflicting configuration: ID {id_tested} in both authorized and unauthorized lists. Denying access.")
                return False
        
        return is_authorized
    
    # Check current_user_id
    if config.current_user_id is not None:
        normalized_current = normalize_id(config.current_user_id)
        return normalized_tested == normalized_current
    
    # Check unauthorized_ids
    if config.unauthorized_ids is not None:
        normalized_unauthorized = [normalize_id(uid) for uid in config.unauthorized_ids]
        return normalized_tested not in normalized_unauthorized
    
    # Empty configuration - assume no access by default (more secure)
    log_warning(f"Empty access control configuration detected. Denying access for ID {id_tested}.")
    return False

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _make_request_with_retry(session: requests.Session, request_config: Dict[str, Any]) -> requests.Response:
    """
    Make a request with retry logic.
    """
    return send_request(session, request_config)

def _test_single_id(
    session: requests.Session,
    endpoint_url: str,
    id_value: Union[str, int],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    if config.rate_limit:
        import time
        time.sleep(config.rate_limit)
    log_info(f"Testing access to {endpoint_url} for ID {id_value}")
    try:
        response = _make_request_with_retry(session, {
            "url": endpoint_url,
            "method": "GET",
            "timeout": request_timeout
        })
        is_success, matched = check_indicators(response.text, success_indicators)
        is_failure, failed = check_indicators(response.text, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        result = AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=response.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access
        )
        return _check_unauthenticated_baseline(result, success_indicators, failure_indicators, config)
    except requests.exceptions.Timeout:
        log_warning(f"Timeout for {endpoint_url}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message="Timeout"
        )
    except requests.exceptions.ConnectionError:
        log_warning(f"Connection error for {endpoint_url}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message="Connection error"
        )
    except Exception as e:
        log_error(f"Request failed for {endpoint_url}: {e}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=str(e)
        )

async def _test_single_id_async(
    runner: AsyncRequestRunner,
    endpoint_url: str,
    id_value: Union[str, int],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    if config.rate_limit:
        await asyncio.sleep(config.rate_limit)
    log_info(f"[Async] Testing access to {endpoint_url} for ID {id_value}")
    try:
        result = await runner.send_request(
            url=endpoint_url,
            method="GET",
            timeout=request_timeout
        )
        is_success, matched = check_indicators(result.body, success_indicators)
        is_failure, failed = check_indicators(result.body, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        result_obj = AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=result.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access
        )
        return _check_unauthenticated_baseline(result_obj, success_indicators, failure_indicators, config)
    except Exception as e:
        log_warning(f"Async request failed for {endpoint_url}: {e}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=str(e)
        )

def _test_single_id_with_baselines(
    session: requests.Session,
    endpoint_url: str,
    id_value: Union[str, int],
    method: str,
    request_data: Optional[dict],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    """
    Test a single ID with support for custom method/data and multiple baseline sessions. Returns AccessTestResult with audit log.
    """
    if config.rate_limit:
        import time
        time.sleep(config.rate_limit)
    log_info(f"Testing access to {endpoint_url} for ID {id_value} (method={method})")
    request_kwargs = {
        "url": endpoint_url,
        "method": method,
        "timeout": request_timeout
    }
    if request_data:
        request_kwargs.update(request_data)
    try:
        response = _make_request_with_retry(session, request_kwargs)
        is_success, matched = check_indicators(response.text, success_indicators)
        is_failure, failed = check_indicators(response.text, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        # Baseline comparison (multi-session)
        baseline_results = []
        if config.baseline_sessions:
            for i, baseline_sess in enumerate(config.baseline_sessions):
                try:
                    baseline_resp = _make_request_with_retry(baseline_sess, request_kwargs)
                    b_success, b_matched = check_indicators(baseline_resp.text, success_indicators)
                    b_failure, b_failed = check_indicators(baseline_resp.text, failure_indicators)
                    baseline_results.append({
                        "session": config.baseline_names[i] if config.baseline_names and i < len(config.baseline_names) else f"baseline_{i}",
                        "status_code": baseline_resp.status_code,
                        "access_granted": b_success and not b_failure,
                        "indicators": b_matched + b_failed,
                        "body_excerpt": baseline_resp.text[:200]
                    })
                except Exception as e:
                    baseline_results.append({
                        "session": config.baseline_names[i] if config.baseline_names and i < len(config.baseline_names) else f"baseline_{i}",
                        "error": str(e)
                    })
        # Audit log
        decision_log = f"Access granted: {access_granted}, Expected: {expected_access}, Vulnerability: {vuln}"
        if baseline_results:
            decision_log += f" | Baselines: {json.dumps(baseline_results)}"
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=response.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access,
            request_method=method,
            request_data=request_data,
            response_body=response.text[:500],
            baseline_results=baseline_results if baseline_results else None,
            decision_log=decision_log
        )
    except Exception as e:
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=f"Error: {str(e)}",
            request_method=method,
            request_data=request_data,
            decision_log=f"Exception: {str(e)}"
        )

async def _test_single_id_with_baselines_async(
    runner: AsyncRequestRunner,
    endpoint_url: str,
    id_value: Union[str, int],
    method: str,
    request_data: Optional[dict],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    """
    Async version of _test_single_id_with_baselines.
    """
    if config.rate_limit:
        await asyncio.sleep(config.rate_limit)
    log_info(f"[Async] Testing access to {endpoint_url} for ID {id_value} (method={method})")
    request_kwargs = {
        "url": endpoint_url,
        "method": method,
        "timeout": request_timeout
    }
    if request_data:
        request_kwargs.update(request_data)
    try:
        result = await runner.send_request(**request_kwargs)
        is_success, matched = check_indicators(result.body, success_indicators)
        is_failure, failed = check_indicators(result.body, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        # Baseline comparison (multi-session)
        baseline_results = []
        if config.baseline_sessions:
            for i, baseline_sess in enumerate(config.baseline_sessions):
                try:
                    import requests
                    baseline_resp = _make_request_with_retry(baseline_sess, request_kwargs)
                    b_success, b_matched = check_indicators(baseline_resp.text, success_indicators)
                    b_failure, b_failed = check_indicators(baseline_resp.text, failure_indicators)
                    baseline_results.append({
                        "session": config.baseline_names[i] if config.baseline_names and i < len(config.baseline_names) else f"baseline_{i}",
                        "status_code": baseline_resp.status_code,
                        "access_granted": b_success and not b_failure,
                        "indicators": b_matched + b_failed,
                        "body_excerpt": baseline_resp.text[:200]
                    })
                except Exception as e:
                    baseline_results.append({
                        "session": config.baseline_names[i] if config.baseline_names and i < len(config.baseline_names) else f"baseline_{i}",
                        "error": str(e)
                    })
        decision_log = f"Access granted: {access_granted}, Expected: {expected_access}, Vulnerability: {vuln}"
        if baseline_results:
            decision_log += f" | Baselines: {json.dumps(baseline_results)}"
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=result.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access,
            request_method=method,
            request_data=request_data,
            response_body=result.body[:500],
            baseline_results=baseline_results if baseline_results else None,
            decision_log=decision_log
        )
    except Exception as e:
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=f"Error: {str(e)}",
            request_method=method,
            request_data=request_data,
            decision_log=f"Exception: {str(e)}"
        ) 