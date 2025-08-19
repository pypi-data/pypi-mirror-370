from logicpwn.exporters import BaseExporter
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
from typing import List, Optional, IO
from logicpwn.core.reporter.template_renderer import TemplateRenderer
from logicpwn.core.logging.redactor import SensitiveDataRedactor
import os

class MarkdownExporter(BaseExporter):
    """
    Enhanced Markdown exporter with proper sanitization, error handling, and sensitive data redaction.
    """
    def __init__(self):
        """
        Initialize the exporter with the default template directory and data redactor.
        """
        self.template_dir = "logicpwn/templates"
        self.redactor = SensitiveDataRedactor()

    def _redact_sensitive_content(self, content: str) -> str:
        """
        Redact sensitive information from content using the centralized redactor.
        
        Args:
            content: Content to redact
            
        Returns:
            Redacted and Markdown-escaped content
        """
        if not content:
            return content
        
        # First redact sensitive data, then escape Markdown
        redacted = self.redactor.redact_string_body(str(content))
        return self._escape_markdown(redacted)

    def set_template_dir(self, template_dir: str):
        """
        Set a custom template directory for rendering.
        
        Args:
            template_dir: Path to the template directory
            
        Raises:
            ValueError: If template directory is invalid
        """
        if not template_dir or not template_dir.strip():
            raise ValueError("template_dir cannot be empty")
        self.template_dir = template_dir

    def export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata, template_dir: Optional[str] = None) -> str:
        """
        Export findings and metadata to Markdown format with sanitization.
        
        Args:
            findings: List of VulnerabilityFinding objects
            metadata: ReportMetadata object
            template_dir: Optional custom template directory
            
        Returns:
            Markdown string
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate inputs
        self.validate_inputs(findings, metadata)
        
        renderer = TemplateRenderer(template_dir or self.template_dir)
        
        # Prepare context with sanitized data
        context = {
            "title": self._escape_markdown(metadata.title),
            "target_url": self._escape_markdown(metadata.target_url),
            "scan_start_time": metadata.scan_start_time,
            "scan_end_time": metadata.scan_end_time,
            "total_findings": len(findings),
            "critical_count": self._count_findings_by_severity(findings, 'Critical'),
            "high_count": self._count_findings_by_severity(findings, 'High'),
            "medium_count": self._count_findings_by_severity(findings, 'Medium'),
            "low_count": self._count_findings_by_severity(findings, 'Low'),
            "findings": [self._prepare_finding_context(f) for f in findings],
            "scan_duration": self._calculate_scan_duration(metadata),
            "logicpwn_version": self._escape_markdown(getattr(metadata, 'logicpwn_version', 'Unknown')),
            "authenticated_user": self._escape_markdown(getattr(metadata, 'authenticated_user', None)),
            "export_timestamp": self.format_datetime(None)  # Current time
        }
        
        try:
            return renderer.render("markdown_template.md", context)
        except Exception as e:
            # Enhanced fallback with better structure
            return self._generate_fallback_markdown(findings, metadata)

    def _prepare_finding_context(self, finding: VulnerabilityFinding) -> dict:
        """
        Prepare finding data for Markdown context with sanitization.
        
        Args:
            finding: Vulnerability finding
            
        Returns:
            Sanitized finding dictionary
        """
        return {
            "severity": self._escape_markdown(getattr(finding, 'severity', 'Unknown')),
            "title": self._escape_markdown(getattr(finding, 'title', 'Untitled')),
            "cvss_score": self._safe_cvss_score(getattr(finding, 'cvss_score', None)),
            "affected_endpoints": self._format_endpoints_markdown(getattr(finding, 'affected_endpoints', [])),
            "description": self._format_markdown_content(getattr(finding, 'description', 'No description')),
            "proof_of_concept": self._redact_sensitive_content(getattr(finding, 'proof_of_concept', 'No PoC')),
            "impact": self._format_markdown_content(getattr(finding, 'impact', 'Impact not specified')),
            "remediation": self._format_markdown_content(getattr(finding, 'remediation', 'Remediation not specified')),
            "references": self._format_references_markdown(getattr(finding, 'references', [])),
            "discovered_at": self.format_datetime(getattr(finding, 'discovered_at', None)),
            "severity_emoji": self._get_severity_emoji(getattr(finding, 'severity', 'Unknown'))
        }

    def _generate_fallback_markdown(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> str:
        """
        Generate fallback Markdown with enhanced structure.
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata
            
        Returns:
            Markdown string
        """
        lines = [
            f"# {self._escape_markdown(metadata.title)}",
            "",
            "## Executive Summary",
            "",
            f"**Target:** {self._escape_markdown(metadata.target_url)}",
            f"**Assessment Period:** {self._format_scan_period(metadata)}",
            f"**Total Findings:** {len(findings)}",
            f"**Critical Issues:** {self._count_findings_by_severity(findings, 'Critical')} 🔴",
            f"**High Severity:** {self._count_findings_by_severity(findings, 'High')} 🟠", 
            f"**Medium Severity:** {self._count_findings_by_severity(findings, 'Medium')} 🟡",
            f"**Low Severity:** {self._count_findings_by_severity(findings, 'Low')} 🟢",
            "",
            "---",
            "",
            "## 🔍 Vulnerability Details",
            ""
        ]
        
        # Add findings with enhanced formatting
        for i, finding in enumerate(findings, 1):
            severity = getattr(finding, 'severity', 'Unknown')
            emoji = self._get_severity_emoji(severity)
            
            lines.extend([
                f"### {i}. {emoji} {self._escape_markdown(getattr(finding, 'title', 'Untitled'))}",
                "",
                f"**Severity:** {self._escape_markdown(severity)}  ",
                f"**CVSS Score:** {self._safe_cvss_score(getattr(finding, 'cvss_score', None))}  ",
                f"**Discovered:** {self.format_datetime(getattr(finding, 'discovered_at', None))}",
                "",
                "#### 🎯 Affected Endpoints",
                "",
                self._format_endpoints_markdown(getattr(finding, 'affected_endpoints', [])),
                "",
                "#### 📝 Description",
                "",
                self._format_markdown_content(getattr(finding, 'description', 'No description')),
                "",
                "#### 🔬 Proof of Concept",
                "",
                "```http",
                self._format_code_content(getattr(finding, 'proof_of_concept', 'No PoC')),
                "```",
                "",
                "#### 💥 Impact",
                "",
                self._format_markdown_content(getattr(finding, 'impact', 'Impact not specified')),
                "",
                "#### 🛠️ Remediation",
                "",
                self._format_markdown_content(getattr(finding, 'remediation', 'Remediation not specified')),
                "",
                "#### 📚 References",
                "",
                self._format_references_markdown(getattr(finding, 'references', [])),
                "",
                "---",
                ""
            ])
        
        # Add appendix with enhanced information
        lines.extend([
            "## 📊 Report Information",
            "",
            "| Field | Value |",
            "|-------|-------|",
            f"| **Scan Duration** | {self._calculate_scan_duration(metadata)} |",
            f"| **LogicPwn Version** | {self._escape_markdown(getattr(metadata, 'logicpwn_version', 'Unknown'))} |",
            f"| **Authentication** | {self._escape_markdown(getattr(metadata, 'authenticated_user', None))} |",
            f"| **Generated** | {self.format_datetime(None)} |",
            f"| **Total Requests** | {getattr(metadata, 'total_requests', 'Unknown')} |",
            "",
            "---",
            "",
            "*Report generated by LogicPwn Security Testing Framework*"
        ])
        
        return '\n'.join(lines)

    def stream_export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata, file: IO, template_dir: Optional[str] = None):
        """
        Stream findings and metadata to a file in Markdown format with memory efficiency.
        
        Args:
            findings: List of VulnerabilityFinding objects
            metadata: ReportMetadata object
            file: File-like object to write to
            template_dir: Optional custom template directory
        """
        try:
            # Validate inputs
            self.validate_inputs(findings, metadata)
            
            # Stream header
            file.write(f"# {self._escape_markdown(metadata.title)}\n\n")
            file.write("## Executive Summary\n\n")
            file.write(f"**Target:** {self._escape_markdown(metadata.target_url)}\n")
            file.write(f"**Assessment Period:** {self._format_scan_period(metadata)}\n")
            file.write(f"**Total Findings:** {len(findings)}\n")
            file.write(f"**Critical Issues:** {self._count_findings_by_severity(findings, 'Critical')} 🔴\n")
            file.write(f"**High Severity:** {self._count_findings_by_severity(findings, 'High')} 🟠\n")
            file.write(f"**Medium Severity:** {self._count_findings_by_severity(findings, 'Medium')} 🟡\n")
            file.write(f"**Low Severity:** {self._count_findings_by_severity(findings, 'Low')} 🟢\n\n")
            file.write("---\n\n")
            file.write("## 🔍 Vulnerability Details\n\n")
            
            # Stream findings
            for i, finding in enumerate(findings, 1):
                severity = getattr(finding, 'severity', 'Unknown')
                emoji = self._get_severity_emoji(severity)
                
                file.write(f"### {i}. {emoji} {self._escape_markdown(getattr(finding, 'title', 'Untitled'))}\n\n")
                file.write(f"**Severity:** {self._escape_markdown(severity)}  \n")
                file.write(f"**CVSS Score:** {self._safe_cvss_score(getattr(finding, 'cvss_score', None))}  \n")
                file.write(f"**Discovered:** {self.format_datetime(getattr(finding, 'discovered_at', None))}\n\n")
                
                file.write("#### 🎯 Affected Endpoints\n\n")
                file.write(self._format_endpoints_markdown(getattr(finding, 'affected_endpoints', [])) + "\n\n")
                
                file.write("#### 📝 Description\n\n")
                file.write(self._format_markdown_content(getattr(finding, 'description', 'No description')) + "\n\n")
                
                file.write("#### 🔬 Proof of Concept\n\n")
                file.write("```http\n")
                file.write(self._format_code_content(getattr(finding, 'proof_of_concept', 'No PoC')) + "\n")
                file.write("```\n\n")
                
                file.write("#### 💥 Impact\n\n")
                file.write(self._format_markdown_content(getattr(finding, 'impact', 'Impact not specified')) + "\n\n")
                
                file.write("#### 🛠️ Remediation\n\n")
                file.write(self._format_markdown_content(getattr(finding, 'remediation', 'Remediation not specified')) + "\n\n")
                
                file.write("#### 📚 References\n\n")
                file.write(self._format_references_markdown(getattr(finding, 'references', [])) + "\n\n")
                
                file.write("---\n\n")
            
            # Stream appendix
            file.write("## 📊 Report Information\n\n")
            file.write("| Field | Value |\n")
            file.write("|----------|-------|\n")
            file.write(f"| **Scan Duration** | {self._calculate_scan_duration(metadata)} |\n")
            file.write(f"| **LogicPwn Version** | {self._escape_markdown(getattr(metadata, 'logicpwn_version', 'Unknown'))} |\n")
            file.write(f"| **Authentication** | {self._escape_markdown(getattr(metadata, 'authenticated_user', None))} |\n")
            file.write(f"| **Generated** | {self.format_datetime(None)} |\n")
            file.write(f"| **Total Requests** | {getattr(metadata, 'total_requests', 'Unknown')} |\n\n")
            file.write("---\n\n")
            file.write("*Report generated by LogicPwn Security Testing Framework*\n")
            
        except Exception as e:
            raise ValueError(f"Failed to stream Markdown export: {e}")

    # Helper methods
    def _escape_markdown(self, text: any) -> str:
        """
        Escape Markdown special characters to prevent format injection.
        
        Args:
            text: Input text
            
        Returns:
            Markdown-escaped string
        """
        if text is None:
            return "N/A"
        
        text_str = str(text)
        
        # Markdown special characters that need escaping
        markdown_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
        
        for char in markdown_chars:
            text_str = text_str.replace(char, f'\\{char}')
        
        return self.sanitize_text(text_str)

    def _count_findings_by_severity(self, findings: List[VulnerabilityFinding], severity: str) -> int:
        """Count findings by severity level."""
        return sum(1 for f in findings if getattr(f, 'severity', '').lower() == severity.lower())

    def _safe_cvss_score(self, score: any) -> str:
        """Safely format CVSS score."""
        if score is None:
            return "N/A"
        try:
            return f"{float(score):.1f}"
        except (ValueError, TypeError):
            return "N/A"

    def _format_endpoints_markdown(self, endpoints: any) -> str:
        """Format endpoints for Markdown display."""
        if not endpoints:
            return "*No endpoints specified*"
        
        if isinstance(endpoints, list):
            escaped_endpoints = [f"`{self._escape_markdown(ep)}`" for ep in endpoints if ep is not None]
            if escaped_endpoints:
                return "- " + "\n- ".join(escaped_endpoints)
            else:
                return "*No valid endpoints*"
        else:
            return f"`{self._escape_markdown(endpoints)}`"

    def _format_markdown_content(self, content: any) -> str:
        """Format content for Markdown with proper escaping."""
        escaped = self._escape_markdown(content)
        # Convert newlines to proper Markdown line breaks
        return escaped.replace('\n', '  \n') if escaped != "N/A" else escaped

    def _format_code_content(self, code: any) -> str:
        """Format code content without Markdown escaping (for code blocks)."""
        return self.sanitize_text(code)
    
    def _format_code_markdown(self, code: any) -> str:
        """Format code/payload for markdown output."""
        if code is None:
            return "No code provided"
        code_str = str(code)
        # Escape markdown and wrap in code block
        code_str = self._escape_markdown(code_str)
        return f"```\n{code_str}\n```"

    def _format_references_markdown(self, references: any) -> str:
        """Format references as Markdown links."""
        if not references:
            return "*No references*"
        
        if isinstance(references, list):
            ref_links = []
            for ref in references:
                if ref is None:
                    continue
                escaped_ref = self._escape_markdown(ref)
                if str(ref).startswith(('http://', 'https://')):
                    ref_links.append(f"- [{escaped_ref}]({ref})")
                else:
                    ref_links.append(f"- {escaped_ref}")
            return "\n".join(ref_links) if ref_links else "*No valid references*"
        else:
            escaped_ref = self._escape_markdown(references)
            if str(references).startswith(('http://', 'https://')):
                return f"- [{escaped_ref}]({references})"
            else:
                return f"- {escaped_ref}"

    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level."""
        severity_map = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🟢'
        }
        return severity_map.get(str(severity).lower(), '⚪')

    def _format_scan_period(self, metadata: ReportMetadata) -> str:
        """Format scan period for display."""
        try:
            start = getattr(metadata, 'scan_start_time', None)
            end = getattr(metadata, 'scan_end_time', None)
            
            if start and end:
                if hasattr(start, 'strftime') and hasattr(end, 'strftime'):
                    return f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')}"
                else:
                    return f"{start} - {end}"
            return "Unknown"
        except Exception:
            return "Unknown"

    def _calculate_scan_duration(self, metadata: ReportMetadata) -> str:
        """Calculate and format scan duration."""
        try:
            start = getattr(metadata, 'scan_start_time', None) 
            end = getattr(metadata, 'scan_end_time', None)
            
            if start and end and hasattr(start, 'timestamp') and hasattr(end, 'timestamp'):
                duration = end - start
                return str(duration)
            return "Unknown"
        except Exception:
            return "Unknown"
            file.write(f"\n**References:** {', '.join(finding.references) if finding.references else 'N/A'}\n")
            file.write(f"\n**Discovered At:** {finding.discovered_at.isoformat()}\n\n---\n\n")
        # Stream appendix
        file.write("## Appendix\n")
        file.write(f"- **Scan Duration:** {(metadata.scan_end_time - metadata.scan_start_time)}\n")
        file.write(f"- **LogicPwn Version:** {metadata.logicpwn_version}\n")
        file.write(f"- **Authentication:** {metadata.authenticated_user or 'N/A'}\n") 