"""
Role Hierarchy and Privilege Mapping Module for LogicPWN.

Provides comprehensive role-based access control testing including:
- Role hierarchy understanding and mapping
- Systematic role permission testing
- Privilege escalation detection and automation
- Role boundary validation
- Admin function discovery
- Permission matrix analysis
"""

import asyncio
import re
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import requests
from urllib.parse import urljoin, urlparse

from logicpwn.core.logging import log_info, log_warning, log_error
from logicpwn.core.access.models import AccessTestResult, AccessDetectorConfig
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner


class PrivilegeLevel(Enum):
    """Enumeration of privilege levels."""
    ANONYMOUS = "anonymous"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM = "system"


class PermissionType(Enum):
    """Types of permissions to test."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    SYSTEM = "system"


class RoleTestType(Enum):
    """Types of role-based tests."""
    HORIZONTAL_ESCALATION = "horizontal_escalation"
    VERTICAL_ESCALATION = "vertical_escalation"
    PERMISSION_BYPASS = "permission_bypass"
    ADMIN_DISCOVERY = "admin_discovery"
    ROLE_ENUMERATION = "role_enumeration"
    FUNCTION_MAPPING = "function_mapping"


@dataclass
class RoleDefinition:
    """Defines a role with its permissions and hierarchy."""
    role_name: str
    role_id: Optional[str] = None
    privilege_level: PrivilegeLevel = PrivilegeLevel.USER
    permissions: List[str] = field(default_factory=list)
    parent_roles: List[str] = field(default_factory=list)
    child_roles: List[str] = field(default_factory=list)
    accessible_endpoints: List[str] = field(default_factory=list)
    forbidden_endpoints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrivilegeTestResult:
    """Result of a privilege/role-based test."""
    test_type: RoleTestType
    source_role: RoleDefinition
    target_role: Optional[RoleDefinition]
    endpoint: str
    function_name: Optional[str]
    expected_access: bool
    actual_access: bool
    privilege_escalation: bool
    response_data: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    details: str = ""
    timestamp: str = field(default_factory=lambda: str(asyncio.get_event_loop().time()))


@dataclass
class RoleTestConfig:
    """Configuration for role-based testing."""
    test_types: List[RoleTestType] = field(default_factory=lambda: [
        RoleTestType.VERTICAL_ESCALATION,
        RoleTestType.HORIZONTAL_ESCALATION,
        RoleTestType.ADMIN_DISCOVERY
    ])
    max_concurrent_tests: int = 10
    request_timeout: int = 30
    admin_indicators: List[str] = field(default_factory=lambda: [
        "admin", "administrator", "manage", "delete", "create", "update",
        "system", "config", "settings", "users", "permissions", "roles"
    ])
    privilege_indicators: List[str] = field(default_factory=lambda: [
        "privilege", "elevated", "sudo", "root", "superuser", "owner"
    ])
    function_discovery_paths: List[str] = field(default_factory=lambda: [
        "/admin", "/api/admin", "/manage", "/system", "/config",
        "/dashboard/admin", "/panel", "/control", "/supervisor"
    ])
    endpoint_enumeration_depth: int = 3
    role_hierarchy_detection: bool = True


class RoleHierarchyMapper:
    """Maps and understands role hierarchies within applications."""
    
    def __init__(self, config: RoleTestConfig):
        self.config = config
        self.known_roles: Dict[str, RoleDefinition] = {}
        self.hierarchy_cache: Dict[str, List[str]] = {}
    
    def discover_roles(
        self, 
        session: requests.Session, 
        base_url: str,
        known_roles: List[str] = None
    ) -> List[RoleDefinition]:
        """Discover application roles through various techniques."""
        discovered_roles = []
        known_roles = known_roles or []
        
        # Method 1: API endpoint discovery
        api_roles = self._discover_roles_from_api(session, base_url)
        discovered_roles.extend(api_roles)
        
        # Method 2: Error message analysis
        error_roles = self._discover_roles_from_errors(session, base_url)
        discovered_roles.extend(error_roles)
        
        # Method 3: Pattern-based role inference
        pattern_roles = self._infer_roles_from_patterns(known_roles)
        discovered_roles.extend(pattern_roles)
        
        # Method 4: Admin panel discovery
        admin_roles = self._discover_admin_roles(session, base_url)
        discovered_roles.extend(admin_roles)
        
        # Build role hierarchy
        self._build_role_hierarchy(discovered_roles)
        
        return self._deduplicate_roles(discovered_roles)
    
    def _discover_roles_from_api(self, session: requests.Session, base_url: str) -> List[RoleDefinition]:
        """Discover roles from API endpoints."""
        roles = []
        
        # Common role/permission API endpoints
        role_endpoints = [
            "/api/roles",
            "/api/permissions", 
            "/api/users/roles",
            "/api/auth/roles",
            "/api/admin/roles",
            "/api/v1/roles",
            "/roles",
            "/permissions"
        ]
        
        for endpoint in role_endpoints:
            url = urljoin(base_url, endpoint)
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                if response.status_code == 200:
                    extracted_roles = self._extract_roles_from_response(response.text)
                    roles.extend(extracted_roles)
            except Exception as e:
                log_warning(f"Error accessing role endpoint {url}: {str(e)}")
        
        return roles
    
    def _extract_roles_from_response(self, response_text: str) -> List[RoleDefinition]:
        """Extract role information from API response."""
        roles = []
        
        # Common role patterns in JSON responses
        role_patterns = [
            r'"role":\s*"([^"]+)"',
            r'"role_name":\s*"([^"]+)"',
            r'"name":\s*"([^"]+)"',
            r'"type":\s*"([^"]+)"',
            r'"permission":\s*"([^"]+)"'
        ]
        
        role_names = set()
        for pattern in role_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 2:
                    role_names.add(match.lower())
        
        # Filter and create role definitions
        for role_name in role_names:
            if self._is_valid_role_name(role_name):
                privilege_level = self._infer_privilege_level(role_name)
                role_def = RoleDefinition(
                    role_name=role_name,
                    privilege_level=privilege_level,
                    metadata={"discovery_method": "api_extraction"}
                )
                roles.append(role_def)
        
        return roles
    
    def _is_valid_role_name(self, role_name: str) -> bool:
        """Validate if a discovered string is likely a role name."""
        # Filter out common false positives
        invalid_patterns = [
            "null", "undefined", "none", "true", "false", "yes", "no",
            "email", "password", "token", "id", "url", "http", "www"
        ]
        
        role_lower = role_name.lower()
        if role_lower in invalid_patterns:
            return False
        
        # Check for role-like patterns
        role_indicators = [
            "admin", "user", "guest", "member", "owner", "manager",
            "moderator", "supervisor", "operator", "viewer", "editor"
        ]
        
        return any(indicator in role_lower for indicator in role_indicators)
    
    def _infer_privilege_level(self, role_name: str) -> PrivilegeLevel:
        """Infer privilege level from role name."""
        role_lower = role_name.lower()
        
        if any(admin in role_lower for admin in ["admin", "administrator", "root", "super"]):
            if "super" in role_lower:
                return PrivilegeLevel.SUPER_ADMIN
            return PrivilegeLevel.ADMIN
        
        if any(mod in role_lower for mod in ["moderator", "manager", "supervisor"]):
            return PrivilegeLevel.MODERATOR
        
        if any(user in role_lower for user in ["user", "member", "customer"]):
            return PrivilegeLevel.USER
        
        if "guest" in role_lower or "anonymous" in role_lower:
            return PrivilegeLevel.ANONYMOUS
        
        return PrivilegeLevel.USER  # Default
    
    def _discover_roles_from_errors(self, session: requests.Session, base_url: str) -> List[RoleDefinition]:
        """Discover roles from error messages and access denied responses."""
        roles = []
        
        # Test URLs that might reveal role information in errors
        test_urls = [
            "/admin",
            "/admin/users",
            "/api/admin/settings",
            "/dashboard/admin",
            "/system/config",
            "/manage",
            "/control-panel"
        ]
        
        for path in test_urls:
            url = urljoin(base_url, path)
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                
                # Look for role information in error messages
                if response.status_code in [401, 403]:
                    role_hints = self._extract_role_hints_from_error(response.text)
                    for hint in role_hints:
                        role_def = RoleDefinition(
                            role_name=hint,
                            privilege_level=self._infer_privilege_level(hint),
                            metadata={"discovery_method": "error_analysis", "source_url": url}
                        )
                        roles.append(role_def)
            except Exception:
                continue
        
        return roles
    
    def _extract_role_hints_from_error(self, error_text: str) -> List[str]:
        """Extract role hints from error messages."""
        role_hints = []
        
        # Common error message patterns that reveal roles
        error_patterns = [
            r"requires?\s+([a-zA-Z_]+)\s+(?:role|permission)",
            r"only\s+([a-zA-Z_]+)s?\s+can\s+access",
            r"([a-zA-Z_]+)\s+(?:role|permission)\s+required",
            r"insufficient\s+([a-zA-Z_]+)\s+privileges",
            r"must\s+be\s+(?:an?\s+)?([a-zA-Z_]+)"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, error_text, re.IGNORECASE)
            for match in matches:
                if self._is_valid_role_name(match):
                    role_hints.append(match.lower())
        
        return list(set(role_hints))
    
    def _infer_roles_from_patterns(self, known_roles: List[str]) -> List[RoleDefinition]:
        """Infer additional roles based on known role patterns."""
        inferred_roles = []
        
        if not known_roles:
            # Default role set
            default_roles = ["admin", "user", "guest", "moderator", "manager"]
            for role in default_roles:
                role_def = RoleDefinition(
                    role_name=role,
                    privilege_level=self._infer_privilege_level(role),
                    metadata={"discovery_method": "pattern_inference"}
                )
                inferred_roles.append(role_def)
            return inferred_roles
        
        # Generate role variations based on known roles
        role_variations = []
        for role in known_roles:
            variations = self._generate_role_variations(role)
            role_variations.extend(variations)
        
        for variation in role_variations:
            role_def = RoleDefinition(
                role_name=variation,
                privilege_level=self._infer_privilege_level(variation),
                metadata={"discovery_method": "pattern_inference", "base_role": known_roles[0]}
            )
            inferred_roles.append(role_def)
        
        return inferred_roles
    
    def _generate_role_variations(self, base_role: str) -> List[str]:
        """Generate variations of a base role name."""
        variations = []
        
        # Common role prefixes and suffixes
        prefixes = ["super_", "sub_", "junior_", "senior_", "lead_"]
        suffixes = ["_admin", "_user", "_manager", "_operator", "_viewer"]
        
        for prefix in prefixes:
            variations.append(f"{prefix}{base_role}")
        
        for suffix in suffixes:
            variations.append(f"{base_role}{suffix}")
        
        # Plural/singular variations
        if base_role.endswith('s'):
            variations.append(base_role[:-1])
        else:
            variations.append(f"{base_role}s")
        
        return variations
    
    def _discover_admin_roles(self, session: requests.Session, base_url: str) -> List[RoleDefinition]:
        """Discover admin-specific roles and functions."""
        admin_roles = []
        
        for path in self.config.function_discovery_paths:
            url = urljoin(base_url, path)
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                
                # Look for admin function indicators
                if response.status_code < 400:
                    admin_functions = self._extract_admin_functions(response.text, url)
                    
                    # Create admin role definitions based on discovered functions
                    for function in admin_functions:
                        role_def = RoleDefinition(
                            role_name=f"admin_{function}",
                            privilege_level=PrivilegeLevel.ADMIN,
                            accessible_endpoints=[url],
                            metadata={
                                "discovery_method": "admin_discovery",
                                "function": function,
                                "source_url": url
                            }
                        )
                        admin_roles.append(role_def)
            except Exception:
                continue
        
        return admin_roles
    
    def _extract_admin_functions(self, html_content: str, source_url: str) -> List[str]:
        """Extract admin function names from page content."""
        functions = []
        
        # Look for admin-related links, buttons, and text
        admin_patterns = [
            r'(?:href|action)=["\']([^"\']*(?:' + '|'.join(self.config.admin_indicators) + r')[^"\']*)["\']',
            r'(?:id|class)=["\']([^"\']*(?:' + '|'.join(self.config.admin_indicators) + r')[^"\']*)["\']',
            r'>([^<]*(?:' + '|'.join(self.config.admin_indicators) + r')[^<]*)<'
        ]
        
        for pattern in admin_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 3:
                    # Clean and extract function name
                    function = re.sub(r'[^a-zA-Z_]', '_', match.lower())
                    if any(indicator in function for indicator in self.config.admin_indicators):
                        functions.append(function)
        
        return list(set(functions))[:20]  # Limit results
    
    def _build_role_hierarchy(self, roles: List[RoleDefinition]) -> None:
        """Build role hierarchy relationships."""
        if not self.config.role_hierarchy_detection:
            return
        
        # Sort roles by privilege level
        privilege_order = {
            PrivilegeLevel.ANONYMOUS: 0,
            PrivilegeLevel.USER: 1,
            PrivilegeLevel.MODERATOR: 2,
            PrivilegeLevel.ADMIN: 3,
            PrivilegeLevel.SUPER_ADMIN: 4,
            PrivilegeLevel.SYSTEM: 5
        }
        
        roles.sort(key=lambda r: privilege_order.get(r.privilege_level, 1))
        
        # Build hierarchy relationships
        for i, role in enumerate(roles):
            # Set parent roles (higher privilege)
            for j in range(i + 1, len(roles)):
                parent_role = roles[j]
                if privilege_order.get(parent_role.privilege_level, 1) > privilege_order.get(role.privilege_level, 1):
                    role.parent_roles.append(parent_role.role_name)
                    parent_role.child_roles.append(role.role_name)
    
    def _deduplicate_roles(self, roles: List[RoleDefinition]) -> List[RoleDefinition]:
        """Remove duplicate role definitions."""
        seen_names = set()
        unique_roles = []
        
        for role in roles:
            if role.role_name not in seen_names:
                seen_names.add(role.role_name)
                unique_roles.append(role)
                self.known_roles[role.role_name] = role
        
        return unique_roles


class PrivilegeEscalationTester:
    """Tests for privilege escalation vulnerabilities."""
    
    def __init__(self, config: RoleTestConfig):
        self.config = config
        self.role_mapper = RoleHierarchyMapper(config)
        self.discovered_functions: Dict[str, List[str]] = {}
    
    async def test_privilege_escalation(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition,
        target_roles: List[RoleDefinition] = None
    ) -> List[PrivilegeTestResult]:
        """Comprehensive privilege escalation testing."""
        results = []
        
        # Discover roles if not provided
        if not target_roles:
            target_roles = self.role_mapper.discover_roles(session, base_url)
        
        # Execute different types of privilege tests
        for test_type in self.config.test_types:
            if test_type == RoleTestType.VERTICAL_ESCALATION:
                test_results = await self._test_vertical_escalation(
                    base_url, session, current_role, target_roles
                )
                results.extend(test_results)
            
            elif test_type == RoleTestType.HORIZONTAL_ESCALATION:
                test_results = await self._test_horizontal_escalation(
                    base_url, session, current_role, target_roles
                )
                results.extend(test_results)
            
            elif test_type == RoleTestType.ADMIN_DISCOVERY:
                test_results = await self._test_admin_function_discovery(
                    base_url, session, current_role
                )
                results.extend(test_results)
            
            elif test_type == RoleTestType.PERMISSION_BYPASS:
                test_results = await self._test_permission_bypass(
                    base_url, session, current_role, target_roles
                )
                results.extend(test_results)
            
            elif test_type == RoleTestType.FUNCTION_MAPPING:
                test_results = await self._test_function_mapping(
                    base_url, session, current_role
                )
                results.extend(test_results)
        
        return results
    
    async def _test_vertical_escalation(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition,
        target_roles: List[RoleDefinition]
    ) -> List[PrivilegeTestResult]:
        """Test vertical privilege escalation (lower to higher privileges)."""
        results = []
        
        # Find higher privilege roles
        current_privilege = self._get_privilege_value(current_role.privilege_level)
        higher_roles = [
            role for role in target_roles 
            if self._get_privilege_value(role.privilege_level) > current_privilege
        ]
        
        # Test access to higher privilege functions
        async with AsyncRequestRunner(max_concurrent=self.config.max_concurrent_tests) as runner:
            tasks = []
            
            for target_role in higher_roles:
                # Generate admin/privileged endpoints to test
                privileged_endpoints = self._generate_privileged_endpoints(base_url, target_role)
                
                for endpoint in privileged_endpoints:
                    tasks.append(
                        self._test_single_privilege_escalation(
                            runner, endpoint, current_role, target_role, 
                            RoleTestType.VERTICAL_ESCALATION
                        )
                    )
            
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [r for r in test_results if isinstance(r, PrivilegeTestResult)]
        
        return results
    
    async def _test_horizontal_escalation(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition,
        target_roles: List[RoleDefinition]
    ) -> List[PrivilegeTestResult]:
        """Test horizontal privilege escalation (same level, different user)."""
        results = []
        
        # Find roles at the same privilege level
        current_privilege = self._get_privilege_value(current_role.privilege_level)
        same_level_roles = [
            role for role in target_roles 
            if (self._get_privilege_value(role.privilege_level) == current_privilege and
                role.role_name != current_role.role_name)
        ]
        
        # Test access to same-level user resources
        for target_role in same_level_roles:
            user_endpoints = self._generate_user_specific_endpoints(base_url, target_role)
            
            for endpoint in user_endpoints:
                try:
                    response = session.get(endpoint, timeout=self.config.request_timeout)
                    
                    # Check if access was granted when it shouldn't be
                    access_granted = response.status_code < 400
                    should_have_access = False  # Horizontal escalation should be denied
                    
                    if access_granted and not should_have_access:
                        result = PrivilegeTestResult(
                            test_type=RoleTestType.HORIZONTAL_ESCALATION,
                            source_role=current_role,
                            target_role=target_role,
                            endpoint=endpoint,
                            function_name=self._extract_function_name(endpoint),
                            expected_access=should_have_access,
                            actual_access=access_granted,
                            privilege_escalation=True,
                            evidence=[f"Unauthorized access to {target_role.role_name} resources"],
                            risk_level="HIGH",
                            details="Horizontal privilege escalation detected"
                        )
                        results.append(result)
                
                except Exception as e:
                    log_warning(f"Error testing horizontal escalation at {endpoint}: {str(e)}")
        
        return results
    
    def _get_privilege_value(self, privilege_level: PrivilegeLevel) -> int:
        """Get numeric value for privilege level comparison."""
        privilege_values = {
            PrivilegeLevel.ANONYMOUS: 0,
            PrivilegeLevel.USER: 1,
            PrivilegeLevel.MODERATOR: 2,
            PrivilegeLevel.ADMIN: 3,
            PrivilegeLevel.SUPER_ADMIN: 4,
            PrivilegeLevel.SYSTEM: 5
        }
        return privilege_values.get(privilege_level, 1)
    
    def _generate_privileged_endpoints(self, base_url: str, target_role: RoleDefinition) -> List[str]:
        """Generate endpoints that should require elevated privileges."""
        endpoints = []
        base = base_url.rstrip('/')
        
        # Admin function endpoints
        admin_paths = [
            "/admin/users",
            "/admin/settings", 
            "/admin/system",
            "/admin/logs",
            "/api/admin/users",
            "/api/admin/config",
            "/api/admin/permissions",
            "/manage/users",
            "/manage/system",
            "/system/config",
            "/dashboard/admin"
        ]
        
        for path in admin_paths:
            endpoints.append(base + path)
        
        # Role-specific endpoints if available
        if target_role.accessible_endpoints:
            endpoints.extend(target_role.accessible_endpoints)
        
        return endpoints
    
    def _generate_user_specific_endpoints(self, base_url: str, target_role: RoleDefinition) -> List[str]:
        """Generate user-specific endpoints for horizontal escalation testing."""
        endpoints = []
        base = base_url.rstrip('/')
        
        # User-specific resource patterns
        user_patterns = [
            f"/api/users/{target_role.role_name}",
            f"/api/users/{target_role.role_name}/profile",
            f"/api/users/{target_role.role_name}/settings",
            f"/users/{target_role.role_name}",
            f"/profile/{target_role.role_name}",
            f"/account/{target_role.role_name}"
        ]
        
        for pattern in user_patterns:
            endpoints.append(base + pattern)
        
        return endpoints
    
    async def _test_single_privilege_escalation(
        self,
        runner: AsyncRequestRunner,
        endpoint: str,
        source_role: RoleDefinition,
        target_role: RoleDefinition,
        test_type: RoleTestType
    ) -> PrivilegeTestResult:
        """Test a single privilege escalation attempt."""
        try:
            response = await runner.send_request(endpoint, method="GET", timeout=self.config.request_timeout)
            
            access_granted = response.status_code < 400
            should_have_access = self._should_role_have_access(source_role, target_role, endpoint)
            privilege_escalation = access_granted and not should_have_access
            
            evidence = []
            if privilege_escalation:
                evidence = self._extract_escalation_evidence(response, target_role)
            
            risk_level = "CRITICAL" if privilege_escalation else "LOW"
            
            return PrivilegeTestResult(
                test_type=test_type,
                source_role=source_role,
                target_role=target_role,
                endpoint=endpoint,
                function_name=self._extract_function_name(endpoint),
                expected_access=should_have_access,
                actual_access=access_granted,
                privilege_escalation=privilege_escalation,
                response_data={
                    "status_code": response.status_code,
                    "content_length": len(response.body)
                },
                evidence=evidence,
                risk_level=risk_level,
                details=f"Privilege escalation test from {source_role.role_name} to {target_role.role_name}"
            )
            
        except Exception as e:
            return PrivilegeTestResult(
                test_type=test_type,
                source_role=source_role,
                target_role=target_role,
                endpoint=endpoint,
                function_name=self._extract_function_name(endpoint),
                expected_access=False,
                actual_access=False,
                privilege_escalation=False,
                evidence=[f"Request failed: {str(e)}"],
                risk_level="LOW",
                details="Request execution failed"
            )
    
    def _should_role_have_access(
        self, 
        source_role: RoleDefinition, 
        target_role: RoleDefinition, 
        endpoint: str
    ) -> bool:
        """Determine if source role should have access to target role's resources."""
        # Check role hierarchy
        source_privilege = self._get_privilege_value(source_role.privilege_level)
        target_privilege = self._get_privilege_value(target_role.privilege_level)
        
        # Higher or equal privilege should have access
        if source_privilege >= target_privilege:
            return True
        
        # Check explicit permissions
        if endpoint in source_role.accessible_endpoints:
            return True
        
        # Check if it's explicitly forbidden
        if endpoint in source_role.forbidden_endpoints:
            return False
        
        # Default: lower privilege should not access higher privilege resources
        return False
    
    def _extract_escalation_evidence(self, response, target_role: RoleDefinition) -> List[str]:
        """Extract evidence of privilege escalation from response."""
        evidence = []
        response_text = response.body.lower()
        
        # Look for admin/privilege indicators in response
        for indicator in self.config.admin_indicators:
            if indicator in response_text:
                evidence.append(f"Found admin indicator: {indicator}")
        
        for indicator in self.config.privilege_indicators:
            if indicator in response_text:
                evidence.append(f"Found privilege indicator: {indicator}")
        
        # Look for target role information
        if target_role.role_name.lower() in response_text:
            evidence.append(f"Response contains target role: {target_role.role_name}")
        
        return evidence[:10]  # Limit evidence entries
    
    def _extract_function_name(self, endpoint: str) -> Optional[str]:
        """Extract function name from endpoint URL."""
        parsed = urlparse(endpoint)
        path_parts = [part for part in parsed.path.split('/') if part]
        
        if path_parts:
            # Return the last meaningful part
            return path_parts[-1]
        
        return None
    
    async def _test_admin_function_discovery(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition
    ) -> List[PrivilegeTestResult]:
        """Discover and test admin functions."""
        results = []
        
        # Discover admin functions
        admin_functions = await self._discover_admin_functions(base_url, session)
        
        # Test each discovered function
        for function_name, endpoint in admin_functions.items():
            try:
                response = session.get(endpoint, timeout=self.config.request_timeout)
                
                access_granted = response.status_code < 400
                should_have_access = self._should_role_access_admin(current_role)
                escalation = access_granted and not should_have_access
                
                result = PrivilegeTestResult(
                    test_type=RoleTestType.ADMIN_DISCOVERY,
                    source_role=current_role,
                    target_role=None,
                    endpoint=endpoint,
                    function_name=function_name,
                    expected_access=should_have_access,
                    actual_access=access_granted,
                    privilege_escalation=escalation,
                    evidence=[f"Discovered admin function: {function_name}"],
                    risk_level="HIGH" if escalation else "MEDIUM",
                    details=f"Admin function discovery: {function_name}"
                )
                results.append(result)
                
            except Exception as e:
                log_warning(f"Error testing admin function {function_name}: {str(e)}")
        
        return results
    
    async def _discover_admin_functions(self, base_url: str, session: requests.Session) -> Dict[str, str]:
        """Discover admin functions and their endpoints."""
        functions = {}
        
        for discovery_path in self.config.function_discovery_paths:
            url = urljoin(base_url, discovery_path)
            try:
                response = session.get(url, timeout=self.config.request_timeout)
                if response.status_code < 400:
                    page_functions = self._extract_functions_from_page(response.text, url)
                    functions.update(page_functions)
            except Exception:
                continue
        
        return functions
    
    def _extract_functions_from_page(self, html_content: str, base_url: str) -> Dict[str, str]:
        """Extract function names and URLs from HTML page."""
        functions = {}
        
        # Extract links and forms that might be admin functions
        link_patterns = [
            r'href=["\']([^"\']*(?:' + '|'.join(self.config.admin_indicators) + r')[^"\']*)["\']',
            r'action=["\']([^"\']*(?:' + '|'.join(self.config.admin_indicators) + r')[^"\']*)["\']'
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and not match.startswith('#'):
                    function_name = self._derive_function_name(match)
                    if function_name:
                        full_url = urljoin(base_url, match)
                        functions[function_name] = full_url
        
        return functions
    
    def _derive_function_name(self, url_path: str) -> Optional[str]:
        """Derive a function name from URL path."""
        # Extract meaningful part from URL
        path_parts = [part for part in url_path.split('/') if part and part != '..']
        
        if path_parts:
            function_part = path_parts[-1]
            # Clean up the function name
            function_name = re.sub(r'[^a-zA-Z0-9_]', '_', function_part)
            if len(function_name) > 2 and any(indicator in function_name.lower() for indicator in self.config.admin_indicators):
                return function_name
        
        return None
    
    def _should_role_access_admin(self, role: RoleDefinition) -> bool:
        """Check if role should have admin access."""
        return role.privilege_level in [PrivilegeLevel.ADMIN, PrivilegeLevel.SUPER_ADMIN, PrivilegeLevel.SYSTEM]
    
    async def _test_permission_bypass(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition,
        target_roles: List[RoleDefinition]
    ) -> List[PrivilegeTestResult]:
        """Test for permission bypass vulnerabilities."""
        results = []
        
        # Test various bypass techniques
        bypass_techniques = [
            self._test_parameter_bypass,
            self._test_header_bypass,
            self._test_method_bypass
        ]
        
        for target_role in target_roles:
            if target_role.role_name == current_role.role_name:
                continue
            
            privileged_endpoints = self._generate_privileged_endpoints(base_url, target_role)
            
            for endpoint in privileged_endpoints[:5]:  # Limit to avoid overwhelming
                for technique in bypass_techniques:
                    try:
                        result = await technique(endpoint, current_role, target_role)
                        if result and result.privilege_escalation:
                            results.append(result)
                    except Exception as e:
                        log_warning(f"Error in permission bypass test: {str(e)}")
        
        return results
    
    async def _test_parameter_bypass(
        self,
        endpoint: str,
        source_role: RoleDefinition,
        target_role: RoleDefinition
    ) -> Optional[PrivilegeTestResult]:
        """Test permission bypass via URL parameters."""
        bypass_params = {
            'admin': 'true',
            'role': target_role.role_name,
            'privilege': 'admin',
            'elevated': 'true',
            'bypass': 'true'
        }
        
        # This would need to be implemented with actual request logic
        # For now, return a placeholder result
        return None
    
    async def _test_header_bypass(
        self,
        endpoint: str,
        source_role: RoleDefinition,
        target_role: RoleDefinition
    ) -> Optional[PrivilegeTestResult]:
        """Test permission bypass via HTTP headers."""
        # Implementation would test various header-based bypasses
        return None
    
    async def _test_method_bypass(
        self,
        endpoint: str,
        source_role: RoleDefinition,
        target_role: RoleDefinition
    ) -> Optional[PrivilegeTestResult]:
        """Test permission bypass via HTTP method manipulation."""
        # Implementation would test method overrides
        return None
    
    async def _test_function_mapping(
        self,
        base_url: str,
        session: requests.Session,
        current_role: RoleDefinition
    ) -> List[PrivilegeTestResult]:
        """Map accessible functions for the current role."""
        results = []
        
        # Test a wide range of endpoints to map accessible functions
        test_endpoints = self._generate_comprehensive_endpoint_list(base_url)
        
        for endpoint in test_endpoints:
            try:
                response = session.get(endpoint, timeout=self.config.request_timeout)
                
                if response.status_code < 400:
                    function_name = self._extract_function_name(endpoint)
                    
                    result = PrivilegeTestResult(
                        test_type=RoleTestType.FUNCTION_MAPPING,
                        source_role=current_role,
                        target_role=None,
                        endpoint=endpoint,
                        function_name=function_name,
                        expected_access=True,  # We're mapping what's accessible
                        actual_access=True,
                        privilege_escalation=False,
                        evidence=[f"Function accessible to {current_role.role_name}"],
                        risk_level="INFO",
                        details=f"Function mapping for {current_role.role_name}"
                    )
                    results.append(result)
                    
            except Exception:
                continue
        
        return results
    
    def _generate_comprehensive_endpoint_list(self, base_url: str) -> List[str]:
        """Generate comprehensive list of endpoints for function mapping."""
        endpoints = []
        base = base_url.rstrip('/')
        
        # Common endpoint patterns
        patterns = [
            "/api/users", "/api/profile", "/api/settings", "/api/data",
            "/api/reports", "/api/admin", "/api/manage", "/api/system",
            "/dashboard", "/profile", "/settings", "/admin", "/manage",
            "/users", "/reports", "/logs", "/config", "/system"
        ]
        
        for pattern in patterns:
            endpoints.append(base + pattern)
        
        return endpoints


def create_role_test_config(
    enable_all_tests: bool = True,
    max_concurrent: int = 10,
    admin_functions_only: bool = False
) -> RoleTestConfig:
    """Create a standard role test configuration."""
    config = RoleTestConfig(max_concurrent_tests=max_concurrent)
    
    if admin_functions_only:
        config.test_types = [RoleTestType.ADMIN_DISCOVERY]
    elif not enable_all_tests:
        config.test_types = [RoleTestType.VERTICAL_ESCALATION]
    
    return config


async def run_comprehensive_privilege_escalation_test(
    base_url: str,
    session: requests.Session,
    current_role_name: str,
    config: Optional[RoleTestConfig] = None
) -> List[PrivilegeTestResult]:
    """
    High-level function to run comprehensive privilege escalation testing.
    
    This is the main entry point for privilege escalation testing.
    """
    config = config or create_role_test_config()
    tester = PrivilegeEscalationTester(config)
    
    # Create current role context
    current_role = RoleDefinition(
        role_name=current_role_name,
        privilege_level=PrivilegeLevel.USER  # Will be refined during discovery
    )
    
    log_info(f"Starting comprehensive privilege escalation test for role: {current_role_name}")
    
    # Discover roles first
    discovered_roles = tester.role_mapper.discover_roles(session, base_url, [current_role_name])
    
    # Update current role with discovered information
    for role in discovered_roles:
        if role.role_name == current_role_name:
            current_role = role
            break
    
    # Run the comprehensive test
    results = await tester.test_privilege_escalation(base_url, session, current_role, discovered_roles)
    
    # Analyze and log results
    escalations = [r for r in results if r.privilege_escalation]
    critical_issues = [r for r in results if r.risk_level == "CRITICAL"]
    admin_discoveries = [r for r in results if r.test_type == RoleTestType.ADMIN_DISCOVERY]
    
    log_info(f"Privilege escalation test completed:")
    log_info(f"  Total tests: {len(results)}")
    log_info(f"  Privilege escalations: {len(escalations)}")
    log_info(f"  Critical issues: {len(critical_issues)}")
    log_info(f"  Admin functions discovered: {len(admin_discoveries)}")
    
    return results
