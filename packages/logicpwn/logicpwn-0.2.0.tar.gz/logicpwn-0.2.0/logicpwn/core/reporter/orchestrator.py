"""
LogicPwn Reporting Orchestrator
- Professional, extensible, and performant report generation
- Integrates with all core modules (auth, detector, exploit_engine)
- Uses centralized redaction, cache, and performance utilities
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from logicpwn.core.logging.redactor import SensitiveDataRedactor
from logicpwn.core.performance import monitor_performance
from logicpwn.core.cache.cache_utils import cached
from logicpwn.core.reporter.cvss import CVSSCalculator
from logicpwn.core.reporter.redactor import AdvancedRedactor
from logicpwn.core.reporter.models import RedactionRule

# --- Data Models ---
class VulnerabilityFinding(BaseModel):
    """
    Represents a single vulnerability finding for reporting.
    """
    id: str
    title: str
    severity: str  # "Critical", "High", "Medium", "Low", "Info"
    cvss_score: Optional[float] = None
    description: str
    affected_endpoints: List[str]
    proof_of_concept: str
    impact: str
    remediation: str
    references: List[str] = []
    discovered_at: datetime
    exploit_chain: Optional[List[Any]] = None  # ExploitStepResult
    request_response_pairs: List[Any] = []     # RequestResponsePair

class ReportMetadata(BaseModel):
    """
    Metadata for a vulnerability report, including scan details and summary stats.
    """
    report_id: str
    title: str
    target_url: str
    scan_start_time: datetime
    scan_end_time: datetime
    logicpwn_version: str
    authenticated_user: Optional[str] = None
    total_requests: int
    findings_count: Dict[str, int]

class ReportConfig(BaseModel):
    """
    Configuration for report generation, including output style, redaction, and branding.
    """
    target_url: str
    report_title: str
    report_type: str = "vapt"
    format_style: str = "professional"
    include_executive_summary: bool = True
    include_request_response: bool = True
    include_steps_to_reproduce: bool = True
    include_remediation: bool = True
    redaction_enabled: bool = True
    cvss_scoring_enabled: bool = True
    custom_branding: Optional[Dict[str, str]] = None
    redaction_rules: List[RedactionRule] = []

# --- Main Orchestrator ---
class ReportGenerator:
    """
    Main orchestrator for generating vulnerability reports in LogicPwn.
    Handles finding aggregation, CVSS scoring, redaction, and export in multiple formats.
    """
    def __init__(self, config: ReportConfig):
        """
        Initialize the report generator with a given configuration.
        """
        self.config = config
        self.findings: List[VulnerabilityFinding] = []
        self.metadata: Optional[ReportMetadata] = None
        self.redactor = None
        if config.redaction_enabled:
            custom_rules = getattr(config, 'redaction_rules', [])
            self.redactor = AdvancedRedactor(custom_rules)

    def add_finding(self, finding: VulnerabilityFinding) -> None:
        """
        Add a vulnerability finding to the report. Automatically calculates CVSS if enabled.
        """
        if self.config.cvss_scoring_enabled and (finding.cvss_score is None):
            finding.cvss_score = CVSSCalculator.calculate_cvss_score(
                # These should be mapped from finding or context in a real implementation
                exploit_success=True,
                authentication_required=False,
                data_impact="High"
            )
        self.findings.append(finding)

    @monitor_performance("report_generation")
    def generate_report(self, format: str = "markdown", template_dir: str = None) -> str:
        """
        Generate the report in the specified format (markdown, html, json).
        Optionally use a custom template directory.
        """
        from logicpwn.exporters import get_exporter
        exporter = get_exporter(format)
        if hasattr(exporter, 'set_template_dir') and template_dir:
            exporter.set_template_dir(template_dir)
        content = exporter.export(self.findings, self.metadata, template_dir=template_dir)
        return self.redact_sensitive_data(content) if self.redactor else content

    def export_to_file(self, filepath: str, format: str, template_dir: str = None) -> None:
        """
        Export the generated report to a file in the specified format.
        """
        report = self.generate_report(format, template_dir=template_dir)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

    def stream_to_file(self, filepath: str, format: str, template_dir: str = None) -> None:
        """
        Stream the report to a file, writing findings incrementally (for large reports).
        """
        from logicpwn.exporters import get_exporter
        exporter = get_exporter(format)
        with open(filepath, "w", encoding="utf-8") as f:
            if hasattr(exporter, 'stream_export'):
                exporter.stream_export(self.findings, self.metadata, f, template_dir=template_dir)
            else:
                # fallback to normal export
                report = exporter.export(self.findings, self.metadata, template_dir=template_dir)
                f.write(report)

    def redact_sensitive_data(self, content: str) -> str:
        """
        Redact sensitive data from the report content using configured rules.
        """
        return self.redactor.redact_string_body(content)

    @cached(ttl=600)
    def collect_findings_from_modules(self, auth_results, detector_results, exploit_results) -> List[VulnerabilityFinding]:
        """
        Aggregate findings from all LogicPwn modules (stub for integration).
        """
        return [] 