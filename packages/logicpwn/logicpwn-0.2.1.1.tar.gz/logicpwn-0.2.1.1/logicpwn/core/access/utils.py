"""
Legacy access detector utilities. All helpers are now split into validation.py, baseline.py, and core_logic.py.
This module re-exports them for backward compatibility.
"""
from .validation import _validate_endpoint_template, _validate_inputs, _sanitize_test_id
from .baseline import _get_unauth_baseline, get_cached_unauth_baseline, _check_unauthenticated_baseline
from .core_logic import (
    _determine_vulnerability, _should_have_access, _make_request_with_retry,
    _test_single_id, _test_single_id_async, _test_single_id_with_baselines, _test_single_id_with_baselines_async
)

# Import send_request from runner module for backward compatibility
from ..runner.runner import send_request 