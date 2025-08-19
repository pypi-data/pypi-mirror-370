from .detector import detect_idor_flaws, detect_idor_flaws_async
from .models import AccessTestResult, AccessDetectorConfig
from .validation import _validate_endpoint_template, _validate_inputs, _sanitize_test_id
from .baseline import _get_unauth_baseline, get_cached_unauth_baseline, _check_unauthenticated_baseline
from .core_logic import (
    _determine_vulnerability, _should_have_access, _make_request_with_retry,
    _test_single_id, _test_single_id_async, _test_single_id_with_baselines, _test_single_id_with_baselines_async
)
from .logging_helpers import log_info, log_warning, log_error

# Enhanced access detection capabilities
from .enhanced_detector import (
    run_enhanced_access_detection,
    run_enhanced_access_detection_sync,
    quick_idor_with_smart_ids,
    tenant_isolation_test_only,
    privilege_escalation_test_only,
    create_enhanced_access_config,
    EnhancedAccessTester,
    EnhancedAccessTestConfig,
    EnhancedAccessTestResults
)

# ID Generation and Fuzzing
from .id_generation import (
    generate_smart_id_list,
    EnhancedIDGenerator,
    create_id_generation_config,
    IDType,
    IDPattern,
    IDGenerationConfig,
    PatternDetector
)

# Tenant Isolation Testing
from .tenant_isolation import (
    run_comprehensive_tenant_isolation_test,
    create_tenant_test_config,
    TenantContext,
    TenantTestResult,
    TenantTestConfig,
    TenantIsolationTester,
    TenantEnumerator,
    TenantIsolationLevel,
    TenantTestType
)

# Privilege Escalation and Role Testing
from .privilege_escalation import (
    run_comprehensive_privilege_escalation_test,
    create_role_test_config,
    RoleDefinition,
    PrivilegeTestResult,
    RoleTestConfig,
    PrivilegeEscalationTester,
    RoleHierarchyMapper,
    PrivilegeLevel,
    PermissionType,
    RoleTestType
) 