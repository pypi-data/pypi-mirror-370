"""
Validation data models and enums for LogicPwn response validation.
Enhanced with adaptive confidence scoring and business logic discovery.
"""
from typing import Dict, Optional, List, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import time

class ValidationType(Enum):
    """Types of validation criteria."""
    SUCCESS_CRITERIA = "success_criteria"
    FAILURE_CRITERIA = "failure_criteria"
    REGEX_PATTERN = "regex_pattern"
    STATUS_CODE = "status_code"
    HEADER_CRITERIA = "header_criteria"
    JSON_PATH = "json_path"
    TIMING_ANALYSIS = "timing_analysis"
    BUSINESS_LOGIC = "business_logic"
    CONTENT = "content"
    ERROR = "error"
    COMPOSITE = "composite"

class SeverityLevel(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ConfidenceLevel(Enum):
    """Confidence level classifications."""
    VERY_HIGH = "very_high"      # 0.9 - 1.0
    HIGH = "high"                # 0.7 - 0.89
    MEDIUM = "medium"            # 0.5 - 0.69
    LOW = "low"                  # 0.3 - 0.49
    VERY_LOW = "very_low"        # 0.0 - 0.29

@dataclass
class AdaptiveConfidenceWeights:
    """Adaptive weights for confidence scoring."""
    pattern_match_weight: float = 0.4
    status_code_weight: float = 0.2
    response_time_weight: float = 0.1
    header_analysis_weight: float = 0.1
    content_length_weight: float = 0.05
    multiple_indicators_bonus: float = 0.15
    
    # Adaptive multipliers based on context
    critical_vuln_multiplier: float = 1.2
    authenticated_context_multiplier: float = 1.1
    production_env_multiplier: float = 0.9
    
    def adjust_for_vulnerability_type(self, vuln_type: str) -> 'AdaptiveConfidenceWeights':
        """Adjust weights based on vulnerability type."""
        adjusted = AdaptiveConfidenceWeights()
        
        if vuln_type in ['sql_injection', 'command_injection', 'ssrf']:
            adjusted.pattern_match_weight = 0.5
            adjusted.status_code_weight = 0.3
        elif vuln_type in ['xss', 'csrf']:
            adjusted.pattern_match_weight = 0.6
            adjusted.content_length_weight = 0.1
        elif vuln_type in ['business_logic', 'auth_bypass']:
            adjusted.status_code_weight = 0.4
            adjusted.header_analysis_weight = 0.2
        
        return adjusted

@dataclass
class ValidationResult:
    """Enhanced structured result from response validation."""
    is_valid: bool = False
    matched_patterns: List[str] = field(default_factory=list)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    confidence_level: Optional[ConfidenceLevel] = None
    severity: Optional[SeverityLevel] = None
    vulnerability_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_type: Optional[ValidationType] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    evidence: List[str] = field(default_factory=list)
    false_positive_indicators: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate confidence level and perform post-validation analysis."""
        if self.confidence_level is None:
            self.confidence_level = self._calculate_confidence_level()
        
        # Adjust confidence based on false positive indicators
        if self.false_positive_indicators:
            self.confidence_score *= 0.8  # Reduce confidence by 20%
        
        # Set default severity based on vulnerability type and confidence
        if self.severity is None:
            self.severity = self._determine_severity()
    
    def _calculate_confidence_level(self) -> ConfidenceLevel:
        """Calculate confidence level based on score."""
        if self.confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.7:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif self.confidence_score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _determine_severity(self) -> SeverityLevel:
        """Determine severity based on vulnerability type and confidence."""
        if not self.vulnerability_type:
            return SeverityLevel.INFO
        
        critical_vulns = ['sql_injection', 'command_injection', 'ssrf', 'auth_bypass']
        high_vulns = ['xss', 'csrf', 'lfi', 'rfi', 'xxe']
        medium_vulns = ['directory_traversal', 'open_redirect', 'info_disclosure']
        
        base_severity = SeverityLevel.LOW
        if self.vulnerability_type in critical_vulns:
            base_severity = SeverityLevel.CRITICAL
        elif self.vulnerability_type in high_vulns:
            base_severity = SeverityLevel.HIGH
        elif self.vulnerability_type in medium_vulns:
            base_severity = SeverityLevel.MEDIUM
        
        # Adjust based on confidence
        if self.confidence_score < 0.5 and base_severity == SeverityLevel.CRITICAL:
            return SeverityLevel.HIGH
        elif self.confidence_score < 0.3:
            return SeverityLevel.LOW
        
        return base_severity

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "matched_patterns": self.matched_patterns,
            "extracted_data": self.extracted_data,
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level.value if self.confidence_level else None,
            "severity": self.severity.value if self.severity else None,
            "vulnerability_type": self.vulnerability_type,
            "metadata": self.metadata,
            "validation_type": self.validation_type.value if self.validation_type else None,
            "error_message": self.error_message,
            "response_time": self.response_time,
            "evidence": self.evidence,
            "false_positive_indicators": self.false_positive_indicators
        }

    def __str__(self) -> str:
        return f"ValidationResult(valid={self.is_valid}, confidence={self.confidence_score:.2f}, severity={self.severity.value if self.severity else 'unknown'})"

class ValidationConfig(BaseModel):
    """Enhanced configuration model for response validation."""
    success_criteria: List[str] = Field(default_factory=list, description="Text indicators of successful validation")
    failure_criteria: List[str] = Field(default_factory=list, description="Text indicators of failed validation")
    regex_patterns: List[str] = Field(default_factory=list, description="Regex patterns to match against response content")
    status_codes: List[int] = Field(default_factory=list, description="Acceptable HTTP status codes")
    headers_criteria: Dict[str, str] = Field(default_factory=dict, description="Required headers and their values")
    json_paths: List[str] = Field(default_factory=list, description="JSON path expressions for JSON responses")
    return_structured: bool = Field(default=False, description="Return ValidationResult object instead of boolean")
    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum confidence score for validation")
    
    # Enhanced validation options
    require_all_success: bool = Field(default=True, description="Require all success criteria to match")
    require_all_failure: bool = Field(default=False, description="Require all failure criteria to match")
    case_sensitive: bool = Field(default=False, description="Case sensitive pattern matching")
    response_time_threshold: Optional[float] = Field(default=None, description="Maximum acceptable response time")
    min_content_length: Optional[int] = Field(default=None, description="Minimum content length for validation")
    max_content_length: Optional[int] = Field(default=None, description="Maximum content length for validation")
    
    # Adaptive confidence scoring
    adaptive_scoring: bool = Field(default=True, description="Enable adaptive confidence scoring")
    confidence_weights: Optional[AdaptiveConfidenceWeights] = Field(default=None, description="Custom confidence weights")
    vulnerability_type: Optional[str] = Field(default=None, description="Type of vulnerability being tested")
    
    # Business logic validation
    business_rule_validator: Optional[str] = Field(default=None, description="Custom business rule validator function name")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context for validation")
    
    # False positive reduction
    false_positive_patterns: List[str] = Field(default_factory=list, description="Patterns that indicate false positives")
    whitelist_patterns: List[str] = Field(default_factory=list, description="Patterns that should be ignored")

    @field_validator('regex_patterns')
    @classmethod
    def validate_regex_patterns(cls, v: List[str]) -> List[str]:
        """Validate regex patterns are compilable."""
        import re
        for pattern in v:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        return v

    @field_validator('status_codes')
    @classmethod
    def validate_status_codes(cls, v: List[int]) -> List[int]:
        """Validate HTTP status codes are in valid range."""
        for code in v:
            if not (100 <= code <= 599):
                raise ValueError(f"Invalid HTTP status code: {code}")
        return v

    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence_threshold(cls, v: float) -> float:
        """Ensure confidence threshold is in valid range."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v

    def get_confidence_weights(self) -> AdaptiveConfidenceWeights:
        """Get confidence weights, creating adaptive ones if needed."""
        if self.confidence_weights:
            return self.confidence_weights
        
        weights = AdaptiveConfidenceWeights()
        if self.vulnerability_type:
            weights = weights.adjust_for_vulnerability_type(self.vulnerability_type)
        
        return weights

@dataclass 
class BusinessLogicRule:
    """Business logic validation rule."""
    name: str
    description: str
    validator_function: Callable[[Any, Dict[str, Any]], bool]
    expected_behavior: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    confidence_weight: float = 0.5

@dataclass
class BusinessLogicTemplate:
    """Template for business logic testing workflows."""
    name: str
    description: str
    workflow_steps: List[str]
    validation_rules: List[BusinessLogicRule]
    context_requirements: List[str]
    expected_outcomes: Dict[str, Any]
    
    # Common business logic templates
    @staticmethod
    def ecommerce_price_manipulation() -> 'BusinessLogicTemplate':
        """Template for e-commerce price manipulation testing."""
        return BusinessLogicTemplate(
            name="E-commerce Price Manipulation",
            description="Test for price manipulation vulnerabilities in e-commerce workflows",
            workflow_steps=[
                "Add item to cart",
                "Modify price parameter",
                "Proceed to checkout",
                "Validate final price"
            ],
            validation_rules=[
                BusinessLogicRule(
                    name="negative_price_check",
                    description="Check if negative prices are accepted",
                    validator_function=lambda response, context: "negative" in str(response) or "error" in str(response),
                    expected_behavior="Negative prices should be rejected",
                    severity=SeverityLevel.HIGH
                )
            ],
            context_requirements=["product_id", "original_price"],
            expected_outcomes={"price_manipulation_detected": False}
        )
    
    @staticmethod
    def banking_transaction_limits() -> 'BusinessLogicTemplate':
        """Template for banking transaction limit testing."""
        return BusinessLogicTemplate(
            name="Banking Transaction Limits",
            description="Test transaction limit enforcement in banking applications",
            workflow_steps=[
                "Authenticate user",
                "Check account balance",
                "Attempt transaction above limit",
                "Validate transaction rejection"
            ],
            validation_rules=[
                BusinessLogicRule(
                    name="limit_enforcement_check",
                    description="Check if transaction limits are properly enforced",
                    validator_function=lambda response, context: "limit exceeded" in str(response).lower(),
                    expected_behavior="Transactions above limit should be rejected",
                    severity=SeverityLevel.CRITICAL
                )
            ],
            context_requirements=["account_balance", "transaction_limit"],
            expected_outcomes={"limit_bypass_detected": False}
        ) 