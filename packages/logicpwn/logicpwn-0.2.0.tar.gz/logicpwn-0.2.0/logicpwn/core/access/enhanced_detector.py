"""
Enhanced Access/IDOR Detection with Advanced Capabilities.

This module provides the enhanced entry point for the access detection system,
integrating all the advanced capabilities:
- Intelligent ID generation and fuzzing
- Tenant isolation testing
- Role hierarchy understanding and privilege escalation
- Comprehensive admin function discovery
- Automated vulnerability detection workflows
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
import requests

from logicpwn.core.logging import log_info, log_warning, log_error
from logicpwn.core.access.models import AccessTestResult, AccessDetectorConfig
from logicpwn.core.access.detector import detect_idor_flaws, detect_idor_flaws_async
from logicpwn.core.access.id_generation import (
    generate_smart_id_list, 
    EnhancedIDGenerator, 
    create_id_generation_config
)
from logicpwn.core.access.tenant_isolation import (
    run_comprehensive_tenant_isolation_test,
    TenantTestConfig,
    TenantContext,
    TenantTestResult
)
from logicpwn.core.access.privilege_escalation import (
    run_comprehensive_privilege_escalation_test,
    RoleTestConfig,
    RoleDefinition,
    PrivilegeTestResult,
    PrivilegeLevel
)


@dataclass
class EnhancedAccessTestConfig:
    """Comprehensive configuration for enhanced access testing."""
    # Basic IDOR testing
    basic_idor_config: Optional[AccessDetectorConfig] = None
    
    # ID generation and fuzzing
    enable_smart_id_generation: bool = True
    max_generated_ids: int = 1000
    include_privilege_escalation_ids: bool = True
    include_tenant_testing_ids: bool = True
    
    # Tenant isolation testing
    enable_tenant_isolation: bool = True
    tenant_test_config: Optional[TenantTestConfig] = None
    current_tenant_id: Optional[str] = None
    
    # Role and privilege testing
    enable_privilege_escalation: bool = True
    role_test_config: Optional[RoleTestConfig] = None
    current_role_name: Optional[str] = None
    
    # Admin function discovery
    enable_admin_discovery: bool = True
    admin_discovery_depth: int = 3
    
    # Performance and safety
    max_concurrent_tests: int = 20
    request_timeout: int = 30
    
    # Output and reporting
    detailed_reporting: bool = True
    include_evidence: bool = True


@dataclass
class EnhancedAccessTestResults:
    """Comprehensive results from enhanced access testing."""
    # Basic IDOR results
    idor_results: List[AccessTestResult] = field(default_factory=list)
    
    # Tenant isolation results
    tenant_isolation_results: List[TenantTestResult] = field(default_factory=list)
    
    # Privilege escalation results
    privilege_escalation_results: List[PrivilegeTestResult] = field(default_factory=list)
    
    # Summary statistics
    total_tests_executed: int = 0
    vulnerabilities_found: int = 0
    critical_vulnerabilities: int = 0
    high_risk_vulnerabilities: int = 0
    
    # Generated data
    generated_ids: List[str] = field(default_factory=list)
    discovered_tenants: List[str] = field(default_factory=list)
    discovered_roles: List[str] = field(default_factory=list)
    discovered_admin_functions: List[str] = field(default_factory=list)
    
    # Metadata
    test_duration: float = 0.0
    test_config: Optional[EnhancedAccessTestConfig] = None


class EnhancedAccessTester:
    """
    Enhanced access tester that orchestrates comprehensive access control testing.
    
    This class integrates all the advanced access testing capabilities into a
    unified interface for complete access control vulnerability assessment.
    """
    
    def __init__(self, config: Optional[EnhancedAccessTestConfig] = None):
        self.config = config or EnhancedAccessTestConfig()
        self.id_generator = EnhancedIDGenerator(
            create_id_generation_config(
                max_ids=self.config.max_generated_ids,
                enable_edge_cases=True
            )
        )
    
    async def run_comprehensive_access_test(
        self,
        session: requests.Session,
        base_url: str,
        endpoint_template: str,
        example_ids: List[str],
        success_indicators: List[str],
        failure_indicators: List[str]
    ) -> EnhancedAccessTestResults:
        """
        Run comprehensive access control testing with all enhanced capabilities.
        
        This is the main entry point for the enhanced access testing system.
        """
        import time
        start_time = time.time()
        
        log_info("Starting comprehensive enhanced access control testing")
        
        results = EnhancedAccessTestResults(test_config=self.config)
        
        try:
            # Phase 1: Smart ID Generation
            if self.config.enable_smart_id_generation:
                generated_ids = await self._generate_smart_test_ids(example_ids)
                results.generated_ids = generated_ids
                log_info(f"Generated {len(generated_ids)} intelligent test IDs")
            else:
                generated_ids = example_ids
            
            # Phase 2: Basic IDOR Testing with Enhanced IDs
            idor_results = await self._run_enhanced_idor_testing(
                session, endpoint_template, generated_ids, success_indicators, failure_indicators
            )
            results.idor_results = idor_results
            log_info(f"Completed IDOR testing: {len(idor_results)} tests executed")
            
            # Phase 3: Tenant Isolation Testing
            if self.config.enable_tenant_isolation and self.config.current_tenant_id:
                tenant_results = await self._run_tenant_isolation_testing(
                    session, base_url
                )
                results.tenant_isolation_results = tenant_results
                log_info(f"Completed tenant isolation testing: {len(tenant_results)} tests executed")
            
            # Phase 4: Privilege Escalation Testing
            if self.config.enable_privilege_escalation and self.config.current_role_name:
                privilege_results = await self._run_privilege_escalation_testing(
                    session, base_url
                )
                results.privilege_escalation_results = privilege_results
                log_info(f"Completed privilege escalation testing: {len(privilege_results)} tests executed")
            
            # Phase 5: Generate Summary Statistics
            self._calculate_summary_statistics(results)
            
            results.test_duration = time.time() - start_time
            
            log_info(f"Enhanced access testing completed in {results.test_duration:.2f} seconds")
            log_info(f"Total vulnerabilities found: {results.vulnerabilities_found}")
            log_info(f"Critical vulnerabilities: {results.critical_vulnerabilities}")
            
            return results
            
        except Exception as e:
            log_error(f"Error in comprehensive access testing: {str(e)}")
            results.test_duration = time.time() - start_time
            return results
    
    async def _generate_smart_test_ids(self, example_ids: List[str]) -> List[str]:
        """Generate intelligent test IDs using the enhanced ID generator."""
        return generate_smart_id_list(
            example_ids=example_ids,
            max_total_ids=self.config.max_generated_ids,
            include_privilege_escalation=self.config.include_privilege_escalation_ids,
            include_tenant_testing=self.config.include_tenant_testing_ids
        )
    
    async def _run_enhanced_idor_testing(
        self,
        session: requests.Session,
        endpoint_template: str,
        test_ids: List[str],
        success_indicators: List[str],
        failure_indicators: List[str]
    ) -> List[AccessTestResult]:
        """Run enhanced IDOR testing with the generated IDs."""
        # Use the existing IDOR detection with enhanced configuration
        enhanced_config = self.config.basic_idor_config or AccessDetectorConfig()
        enhanced_config.max_concurrent_requests = min(
            self.config.max_concurrent_tests, 
            enhanced_config.max_concurrent_requests
        )
        enhanced_config.request_timeout = self.config.request_timeout
        
        # Use async version for better performance
        return await detect_idor_flaws_async(
            endpoint_template=endpoint_template,
            test_ids=test_ids,
            success_indicators=success_indicators,
            failure_indicators=failure_indicators,
            config=enhanced_config
        )
    
    async def _run_tenant_isolation_testing(
        self,
        session: requests.Session,
        base_url: str
    ) -> List[TenantTestResult]:
        """Run comprehensive tenant isolation testing."""
        tenant_config = self.config.tenant_test_config or TenantTestConfig()
        tenant_config.max_concurrent_tests = min(
            self.config.max_concurrent_tests,
            tenant_config.max_concurrent_tests
        )
        
        return await run_comprehensive_tenant_isolation_test(
            base_url=base_url,
            session=session,
            current_tenant_id=self.config.current_tenant_id,
            config=tenant_config
        )
    
    async def _run_privilege_escalation_testing(
        self,
        session: requests.Session,
        base_url: str
    ) -> List[PrivilegeTestResult]:
        """Run comprehensive privilege escalation testing."""
        role_config = self.config.role_test_config or RoleTestConfig()
        role_config.max_concurrent_tests = min(
            self.config.max_concurrent_tests,
            role_config.max_concurrent_tests
        )
        
        return await run_comprehensive_privilege_escalation_test(
            base_url=base_url,
            session=session,
            current_role_name=self.config.current_role_name,
            config=role_config
        )
    
    def _calculate_summary_statistics(self, results: EnhancedAccessTestResults) -> None:
        """Calculate summary statistics for the test results."""
        total_tests = 0
        vulnerabilities = 0
        critical_vulns = 0
        high_risk_vulns = 0
        
        # Count IDOR results
        total_tests += len(results.idor_results)
        for result in results.idor_results:
            if getattr(result, 'vulnerability_detected', False):
                vulnerabilities += 1
                # Assume IDOR vulnerabilities are high risk
                high_risk_vulns += 1
        
        # Count tenant isolation results
        total_tests += len(results.tenant_isolation_results)
        for result in results.tenant_isolation_results:
            if result.isolation_breach:
                vulnerabilities += 1
                if result.risk_level == "CRITICAL":
                    critical_vulns += 1
                elif result.risk_level == "HIGH":
                    high_risk_vulns += 1
        
        # Count privilege escalation results
        total_tests += len(results.privilege_escalation_results)
        for result in results.privilege_escalation_results:
            if result.privilege_escalation:
                vulnerabilities += 1
                if result.risk_level == "CRITICAL":
                    critical_vulns += 1
                elif result.risk_level == "HIGH":
                    high_risk_vulns += 1
        
        # Extract discovered data
        results.discovered_tenants = list(set([
            result.target_tenant.tenant_id for result in results.tenant_isolation_results
            if result.target_tenant
        ]))
        
        results.discovered_roles = list(set([
            result.target_role.role_name for result in results.privilege_escalation_results
            if result.target_role
        ]))
        
        results.discovered_admin_functions = list(set([
            result.function_name for result in results.privilege_escalation_results
            if result.function_name and "admin" in result.function_name.lower()
        ]))
        
        # Update summary
        results.total_tests_executed = total_tests
        results.vulnerabilities_found = vulnerabilities
        results.critical_vulnerabilities = critical_vulns
        results.high_risk_vulnerabilities = high_risk_vulns
    
    def generate_detailed_report(self, results: EnhancedAccessTestResults) -> Dict[str, Any]:
        """Generate a detailed report of the test results."""
        report = {
            "summary": {
                "total_tests": results.total_tests_executed,
                "vulnerabilities_found": results.vulnerabilities_found,
                "critical_vulnerabilities": results.critical_vulnerabilities,
                "high_risk_vulnerabilities": results.high_risk_vulnerabilities,
                "test_duration": results.test_duration
            },
            "id_generation": {
                "total_generated": len(results.generated_ids),
                "example_ids": results.generated_ids[:10] if results.generated_ids else []
            },
            "idor_testing": {
                "total_tests": len(results.idor_results),
                "vulnerabilities": [
                    {
                        "id_tested": result.id_tested,
                        "endpoint": result.endpoint_url,
                        "vulnerable": getattr(result, 'vulnerability_detected', False),
                        "status_code": result.status_code
                    }
                    for result in results.idor_results
                    if getattr(result, 'vulnerability_detected', False)
                ]
            },
            "tenant_isolation": {
                "total_tests": len(results.tenant_isolation_results),
                "discovered_tenants": results.discovered_tenants,
                "isolation_breaches": [
                    {
                        "test_type": result.test_type.value,
                        "source_tenant": result.source_tenant.tenant_id,
                        "target_tenant": result.target_tenant.tenant_id if result.target_tenant else None,
                        "endpoint": result.endpoint,
                        "risk_level": result.risk_level,
                        "evidence": result.evidence
                    }
                    for result in results.tenant_isolation_results
                    if result.isolation_breach
                ]
            },
            "privilege_escalation": {
                "total_tests": len(results.privilege_escalation_results),
                "discovered_roles": results.discovered_roles,
                "discovered_admin_functions": results.discovered_admin_functions,
                "escalations": [
                    {
                        "test_type": result.test_type.value,
                        "source_role": result.source_role.role_name,
                        "target_role": result.target_role.role_name if result.target_role else None,
                        "endpoint": result.endpoint,
                        "function": result.function_name,
                        "risk_level": result.risk_level,
                        "evidence": result.evidence
                    }
                    for result in results.privilege_escalation_results
                    if result.privilege_escalation
                ]
            }
        }
        
        return report


def create_enhanced_access_config(
    enable_all_features: bool = True,
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    max_concurrent: int = 20,
    detailed_testing: bool = True
) -> EnhancedAccessTestConfig:
    """Create a comprehensive enhanced access test configuration."""
    
    # Create sub-configurations
    idor_config = AccessDetectorConfig(
        max_concurrent_requests=max_concurrent,
        request_timeout=30,
        compare_unauthenticated=True
    )
    
    tenant_config = TenantTestConfig(
        max_concurrent_tests=max_concurrent
    ) if enable_all_features else None
    
    role_config = RoleTestConfig(
        max_concurrent_tests=max_concurrent
    ) if enable_all_features else None
    
    return EnhancedAccessTestConfig(
        basic_idor_config=idor_config,
        enable_smart_id_generation=enable_all_features,
        enable_tenant_isolation=enable_all_features and current_tenant_id is not None,
        enable_privilege_escalation=enable_all_features and current_role_name is not None,
        enable_admin_discovery=enable_all_features,
        tenant_test_config=tenant_config,
        role_test_config=role_config,
        current_tenant_id=current_tenant_id,
        current_role_name=current_role_name,
        max_concurrent_tests=max_concurrent,
        detailed_reporting=detailed_testing
    )


async def run_enhanced_access_detection(
    session: requests.Session,
    base_url: str,
    endpoint_template: str,
    example_ids: List[str],
    success_indicators: List[str],
    failure_indicators: List[str],
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    config: Optional[EnhancedAccessTestConfig] = None
) -> EnhancedAccessTestResults:
    """
    High-level function to run enhanced access detection with all capabilities.
    
    This is the main entry point for comprehensive access control testing.
    
    Args:
        session: Authenticated requests session
        base_url: Base URL of the application
        endpoint_template: Template for IDOR testing (e.g., "/api/users/{id}")
        example_ids: Known valid IDs to base generation on
        success_indicators: Response indicators for successful access
        failure_indicators: Response indicators for denied access
        current_tenant_id: Current tenant context (for tenant isolation testing)
        current_role_name: Current role context (for privilege escalation testing)
        config: Optional custom configuration
    
    Returns:
        Comprehensive test results including all vulnerability types
    """
    # Create default config if not provided
    if not config:
        config = create_enhanced_access_config(
            enable_all_features=True,
            current_tenant_id=current_tenant_id,
            current_role_name=current_role_name,
            detailed_testing=True
        )
    
    # Create the enhanced tester
    tester = EnhancedAccessTester(config)
    
    # Run the comprehensive test
    results = await tester.run_comprehensive_access_test(
        session=session,
        base_url=base_url,
        endpoint_template=endpoint_template,
        example_ids=example_ids,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators
    )
    
    return results


def run_enhanced_access_detection_sync(
    session: requests.Session,
    base_url: str,
    endpoint_template: str,
    example_ids: List[str],
    success_indicators: List[str],
    failure_indicators: List[str],
    current_tenant_id: Optional[str] = None,
    current_role_name: Optional[str] = None,
    config: Optional[EnhancedAccessTestConfig] = None
) -> EnhancedAccessTestResults:
    """
    Synchronous wrapper for enhanced access detection.
    
    This function provides a synchronous interface to the async testing capabilities.
    """
    return asyncio.run(run_enhanced_access_detection(
        session=session,
        base_url=base_url,
        endpoint_template=endpoint_template,
        example_ids=example_ids,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators,
        current_tenant_id=current_tenant_id,
        current_role_name=current_role_name,
        config=config
    ))


# Convenience functions for specific testing scenarios

def quick_idor_with_smart_ids(
    session: requests.Session,
    endpoint_template: str,
    example_ids: List[str],
    success_indicators: List[str],
    failure_indicators: List[str],
    max_generated_ids: int = 500
) -> List[AccessTestResult]:
    """Quick IDOR testing with intelligent ID generation."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=True,
        max_generated_ids=max_generated_ids,
        enable_tenant_isolation=False,
        enable_privilege_escalation=False,
        enable_admin_discovery=False
    )
    
    results = run_enhanced_access_detection_sync(
        session=session,
        base_url="",  # Not needed for basic IDOR
        endpoint_template=endpoint_template,
        example_ids=example_ids,
        success_indicators=success_indicators,
        failure_indicators=failure_indicators,
        config=config
    )
    
    return results.idor_results


def tenant_isolation_test_only(
    session: requests.Session,
    base_url: str,
    current_tenant_id: str
) -> List[TenantTestResult]:
    """Run only tenant isolation testing."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=False,
        enable_tenant_isolation=True,
        enable_privilege_escalation=False,
        enable_admin_discovery=False,
        current_tenant_id=current_tenant_id
    )
    
    results = run_enhanced_access_detection_sync(
        session=session,
        base_url=base_url,
        endpoint_template="/api/dummy/{id}",  # Not used
        example_ids=["dummy"],
        success_indicators=["success"],
        failure_indicators=["error"],
        current_tenant_id=current_tenant_id,
        config=config
    )
    
    return results.tenant_isolation_results


def privilege_escalation_test_only(
    session: requests.Session,
    base_url: str,
    current_role_name: str
) -> List[PrivilegeTestResult]:
    """Run only privilege escalation testing."""
    config = EnhancedAccessTestConfig(
        enable_smart_id_generation=False,
        enable_tenant_isolation=False,
        enable_privilege_escalation=True,
        enable_admin_discovery=True,
        current_role_name=current_role_name
    )
    
    results = run_enhanced_access_detection_sync(
        session=session,
        base_url=base_url,
        endpoint_template="/api/dummy/{id}",  # Not used
        example_ids=["dummy"],
        success_indicators=["success"],
        failure_indicators=["error"],
        current_role_name=current_role_name,
        config=config
    )
    
    return results.privilege_escalation_results
