"""
Enhanced integration utilities for LogicPwn auth, validator, and performance modules.
This module provides high-level functions that combine authentication, validation, and performance monitoring.
"""
from typing import Dict, List, Optional, Union, Any
import time
from loguru import logger

from logicpwn.core.auth import (
    AuthConfig, 
    LogicPwnHTTPClient, 
    authenticate_session_advanced,
    CSRFConfig,
    create_csrf_config
)
from logicpwn.core.validator import (
    validate_response,
    validate_with_preset,
    ValidationResult,
    ValidationConfig,
    list_available_presets
)
from logicpwn.core.performance import (
    monitor_performance,
    PerformanceMonitor,
    PerformanceMetrics
)
from logicpwn.models.request_result import RequestResult
from logicpwn.exceptions import AuthenticationError, ValidationError, NetworkError


class AuthenticatedValidator:
    """
    High-level class that combines authentication, HTTP requests, validation, and performance monitoring.
    """
    
    def __init__(self, 
                                     auth_config: Union[AuthConfig, Dict[str, Any]],
                                     base_url: str = "",
                                     enable_performance_monitoring: bool = True):
                            """
                            Initialize authenticated validator with integrated monitoring.
                            
                            Args:
                                auth_config: Authentication configuration
                                base_url: Base URL for HTTP requests
                                enable_performance_monitoring: Whether to enable performance monitoring
                            """
                            self.auth_config = auth_config if isinstance(auth_config, AuthConfig) else AuthConfig(**auth_config)
                            self.base_url = base_url
                            self.enable_monitoring = enable_performance_monitoring
                            self.client: Optional[LogicPwnHTTPClient] = None
                            self.performance_monitor = PerformanceMonitor() if enable_performance_monitoring else None
                            self._metrics: List[PerformanceMetrics] = []
                            
    @monitor_performance("authenticated_client_creation")
    def authenticate(self) -> bool:
                            """
                            Authenticate and create HTTP client with performance monitoring.
                            
                            Returns:
                                True if authentication successful, False otherwise
                            """
                            try:
                                self.client = authenticate_session_advanced(self.auth_config, self.base_url)
                                logger.info(f"Successfully authenticated to {self.auth_config.url}")
                                return True
                            except Exception as e:
                                logger.error(f"Authentication failed: {e}")
                                return False
    
    @monitor_performance("authenticated_request_with_validation")
    def request_and_validate(self,
                                               method: str,
                                               url: str,
                                               validation_config: Optional[Union[ValidationConfig, str, Dict[str, Any]]] = None,
                                               validation_preset: Optional[str] = None,
                                               **request_kwargs) -> Dict[str, Any]:
                            """
                            Make authenticated request and validate response with performance monitoring.
                            
                            Args:
                                method: HTTP method
                                url: Request URL
                                validation_config: Validation configuration or preset name
                                validation_preset: Preset name for validation
                                **request_kwargs: Additional request arguments
                                
                            Returns:
                                Dictionary containing request result, validation result, and metrics
                            """
                            if not self.client:
                                raise AuthenticationError("Client not authenticated. Call authenticate() first.")
                            
                            start_time = time.time()
                            
                            try:
                                # Make authenticated request
                                with self.performance_monitor if self.enable_monitoring else nullcontext():
                                    if method.upper() == 'GET':
                                        result = self.client.get(url, **request_kwargs)
                                    elif method.upper() == 'POST':
                                        result = self.client.post(url, **request_kwargs)
                                    elif method.upper() == 'PUT':
                                        result = self.client.put(url, **request_kwargs)
                                    elif method.upper() == 'DELETE':
                                        result = self.client.delete(url, **request_kwargs)
                                    else:
                                        result = self.client.request(method, url, **request_kwargs)
                                
                                # Convert RequestResult to a response-like object for validation
                                mock_response = self._create_mock_response(result)
                                
                                # Validate response
                                validation_result = None
                                if validation_preset:
                                    validation_result = validate_with_preset(mock_response, validation_preset)
                                elif validation_config:
                                    if isinstance(validation_config, str):
                                        validation_result = validate_with_preset(mock_response, validation_config)
                                    elif isinstance(validation_config, dict):
                                        validation_result = validate_response(mock_response, return_structured=True, **validation_config)
                                    elif isinstance(validation_config, ValidationConfig):
                                        validation_result = validate_response(
                                            mock_response,
                                            success_criteria=validation_config.success_criteria,
                                            failure_criteria=validation_config.failure_criteria,
                                            regex_patterns=validation_config.regex_patterns,
                                            status_codes=validation_config.status_codes,
                                            headers_criteria=validation_config.headers_criteria,
                                            return_structured=True,
                                            confidence_threshold=validation_config.confidence_threshold
                                        )
                                
                                duration = time.time() - start_time
                                
                                return {
                                    'request_result': result,
                                    'validation_result': validation_result,
                                    'success': result.status_code < 400 and (validation_result is None or validation_result.is_valid),
                                    'duration': duration,
                                    'performance_metrics': self.get_latest_metrics() if self.enable_monitoring else None
                                }
                                
                            except Exception as e:
                                logger.error(f"Request and validation failed: {e}")
                                return {
                                    'request_result': None,
                                    'validation_result': ValidationResult(is_valid=False, error_message=str(e)),
                                    'success': False,
                                    'duration': time.time() - start_time,
                                    'error': str(e)
                                }
    
    def _create_mock_response(self, request_result: RequestResult):
                            """Create a mock response object from RequestResult for validation."""
                            class MockResponse:
                                def __init__(self, result: RequestResult):
                                    self.text = result.body or ""
                                    self.status_code = result.status_code
                                    self.headers = result.headers or {}
                                    
                            return MockResponse(request_result)
    
    @monitor_performance("bulk_validation_test")
    def test_multiple_endpoints(self,
                                                   endpoints: List[Dict[str, Any]],
                                                   validation_preset: str = "login_success") -> List[Dict[str, Any]]:
                            """
                            Test multiple endpoints with validation and performance monitoring.
                            
                            Args:
                                endpoints: List of endpoint configurations with 'method', 'url', and optional 'data'
                                validation_preset: Validation preset to use for all endpoints
                                
                            Returns:
                                List of test results for each endpoint
                            """
                            if not self.client:
                                raise AuthenticationError("Client not authenticated. Call authenticate() first.")
                            
                            results = []
                            
                            for i, endpoint in enumerate(endpoints):
                                logger.info(f"Testing endpoint {i+1}/{len(endpoints)}: {endpoint.get('method', 'GET')} {endpoint['url']}")
                                
                                result = self.request_and_validate(
                                    method=endpoint.get('method', 'GET'),
                                    url=endpoint['url'],
                                    validation_preset=validation_preset,
                                    data=endpoint.get('data'),
                                    params=endpoint.get('params'),
                                    headers=endpoint.get('headers')
                                )
                                
                                results.append({
                                    'endpoint': endpoint,
                                    'result': result,
                                    'endpoint_index': i
                                })
                                
                            return results
    
    def get_latest_metrics(self) -> Optional[PerformanceMetrics]:
                            """Get the latest performance metrics."""
                            if self.performance_monitor and self.performance_monitor.metrics:
                                return self.performance_monitor.metrics[-1]
                            return None
    
    def get_all_metrics(self) -> List[PerformanceMetrics]:
                            """Get all performance metrics collected."""
                            if self.performance_monitor:
                                return self.performance_monitor.metrics
                            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
                            """Get a summary of performance metrics."""
                            if not self.performance_monitor or not self.performance_monitor.metrics:
                                return {"message": "No performance data available"}
                            
                            metrics = self.performance_monitor.metrics
                            durations = [m.duration for m in metrics]
                            memory_usage = [m.memory_after - m.memory_before for m in metrics]
                            cpu_usage = [m.cpu_percent for m in metrics]
                            
                            return {
                                "total_operations": len(metrics),
                                "total_duration": sum(durations),
                                "average_duration": sum(durations) / len(durations),
                                "min_duration": min(durations),
                                "max_duration": max(durations),
                                "average_memory_usage": sum(memory_usage) / len(memory_usage),
                                "average_cpu_usage": sum(cpu_usage) / len(cpu_usage),
                                "operations": [m.operation_name for m in metrics]
                            }
    
    def close(self):
                            """Clean up resources."""
                            if self.client:
                                self.client.close()


# Helper context manager for optional performance monitoring
class nullcontext:
    """Null context manager for when performance monitoring is disabled."""
    def __enter__(self):
                            return self
    def __exit__(self, *args):
                            pass


def create_authenticated_validator(auth_config: Union[AuthConfig, Dict[str, Any]], 
                                                     base_url: str = "",
                                                     auto_authenticate: bool = True,
                                                     enable_monitoring: bool = True) -> AuthenticatedValidator:
    """
    Factory function to create and optionally authenticate a validator.
    
    Args:
                            auth_config: Authentication configuration
                            base_url: Base URL for requests
                            auto_authenticate: Whether to authenticate immediately
                            enable_monitoring: Whether to enable performance monitoring
                            
    Returns:
                            Configured AuthenticatedValidator instance
    """
    validator = AuthenticatedValidator(auth_config, base_url, enable_monitoring)
    
    if auto_authenticate:
                            if not validator.authenticate():
                                raise AuthenticationError("Failed to authenticate validator")
    
    return validator


@monitor_performance("quick_auth_validation_test")
def quick_auth_test(url: str,
                                       username: str,
                                       password: str,
                                       test_url: str = None,
                                       validation_preset: str = "login_success") -> Dict[str, Any]:
    """
    Quick function to test authentication and validate a single endpoint.
    
    Args:
                            url: Login URL
                            username: Username for authentication
                            password: Password for authentication  
                            test_url: URL to test after authentication (defaults to login URL)
                            validation_preset: Validation preset to use
                            
    Returns:
                            Test result with authentication and validation results
    """
    try:
                                # Create auth config from parameters
                            auth_config = AuthConfig(
                                url=url,
                                credentials={"username": username, "password": password},
                                success_indicators=["welcome", "dashboard", "login successful"]
                            )
                            
                                # Extract base URL
                            from urllib.parse import urljoin, urlparse
                            parsed = urlparse(url)
                            base_url = f"{parsed.scheme}://{parsed.netloc}"
                            
                                # Use login URL as test URL if not provided
                            if test_url is None:
                                test_url = url
                                
                            validator = create_authenticated_validator(auth_config, base_url)
                            result = validator.request_and_validate('GET', test_url, validation_preset=validation_preset)
                            validator.close()
                            return result
    except Exception as e:
                            return {
                                'success': False,
                                'error': str(e),
                                'request_result': None,
                                'validation_result': ValidationResult(is_valid=False, error_message=str(e))
                            }


def list_validator_presets() -> List[str]:
    """List all available validation presets."""
    return list_available_presets()


def create_dvwa_validator(base_url: str, 
                                             username: str = "admin",
                                             password: str = "password") -> AuthenticatedValidator:
    """
    Convenience function to create a validator configured for DVWA.
    
    Args:
                            username: DVWA username
                            password: DVWA password  
                            base_url: DVWA base URL
                            
    Returns:
                            Configured AuthenticatedValidator for DVWA
    """
    csrf_config = create_csrf_config(
                            enabled=True,
                            auto_include=True,
                            refresh_on_failure=True
    )
    
    auth_config = AuthConfig(
                            url=f"{base_url}/login.php",
                            method="POST",
                            credentials={
                                "username": username,
                                "password": password,
                                "Login": "Login"
                            },
                            success_indicators=["Welcome", "DVWA"],
                            failure_indicators=["Login failed", "incorrect"],
                            csrf_config=csrf_config,
                            session_validation_url=f"{base_url}/vulnerabilities/brute/",
                            timeout=30,
                            verify_ssl=False
    )
    
    return create_authenticated_validator(auth_config, base_url)
