from typing import List, Union, Optional, Dict, Any
from dataclasses import dataclass, field
import datetime
import requests

@dataclass
class AccessTestResult:
    """
    Result of a single access control/IDOR test.
    """
    id_tested: Union[str, int]
    endpoint_url: str
    status_code: int
    access_granted: bool
    vulnerability_detected: bool
    response_indicators: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    expected_access: Optional[bool] = None
    # Audit/log fields
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    request_method: str = "GET"
    request_data: Optional[Dict[str, Any]] = None
    response_body: Optional[str] = None
    baseline_results: Optional[List[Dict[str, Any]]] = None  # Info from baseline sessions
    decision_log: Optional[str] = None  # Human-readable explanation

    @property
    def is_vulnerable(self) -> bool:
        """Alias for vulnerability_detected for backward compatibility."""
        return self.vulnerability_detected

@dataclass
class AccessDetectorConfig:
    """
    Configuration for the access/IDOR detector.
    
    Enhanced with validation methods and conflict detection.
    """
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    compare_unauthenticated: bool = True
    current_user_id: Optional[Union[str, int]] = None
    authorized_ids: Optional[List[Union[str, int]]] = None
    unauthorized_ids: Optional[List[Union[str, int]]] = None
    rate_limit: Optional[float] = None  # seconds between requests
    # New: allow custom HTTP method and request data per test
    method: str = "GET"
    request_data_map: Optional[Dict[Union[str, int], Dict[str, Any]]] = None  # Per-ID request data
    # New: support multiple baseline sessions (e.g., guest, user, admin)
    baseline_sessions: Optional[List[requests.Session]] = None
    baseline_names: Optional[List[str]] = None  # Names for each baseline session
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate the configuration for logical consistency and security.
        
        Raises:
            ValueError: If configuration is invalid or insecure
        """
        # Validate concurrent requests
        if self.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be positive")
        if self.max_concurrent_requests > 100:
            raise ValueError("max_concurrent_requests should not exceed 100 for safety")
        
        # Validate timeout
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        
        # Validate retry attempts
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts cannot be negative")
        if self.retry_attempts > 10:
            raise ValueError("retry_attempts should not exceed 10 for safety")
        
        # Validate rate limit
        if self.rate_limit is not None and self.rate_limit < 0:
            raise ValueError("rate_limit cannot be negative")
        
        # Check for conflicting ID configurations
        self._validate_id_conflicts()
        
        # Validate baseline configuration
        self._validate_baseline_config()
    
    def _validate_id_conflicts(self) -> None:
        """Check for conflicts in ID configurations."""
        # Normalize IDs for comparison
        def normalize_ids(ids):
            if ids is None:
                return set()
            return {str(id_val) for id_val in ids}
        
        authorized = normalize_ids(self.authorized_ids)
        unauthorized = normalize_ids(self.unauthorized_ids)
        current = str(self.current_user_id) if self.current_user_id is not None else None
        
        # Check for overlapping authorized/unauthorized
        conflicts = authorized & unauthorized
        if conflicts:
            raise ValueError(f"IDs found in both authorized_ids and unauthorized_ids: {conflicts}")
        
        # Check current_user_id conflicts
        if current is not None:
            if current in unauthorized:
                raise ValueError(f"current_user_id {current} cannot be in unauthorized_ids")
            if self.authorized_ids is not None and current not in authorized:
                raise ValueError(f"current_user_id {current} should be in authorized_ids if specified")
    
    def _validate_baseline_config(self) -> None:
        """Validate baseline session configuration."""
        if self.baseline_sessions is not None:
            if not isinstance(self.baseline_sessions, list):
                raise TypeError("baseline_sessions must be a list")
            
            if self.baseline_names is not None:
                if len(self.baseline_names) != len(self.baseline_sessions):
                    raise ValueError("baseline_names length must match baseline_sessions length")
    
    def has_valid_auth_config(self) -> bool:
        """Check if at least one authentication configuration is provided."""
        return any([
            self.current_user_id is not None,
            self.authorized_ids is not None,
            self.unauthorized_ids is not None
        ])
    
    def get_expected_access_summary(self) -> Dict[str, Any]:
        """Get a summary of the access control configuration."""
        return {
            "current_user_id": self.current_user_id,
            "authorized_count": len(self.authorized_ids) if self.authorized_ids else 0,
            "unauthorized_count": len(self.unauthorized_ids) if self.unauthorized_ids else 0,
            "has_baseline_sessions": self.baseline_sessions is not None,
            "baseline_count": len(self.baseline_sessions) if self.baseline_sessions else 0
        } 