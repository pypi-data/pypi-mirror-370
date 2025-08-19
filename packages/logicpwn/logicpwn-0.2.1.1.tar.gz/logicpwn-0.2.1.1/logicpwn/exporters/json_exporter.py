import json
from logicpwn.exporters import BaseExporter
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
from typing import List, Any, Dict
from datetime import datetime, date
import decimal
from logicpwn.core.logging.redactor import SensitiveDataRedactor

class JSONExporter(BaseExporter):
    """
    Enhanced JSON exporter with proper serialization, error handling, and sensitive data redaction.
    """
    
    def __init__(self):
        """Initialize JSON exporter with data redactor."""
        super().__init__()
        self.redactor = SensitiveDataRedactor()
    
    def _redact_sensitive_content(self, content: str) -> str:
        """
        Redact sensitive information from content using the centralized redactor.
        
        Args:
            content: Content to redact
            
        Returns:
            Redacted content
        """
        if not content:
            return content
        
        # Use the centralized redactor for consistent redaction
        return self.redactor.redact_string_body(str(content))
    
    def export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> str:
        """
        Export findings and metadata to JSON format.
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata
            
        Returns:
            JSON string
            
        Raises:
            ValueError: If input validation fails
            TypeError: If serialization fails
        """
        # Validate inputs
        self.validate_inputs(findings, metadata)
        
        try:
            # Prepare report data with safe serialization
            report = {
                "report_metadata": self._serialize_metadata(metadata),
                "findings": [self._serialize_finding(f) for f in findings],
                "export_info": {
                    "exported_at": datetime.now().isoformat(),
                    "total_findings": len(findings),
                    "exporter_version": "1.0.0"
                }
            }
            
            return json.dumps(report, indent=2, default=self._json_serializer, ensure_ascii=False)
            
        except Exception as e:
            raise ValueError(f"Failed to serialize data to JSON: {e}")
    
    def _serialize_finding(self, finding: VulnerabilityFinding) -> Dict[str, Any]:
        """
        Safely serialize a vulnerability finding.
        
        Args:
            finding: Vulnerability finding object
            
        Returns:
            Serializable dictionary
        """
        if hasattr(finding, 'model_dump'):
            data = finding.model_dump()
        elif hasattr(finding, 'dict'):
            data = finding.dict()
        else:
            # Fallback to object attributes
            data = {}
            for attr in dir(finding):
                if not attr.startswith('_') and not callable(getattr(finding, attr)):
                    data[attr] = getattr(finding, attr)
        
        # Ensure all fields are present with safe defaults and redaction
        safe_data = {
            "severity": self.sanitize_text(data.get("severity")),
            "title": self.sanitize_text(data.get("title")),
            "cvss_score": self._safe_float(data.get("cvss_score")),
            "affected_endpoints": self._safe_list(data.get("affected_endpoints")),
            "description": self.sanitize_text(data.get("description")),
            "proof_of_concept": self._redact_sensitive_content(data.get("proof_of_concept")),
            "impact": self.sanitize_text(data.get("impact")),
            "remediation": self.sanitize_text(data.get("remediation")),
            "references": self._safe_list(data.get("references")),
            "discovered_at": self.format_datetime(data.get("discovered_at")),
            "confidence_level": self.sanitize_text(data.get("confidence_level", "Medium")),
            "false_positive": bool(data.get("false_positive", False))
        }
        
        return safe_data
    
    def _serialize_metadata(self, metadata: ReportMetadata) -> Dict[str, Any]:
        """
        Safely serialize report metadata.
        
        Args:
            metadata: Report metadata object
            
        Returns:
            Serializable dictionary
        """
        if hasattr(metadata, 'model_dump'):
            data = metadata.model_dump()
        elif hasattr(metadata, 'dict'):
            data = metadata.dict()
        else:
            # Fallback to object attributes
            data = {}
            for attr in dir(metadata):
                if not attr.startswith('_') and not callable(getattr(metadata, attr)):
                    data[attr] = getattr(metadata, attr)
        
        # Ensure all fields are present with safe defaults
        safe_data = {
            "title": self.sanitize_text(data.get("title")),
            "target_url": self.sanitize_text(data.get("target_url")),
            "scan_start_time": self.format_datetime(data.get("scan_start_time")),
            "scan_end_time": self.format_datetime(data.get("scan_end_time")),
            "scan_duration": self._calculate_duration(data.get("scan_start_time"), data.get("scan_end_time")),
            "logicpwn_version": self.sanitize_text(data.get("logicpwn_version", "Unknown")),
            "authenticated_user": self.sanitize_text(data.get("authenticated_user")),
            "total_requests": int(data.get("total_requests", 0)),
            "findings_count": self._safe_dict(data.get("findings_count")),
            "report_id": self.sanitize_text(data.get("report_id", "Unknown"))
        }
        
        return safe_data
    
    def _json_serializer(self, obj: Any) -> Any:
        """
        Custom JSON serializer for complex objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serializable representation
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float."""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_list(self, value: Any) -> List[str]:
        """Safely convert value to list of strings."""
        if value is None:
            return []
        if isinstance(value, list):
            return [self.sanitize_text(item) for item in value]
        return [self.sanitize_text(value)]
    
    def _safe_dict(self, value: Any) -> Dict[str, int]:
        """Safely convert value to dictionary."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return {k: int(v) if isinstance(v, (int, float)) else 0 for k, v in value.items()}
        return {}
    
    def _calculate_duration(self, start: Any, end: Any) -> str:
        """Calculate duration between start and end times."""
        try:
            if start and end and hasattr(start, 'timestamp') and hasattr(end, 'timestamp'):
                duration = end - start
                return str(duration)
        except Exception:
            pass
        return "Unknown" 