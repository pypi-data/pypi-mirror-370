"""
Tenant Isolation Testing Module for LogicPWN.

Provides comprehensive tenant isolation validation capabilities including:
- Cross-tenant access testing
- Tenant boundary enforcement validation
- Multi-tenant data leakage detection
- Tenant context manipulation
- Systematic tenant enumeration
- Privilege escalation across tenants
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from logicpwn.core.logging import log_info, log_warning, log_error
from logicpwn.core.access.models import AccessTestResult, AccessDetectorConfig
from logicpwn.core.access.id_generation import EnhancedIDGenerator, create_id_generation_config
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner


class TenantIsolationLevel(Enum):
    """Levels of tenant isolation to test."""
    DATA = "data"  # Data separation
    SCHEMA = "schema"  # Database schema separation
    INSTANCE = "instance"  # Complete instance separation
    NETWORK = "network"  # Network-level separation
    API = "api"  # API endpoint separation


class TenantTestType(Enum):
    """Types of tenant isolation tests."""
    CROSS_TENANT_ACCESS = "cross_tenant_access"
    TENANT_ENUMERATION = "tenant_enumeration"
    TENANT_ESCALATION = "tenant_escalation"
    DATA_LEAKAGE = "data_leakage"
    CONTEXT_MANIPULATION = "context_manipulation"
    SUBDOMAIN_TAKEOVER = "subdomain_takeover"


@dataclass
class TenantContext:
    """Represents a tenant context for testing."""
    tenant_id: str
    tenant_name: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    api_prefix: Optional[str] = None
    auth_context: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    isolation_level: TenantIsolationLevel = TenantIsolationLevel.DATA
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantTestResult:
    """Result of a tenant isolation test."""
    test_type: TenantTestType
    source_tenant: TenantContext
    target_tenant: Optional[TenantContext]
    endpoint: str
    success: bool
    isolation_breach: bool
    response_data: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    details: str = ""
    timestamp: str = field(default_factory=lambda: str(asyncio.get_event_loop().time()))


@dataclass
class TenantTestConfig:
    """Configuration for tenant isolation testing."""
    test_types: List[TenantTestType] = field(default_factory=lambda: [
        TenantTestType.CROSS_TENANT_ACCESS,
        TenantTestType.TENANT_ENUMERATION,
        TenantTestType.DATA_LEAKAGE
    ])
    isolation_levels: List[TenantIsolationLevel] = field(default_factory=lambda: [
        TenantIsolationLevel.DATA,
        TenantIsolationLevel.API
    ])
    max_concurrent_tests: int = 10
    request_timeout: int = 30
    enumeration_depth: int = 3
    data_leakage_patterns: List[str] = field(default_factory=lambda: [
        r'"tenant_id":\s*"([^"]*)"',
        r'"org[_-]?id":\s*"([^"]*)"',
        r'"account[_-]?id":\s*"([^"]*)"',
        r'"workspace[_-]?id":\s*"([^"]*)"',
        r'tenant[_-]?(\w+)',
        r'org[_-]?(\w+)',
    ])
    forbidden_indicators: List[str] = field(default_factory=lambda: [
        "access denied", "forbidden", "unauthorized", "not found",
        "permission denied", "insufficient privileges"
    ])
    success_indicators: List[str] = field(default_factory=lambda: [
        "tenant_id", "organization", "workspace", "account",
        "users", "data", "settings", "billing"
    ])


class TenantEnumerator:
    """Enumerates and discovers tenant identifiers."""
    
    def __init__(self, config: TenantTestConfig):
        self.config = config
        self.id_generator = EnhancedIDGenerator(create_id_generation_config(max_ids=500))
    
    async def enumerate_tenants(
        self, 
        base_url: str, 
        session: requests.Session,
        known_tenants: List[str] = None
    ) -> List[TenantContext]:
        """Enumerate tenant identifiers through various techniques."""
        tenants = []
        known_tenants = known_tenants or []
        
        # Method 1: DNS enumeration for subdomains
        subdomain_tenants = await self._enumerate_subdomains(base_url)
        tenants.extend(subdomain_tenants)
        
        # Method 2: Path-based tenant enumeration
        path_tenants = await self._enumerate_path_tenants(base_url, session, known_tenants)
        tenants.extend(path_tenants)
        
        # Method 3: API discovery
        api_tenants = await self._enumerate_api_tenants(base_url, session, known_tenants)
        tenants.extend(api_tenants)
        
        # Method 4: Response header analysis
        header_tenants = await self._discover_tenants_from_headers(base_url, session)
        tenants.extend(header_tenants)
        
        # Deduplicate tenants
        unique_tenants = self._deduplicate_tenants(tenants)
        
        log_info(f"Enumerated {len(unique_tenants)} unique tenants")
        return unique_tenants
    
    async def _enumerate_subdomains(self, base_url: str) -> List[TenantContext]:
        """Enumerate tenant subdomains."""
        parsed_url = urlparse(base_url)
        if not parsed_url.netloc:
            return []
        
        # Common tenant subdomain patterns
        tenant_patterns = [
            'admin', 'api', 'app', 'client', 'demo', 'dev', 'staging',
            'test', 'www', 'portal', 'dashboard', 'console', 'manage'
        ]
        
        # Multi-tenant SaaS patterns
        saas_patterns = [
            'tenant1', 'tenant2', 'org1', 'org2', 'company1', 'company2',
            'acme', 'demo-corp', 'test-org', 'sample', 'trial'
        ]
        
        all_patterns = tenant_patterns + saas_patterns
        
        tenants = []
        domain_parts = parsed_url.netloc.split('.')
        if len(domain_parts) >= 2:
            base_domain = '.'.join(domain_parts[-2:])
            
            for pattern in all_patterns:
                tenant_context = TenantContext(
                    tenant_id=pattern,
                    tenant_name=pattern,
                    domain=f"{pattern}.{base_domain}",
                    subdomain=pattern,
                    isolation_level=TenantIsolationLevel.INSTANCE
                )
                tenants.append(tenant_context)
        
        return tenants
    
    async def _enumerate_path_tenants(
        self, 
        base_url: str, 
        session: requests.Session,
        known_tenants: List[str]
    ) -> List[TenantContext]:
        """Enumerate tenants through path-based discovery."""
        tenants = []
        
        # Generate tenant IDs based on known patterns
        if known_tenants:
            tenant_ids = self.id_generator.generate_tenant_isolation_ids(known_tenants)
            all_tenant_ids = []
            for category, ids in tenant_ids.items():
                all_tenant_ids.extend(ids)
        else:
            # Use common patterns
            all_tenant_ids = [
                'admin', 'test', 'demo', 'trial', 'default', 'system',
                'acme', 'example', 'sample', 'dev', 'staging', 'prod'
            ]
        
        # Test path-based tenant access
        tenant_paths = [
            '/tenant/{tenant_id}',
            '/org/{tenant_id}', 
            '/account/{tenant_id}',
            '/workspace/{tenant_id}',
            '/{tenant_id}',
            '/api/v1/tenant/{tenant_id}',
            '/api/tenant/{tenant_id}'
        ]
        
        async with AsyncRequestRunner(max_concurrent=self.config.max_concurrent_tests) as runner:
            tasks = []
            
            for tenant_id in all_tenant_ids[:100]:  # Limit to avoid overwhelming
                for path_template in tenant_paths:
                    path = path_template.format(tenant_id=tenant_id)
                    url = base_url.rstrip('/') + path
                    tasks.append(self._test_tenant_path(runner, url, tenant_id))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, TenantContext):
                    tenants.append(result)
        
        return tenants
    
    async def _test_tenant_path(
        self, 
        runner: AsyncRequestRunner, 
        url: str, 
        tenant_id: str
    ) -> Optional[TenantContext]:
        """Test if a tenant path is accessible."""
        try:
            response = await runner.send_request(url, method="GET", timeout=self.config.request_timeout)
            
            # Check if the response indicates tenant existence
            if (response.status_code in [200, 301, 302, 401, 403] and
                any(indicator in response.body.lower() for indicator in self.config.success_indicators)):
                
                return TenantContext(
                    tenant_id=tenant_id,
                    tenant_name=tenant_id,
                    api_prefix=url,
                    isolation_level=TenantIsolationLevel.API,
                    metadata={
                        "discovery_method": "path_enumeration",
                        "status_code": response.status_code,
                        "url": url
                    }
                )
        except Exception as e:
            log_warning(f"Error testing tenant path {url}: {str(e)}")
        
        return None
    
    async def _enumerate_api_tenants(
        self, 
        base_url: str, 
        session: requests.Session,
        known_tenants: List[str]
    ) -> List[TenantContext]:
        """Enumerate tenants through API discovery."""
        tenants = []
        
        # Common API endpoints that might leak tenant information
        api_endpoints = [
            '/api/tenants',
            '/api/organizations', 
            '/api/accounts',
            '/api/workspaces',
            '/api/v1/tenants',
            '/api/v1/orgs',
            '/admin/tenants',
            '/health',
            '/info',
            '/status'
        ]
        
        for endpoint in api_endpoints:
            url = base_url.rstrip('/') + endpoint
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                if response.status_code == 200:
                    tenant_ids = self._extract_tenant_ids_from_response(response.text)
                    for tenant_id in tenant_ids:
                        tenant_context = TenantContext(
                            tenant_id=tenant_id,
                            tenant_name=tenant_id,
                            isolation_level=TenantIsolationLevel.API,
                            metadata={
                                "discovery_method": "api_discovery",
                                "endpoint": endpoint
                            }
                        )
                        tenants.append(tenant_context)
            except Exception as e:
                log_warning(f"Error accessing API endpoint {url}: {str(e)}")
        
        return tenants
    
    def _extract_tenant_ids_from_response(self, response_text: str) -> List[str]:
        """Extract tenant IDs from API response text."""
        tenant_ids = set()
        
        for pattern in self.config.data_leakage_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    tenant_ids.update(match)
                else:
                    tenant_ids.add(match)
        
        # Filter out common false positives
        filtered_ids = {
            tid for tid in tenant_ids 
            if len(tid) > 1 and tid.lower() not in ['null', 'undefined', 'none', 'test']
        }
        
        return list(filtered_ids)
    
    async def _discover_tenants_from_headers(
        self, 
        base_url: str, 
        session: requests.Session
    ) -> List[TenantContext]:
        """Discover tenant information from HTTP response headers."""
        tenants = []
        
        try:
            response = session.get(base_url, timeout=self.config.request_timeout)
            
            # Check for tenant-related headers
            tenant_headers = [
                'x-tenant-id', 'x-org-id', 'x-account-id', 'x-workspace-id',
                'tenant-id', 'org-id', 'account-id', 'workspace-id'
            ]
            
            for header in tenant_headers:
                if header in response.headers:
                    tenant_id = response.headers[header]
                    tenant_context = TenantContext(
                        tenant_id=tenant_id,
                        tenant_name=tenant_id,
                        isolation_level=TenantIsolationLevel.API,
                        metadata={
                            "discovery_method": "header_analysis",
                            "header": header
                        }
                    )
                    tenants.append(tenant_context)
            
        except Exception as e:
            log_warning(f"Error analyzing headers for {base_url}: {str(e)}")
        
        return tenants
    
    def _deduplicate_tenants(self, tenants: List[TenantContext]) -> List[TenantContext]:
        """Remove duplicate tenant contexts."""
        seen_ids = set()
        unique_tenants = []
        
        for tenant in tenants:
            if tenant.tenant_id not in seen_ids:
                seen_ids.add(tenant.tenant_id)
                unique_tenants.append(tenant)
        
        return unique_tenants


class TenantIsolationTester:
    """Tests tenant isolation boundaries and detects cross-tenant vulnerabilities."""
    
    def __init__(self, config: TenantTestConfig):
        self.config = config
        self.enumerator = TenantEnumerator(config)
    
    async def test_tenant_isolation(
        self, 
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenants: List[TenantContext] = None
    ) -> List[TenantTestResult]:
        """Comprehensive tenant isolation testing."""
        results = []
        
        # Discover target tenants if not provided
        if not target_tenants:
            target_tenants = await self.enumerator.enumerate_tenants(base_url, session)
        
        # Execute different types of tenant tests
        for test_type in self.config.test_types:
            if test_type == TenantTestType.CROSS_TENANT_ACCESS:
                test_results = await self._test_cross_tenant_access(
                    base_url, session, current_tenant, target_tenants
                )
                results.extend(test_results)
            
            elif test_type == TenantTestType.DATA_LEAKAGE:
                test_results = await self._test_data_leakage(
                    base_url, session, current_tenant, target_tenants
                )
                results.extend(test_results)
            
            elif test_type == TenantTestType.CONTEXT_MANIPULATION:
                test_results = await self._test_context_manipulation(
                    base_url, session, current_tenant, target_tenants
                )
                results.extend(test_results)
            
            elif test_type == TenantTestType.TENANT_ENUMERATION:
                test_results = await self._test_tenant_enumeration(
                    base_url, session, current_tenant
                )
                results.extend(test_results)
        
        return results
    
    async def _test_cross_tenant_access(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenants: List[TenantContext]
    ) -> List[TenantTestResult]:
        """Test cross-tenant access violations."""
        results = []
        
        # Common resource endpoints to test across tenants
        resource_endpoints = [
            '/api/users',
            '/api/documents',
            '/api/settings',
            '/api/billing',
            '/api/admin',
            '/dashboard',
            '/profile',
            '/files',
            '/reports'
        ]
        
        async with AsyncRequestRunner(max_concurrent=self.config.max_concurrent_tests) as runner:
            tasks = []
            
            for target_tenant in target_tenants:
                if target_tenant.tenant_id == current_tenant.tenant_id:
                    continue
                
                for endpoint in resource_endpoints:
                    # Generate tenant-specific URLs
                    test_urls = self._generate_tenant_urls(base_url, target_tenant, endpoint)
                    
                    for url in test_urls:
                        tasks.append(
                            self._test_single_cross_tenant_access(
                                runner, url, current_tenant, target_tenant, endpoint
                            )
                        )
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [r for r in results if isinstance(r, TenantTestResult)]
        
        return results
    
    def _generate_tenant_urls(self, base_url: str, tenant: TenantContext, endpoint: str) -> List[str]:
        """Generate possible URLs for tenant-specific resources."""
        urls = []
        base = base_url.rstrip('/')
        
        # Path-based tenant URLs
        path_patterns = [
            f"/tenant/{tenant.tenant_id}{endpoint}",
            f"/org/{tenant.tenant_id}{endpoint}",
            f"/account/{tenant.tenant_id}{endpoint}",
            f"/{tenant.tenant_id}{endpoint}",
            f"/api/v1/tenant/{tenant.tenant_id}{endpoint}",
            f"/api/tenant/{tenant.tenant_id}{endpoint}"
        ]
        
        for pattern in path_patterns:
            urls.append(base + pattern)
        
        # Subdomain-based URLs
        if tenant.domain:
            urls.append(f"https://{tenant.domain}{endpoint}")
        elif tenant.subdomain:
            parsed = urlparse(base_url)
            if parsed.netloc:
                domain_parts = parsed.netloc.split('.')
                if len(domain_parts) >= 2:
                    base_domain = '.'.join(domain_parts[-2:])
                    tenant_domain = f"{tenant.subdomain}.{base_domain}"
                    urls.append(f"{parsed.scheme}://{tenant_domain}{endpoint}")
        
        return urls
    
    async def _test_single_cross_tenant_access(
        self,
        runner: AsyncRequestRunner,
        url: str,
        source_tenant: TenantContext,
        target_tenant: TenantContext,
        endpoint: str
    ) -> TenantTestResult:
        """Test a single cross-tenant access attempt."""
        try:
            response = await runner.send_request(url, method="GET", timeout=self.config.request_timeout)
            
            # Analyze response for isolation breach
            isolation_breach = self._analyze_cross_tenant_response(
                response, source_tenant, target_tenant
            )
            
            evidence = []
            if isolation_breach:
                evidence = self._extract_evidence_from_response(response, target_tenant)
            
            risk_level = "CRITICAL" if isolation_breach else "LOW"
            
            return TenantTestResult(
                test_type=TenantTestType.CROSS_TENANT_ACCESS,
                source_tenant=source_tenant,
                target_tenant=target_tenant,
                endpoint=url,
                success=response.status_code < 400,
                isolation_breach=isolation_breach,
                response_data={
                    "status_code": response.status_code,
                    "content_length": len(response.body),
                    "headers": dict(response.headers)
                },
                evidence=evidence,
                risk_level=risk_level,
                details=f"Cross-tenant access test from {source_tenant.tenant_id} to {target_tenant.tenant_id}"
            )
            
        except Exception as e:
            return TenantTestResult(
                test_type=TenantTestType.CROSS_TENANT_ACCESS,
                source_tenant=source_tenant,
                target_tenant=target_tenant,
                endpoint=url,
                success=False,
                isolation_breach=False,
                evidence=[f"Request failed: {str(e)}"],
                risk_level="LOW",
                details="Request execution failed"
            )
    
    def _analyze_cross_tenant_response(
        self, 
        response, 
        source_tenant: TenantContext, 
        target_tenant: TenantContext
    ) -> bool:
        """Analyze response to determine if tenant isolation was breached."""
        # Check for successful access (should be denied)
        if response.status_code in [200, 201, 202]:
            # Check if response contains target tenant data
            response_text = response.body.lower()
            
            # Look for target tenant identifiers in response
            if target_tenant.tenant_id.lower() in response_text:
                return True
            
            # Look for success indicators that shouldn't be accessible
            for indicator in self.config.success_indicators:
                if indicator.lower() in response_text:
                    return True
        
        return False
    
    def _extract_evidence_from_response(self, response, target_tenant: TenantContext) -> List[str]:
        """Extract evidence of tenant isolation breach from response."""
        evidence = []
        response_text = response.body
        
        # Extract tenant-related data from response
        for pattern in self.config.data_leakage_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    evidence.extend([f"Found tenant data: {m}" for m in match if m])
                else:
                    evidence.append(f"Found tenant data: {match}")
        
        # Look for specific target tenant information
        if target_tenant.tenant_id in response_text:
            evidence.append(f"Response contains target tenant ID: {target_tenant.tenant_id}")
        
        return evidence[:10]  # Limit evidence entries
    
    async def _test_data_leakage(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenants: List[TenantContext]
    ) -> List[TenantTestResult]:
        """Test for data leakage between tenants."""
        results = []
        
        # Endpoints that commonly leak tenant data
        leakage_endpoints = [
            '/api/search',
            '/api/autocomplete',
            '/api/suggestions',
            '/api/logs',
            '/api/audit',
            '/api/export',
            '/api/backup',
            '/health',
            '/debug',
            '/api/stats'
        ]
        
        for endpoint in leakage_endpoints:
            url = base_url.rstrip('/') + endpoint
            
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                
                # Check for tenant data in response
                leaked_tenants = []
                for tenant in target_tenants:
                    if tenant.tenant_id != current_tenant.tenant_id:
                        if tenant.tenant_id.lower() in response.text.lower():
                            leaked_tenants.append(tenant)
                
                if leaked_tenants:
                    for leaked_tenant in leaked_tenants:
                        result = TenantTestResult(
                            test_type=TenantTestType.DATA_LEAKAGE,
                            source_tenant=current_tenant,
                            target_tenant=leaked_tenant,
                            endpoint=url,
                            success=True,
                            isolation_breach=True,
                            evidence=[f"Tenant {leaked_tenant.tenant_id} data found in response"],
                            risk_level="HIGH",
                            details=f"Data leakage detected in {endpoint}"
                        )
                        results.append(result)
                
            except Exception as e:
                log_warning(f"Error testing data leakage at {url}: {str(e)}")
        
        return results
    
    async def _test_context_manipulation(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenants: List[TenantContext]
    ) -> List[TenantTestResult]:
        """Test tenant context manipulation vulnerabilities."""
        results = []
        
        manipulation_techniques = [
            self._test_header_manipulation,
            self._test_parameter_manipulation,
            self._test_cookie_manipulation
        ]
        
        for target_tenant in target_tenants[:5]:  # Limit to avoid overwhelming
            if target_tenant.tenant_id == current_tenant.tenant_id:
                continue
            
            for technique in manipulation_techniques:
                try:
                    result = await technique(base_url, session, current_tenant, target_tenant)
                    if result:
                        results.append(result)
                except Exception as e:
                    log_warning(f"Error in context manipulation test: {str(e)}")
        
        return results
    
    async def _test_header_manipulation(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenant: TenantContext
    ) -> Optional[TenantTestResult]:
        """Test tenant context manipulation via HTTP headers."""
        manipulation_headers = {
            'X-Tenant-ID': target_tenant.tenant_id,
            'X-Org-ID': target_tenant.tenant_id,
            'X-Account-ID': target_tenant.tenant_id,
            'Tenant-ID': target_tenant.tenant_id,
            'Organization': target_tenant.tenant_id
        }
        
        test_url = base_url.rstrip('/') + '/api/profile'
        
        try:
            response = session.get(test_url, headers=manipulation_headers, timeout=self.config.request_timeout)
            
            if (response.status_code == 200 and 
                target_tenant.tenant_id.lower() in response.text.lower()):
                
                return TenantTestResult(
                    test_type=TenantTestType.CONTEXT_MANIPULATION,
                    source_tenant=current_tenant,
                    target_tenant=target_tenant,
                    endpoint=test_url,
                    success=True,
                    isolation_breach=True,
                    evidence=[f"Header manipulation successful with headers: {manipulation_headers}"],
                    risk_level="CRITICAL",
                    details="Tenant context manipulation via HTTP headers"
                )
        except Exception:
            pass
        
        return None
    
    async def _test_parameter_manipulation(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenant: TenantContext
    ) -> Optional[TenantTestResult]:
        """Test tenant context manipulation via URL parameters."""
        manipulation_params = {
            'tenant_id': target_tenant.tenant_id,
            'org_id': target_tenant.tenant_id,
            'account_id': target_tenant.tenant_id,
            'workspace_id': target_tenant.tenant_id
        }
        
        test_url = base_url.rstrip('/') + '/api/data'
        
        try:
            response = session.get(test_url, params=manipulation_params, timeout=self.config.request_timeout)
            
            if (response.status_code == 200 and 
                target_tenant.tenant_id.lower() in response.text.lower()):
                
                return TenantTestResult(
                    test_type=TenantTestType.CONTEXT_MANIPULATION,
                    source_tenant=current_tenant,
                    target_tenant=target_tenant,
                    endpoint=test_url,
                    success=True,
                    isolation_breach=True,
                    evidence=[f"Parameter manipulation successful with params: {manipulation_params}"],
                    risk_level="HIGH",
                    details="Tenant context manipulation via URL parameters"
                )
        except Exception:
            pass
        
        return None
    
    async def _test_cookie_manipulation(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext,
        target_tenant: TenantContext
    ) -> Optional[TenantTestResult]:
        """Test tenant context manipulation via cookies."""
        # Save original cookies
        original_cookies = session.cookies.copy()
        
        try:
            # Set tenant manipulation cookies
            session.cookies.set('tenant_id', target_tenant.tenant_id)
            session.cookies.set('org_id', target_tenant.tenant_id)
            session.cookies.set('account_id', target_tenant.tenant_id)
            
            test_url = base_url.rstrip('/') + '/api/profile'
            response = session.get(test_url, timeout=self.config.request_timeout)
            
            if (response.status_code == 200 and 
                target_tenant.tenant_id.lower() in response.text.lower()):
                
                return TenantTestResult(
                    test_type=TenantTestType.CONTEXT_MANIPULATION,
                    source_tenant=current_tenant,
                    target_tenant=target_tenant,
                    endpoint=test_url,
                    success=True,
                    isolation_breach=True,
                    evidence=["Cookie manipulation successful"],
                    risk_level="HIGH",
                    details="Tenant context manipulation via cookies"
                )
        except Exception:
            pass
        finally:
            # Restore original cookies
            session.cookies.clear()
            session.cookies.update(original_cookies)
        
        return None
    
    async def _test_tenant_enumeration(
        self,
        base_url: str,
        session: requests.Session,
        current_tenant: TenantContext
    ) -> List[TenantTestResult]:
        """Test for tenant enumeration vulnerabilities."""
        results = []
        
        # Test if tenant enumeration is possible
        enumerated_tenants = await self.enumerator.enumerate_tenants(base_url, session, [current_tenant.tenant_id])
        
        if len(enumerated_tenants) > 1:  # Found more than just the current tenant
            result = TenantTestResult(
                test_type=TenantTestType.TENANT_ENUMERATION,
                source_tenant=current_tenant,
                target_tenant=None,
                endpoint=base_url,
                success=True,
                isolation_breach=True,
                evidence=[f"Enumerated {len(enumerated_tenants)} tenants"],
                risk_level="MEDIUM",
                details=f"Tenant enumeration revealed {len(enumerated_tenants)} tenant identifiers"
            )
            results.append(result)
        
        return results


def create_tenant_test_config(
    enable_all_tests: bool = True,
    max_concurrent: int = 10,
    custom_patterns: List[str] = None
) -> TenantTestConfig:
    """Create a standard tenant test configuration."""
    config = TenantTestConfig(max_concurrent_tests=max_concurrent)
    
    if custom_patterns:
        config.data_leakage_patterns.extend(custom_patterns)
    
    if not enable_all_tests:
        config.test_types = [TenantTestType.CROSS_TENANT_ACCESS]
    
    return config


async def run_comprehensive_tenant_isolation_test(
    base_url: str,
    session: requests.Session,
    current_tenant_id: str,
    config: Optional[TenantTestConfig] = None
) -> List[TenantTestResult]:
    """
    High-level function to run comprehensive tenant isolation testing.
    
    This is the main entry point for tenant isolation testing.
    """
    config = config or create_tenant_test_config()
    tester = TenantIsolationTester(config)
    
    # Create current tenant context
    current_tenant = TenantContext(
        tenant_id=current_tenant_id,
        tenant_name=current_tenant_id,
        isolation_level=TenantIsolationLevel.DATA
    )
    
    log_info(f"Starting comprehensive tenant isolation test for tenant: {current_tenant_id}")
    
    # Run the comprehensive test
    results = await tester.test_tenant_isolation(base_url, session, current_tenant)
    
    # Analyze and log results
    isolation_breaches = [r for r in results if r.isolation_breach]
    critical_issues = [r for r in results if r.risk_level == "CRITICAL"]
    
    log_info(f"Tenant isolation test completed:")
    log_info(f"  Total tests: {len(results)}")
    log_info(f"  Isolation breaches: {len(isolation_breaches)}")
    log_info(f"  Critical issues: {len(critical_issues)}")
    
    return results
