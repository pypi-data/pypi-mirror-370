from logicpwn.exporters import BaseExporter
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
from typing import List, Optional, IO
from logicpwn.core.reporter.template_renderer import TemplateRenderer
from logicpwn.core.logging.redactor import SensitiveDataRedactor
import os

class HTMLExporter(BaseExporter):
    """
    Enhanced HTML exporter with XSS prevention, better error handling, and sensitive data redaction.
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
            Redacted and HTML-escaped content
        """
        if not content:
            return content
        
        # First redact sensitive data, then escape HTML
        redacted = self.redactor.redact_string_body(str(content))
        return self.escape_html(redacted)

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
        Export findings and metadata to HTML format with XSS protection.
        
        Args:
            findings: List of VulnerabilityFinding objects
            metadata: ReportMetadata object
            template_dir: Optional custom template directory
            
        Returns:
            HTML string
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate inputs
        self.validate_inputs(findings, metadata)
        
        renderer = TemplateRenderer(template_dir or self.template_dir)
        
        # Prepare context with sanitized data
        context = {
            "title": self.escape_html(metadata.title),
            "target_url": self.escape_html(metadata.target_url),
            "scan_start_time": metadata.scan_start_time,
            "scan_end_time": metadata.scan_end_time,
            "total_findings": len(findings),
            "critical_count": self._count_findings_by_severity(findings, 'Critical'),
            "high_count": self._count_findings_by_severity(findings, 'High'),
            "medium_count": self._count_findings_by_severity(findings, 'Medium'),
            "low_count": self._count_findings_by_severity(findings, 'Low'),
            "findings": [self._prepare_finding_context(f) for f in findings],
            "scan_duration": self._calculate_scan_duration(metadata),
            "logicpwn_version": self.escape_html(getattr(metadata, 'logicpwn_version', 'Unknown')),
            "authenticated_user": self.escape_html(getattr(metadata, 'authenticated_user', None)),
            "export_timestamp": self.format_datetime(None)  # Current time
        }
        
        try:
            return renderer.render("html_template.html", context)
        except Exception as e:
            # Enhanced fallback with better structure and styling
            return self._generate_fallback_html(findings, metadata)

    def _prepare_finding_context(self, finding: VulnerabilityFinding) -> dict:
        """
        Prepare finding data for HTML context with XSS protection.
        
        Args:
            finding: Vulnerability finding
            
        Returns:
            Sanitized finding dictionary
        """
        return {
            "severity": self.escape_html(getattr(finding, 'severity', 'Unknown')),
            "title": self.escape_html(getattr(finding, 'title', 'Untitled')),
            "cvss_score": self._safe_cvss_score(getattr(finding, 'cvss_score', None)),
            "affected_endpoints": self._format_endpoints_html(getattr(finding, 'affected_endpoints', [])),
            "description": self._format_html_content(getattr(finding, 'description', 'No description')),
            "proof_of_concept": self._redact_sensitive_content(getattr(finding, 'proof_of_concept', 'No PoC')),
            "impact": self._format_html_content(getattr(finding, 'impact', 'Impact not specified')),
            "remediation": self._format_html_content(getattr(finding, 'remediation', 'Remediation not specified')),
            "references": self._format_references_html(getattr(finding, 'references', [])),
            "discovered_at": self.format_datetime(getattr(finding, 'discovered_at', None)),
            "severity_class": self._get_severity_css_class(getattr(finding, 'severity', 'Unknown'))
        }

    def _generate_fallback_html(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> str:
        """
        Generate fallback HTML with enhanced styling and structure.
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata
            
        Returns:
            HTML string
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{self.escape_html(metadata.title)}</title>",
            "    <style>",
            self._get_embedded_css(),
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='container'>",
            f"        <header class='report-header'>",
            f"            <h1>{self.escape_html(metadata.title)}</h1>",
            f"            <div class='metadata'>",
            f"                <p><strong>Target:</strong> {self.escape_html(metadata.target_url)}</p>",
            f"                <p><strong>Scan Period:</strong> {self._format_scan_period(metadata)}</p>",
            f"                <p><strong>Total Findings:</strong> {len(findings)}</p>",
            f"                <p><strong>Critical Issues:</strong> {self._count_findings_by_severity(findings, 'Critical')}</p>",
            f"            </div>",
            f"        </header>",
            "        <main>",
            "            <section class='findings-section'>",
            "                <h2>Vulnerability Details</h2>"
        ]
        
        # Add findings
        for finding in findings:
            html_parts.extend(self._format_finding_html(finding))
        
        # Add footer
        html_parts.extend([
            "            </section>",
            "        </main>",
            "        <footer class='report-footer'>",
            "            <h2>Report Information</h2>",
            "            <ul>",
            f"                <li><strong>Scan Duration:</strong> {self._calculate_scan_duration(metadata)}</li>",
            f"                <li><strong>LogicPwn Version:</strong> {self.escape_html(getattr(metadata, 'logicpwn_version', 'Unknown'))}</li>",
            f"                <li><strong>Authentication:</strong> {self.escape_html(getattr(metadata, 'authenticated_user', None))}</li>",
            f"                <li><strong>Generated:</strong> {self.format_datetime(None)}</li>",
            "            </ul>",
            "        </footer>",
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return '\n'.join(html_parts)

    def _format_finding_html(self, finding: VulnerabilityFinding) -> List[str]:
        """Format a single finding as HTML."""
        severity = getattr(finding, 'severity', 'Unknown')
        css_class = self._get_severity_css_class(severity)
        
        return [
            f"                <article class='finding {css_class}'>",
            f"                    <header class='finding-header'>",
            f"                        <h3><span class='severity'>{self.escape_html(severity)}</span> - {self.escape_html(getattr(finding, 'title', 'Untitled'))}</h3>",
            f"                        <div class='finding-meta'>",
            f"                            <span class='cvss'>CVSS: {self._safe_cvss_score(getattr(finding, 'cvss_score', None))}</span>",
            f"                            <span class='discovered'>Discovered: {self.format_datetime(getattr(finding, 'discovered_at', None))}</span>",
            f"                        </div>",
            f"                    </header>",
            f"                    <div class='finding-content'>",
            f"                        <div class='field'>",
            f"                            <h4>Affected Endpoints</h4>",
            f"                            <div class='endpoints'>{self._format_endpoints_html(getattr(finding, 'affected_endpoints', []))}</div>",
            f"                        </div>",
            f"                        <div class='field'>",
            f"                            <h4>Description</h4>",
            f"                            <div class='description'>{self._format_html_content(getattr(finding, 'description', 'No description'))}</div>",
            f"                        </div>",
            f"                        <div class='field'>",
            f"                            <h4>Proof of Concept</h4>",
            f"                            <pre class='poc'>{self.escape_html(getattr(finding, 'proof_of_concept', 'No PoC'))}</pre>",
            f"                        </div>",
            f"                        <div class='field'>",
            f"                            <h4>Impact</h4>",
            f"                            <div class='impact'>{self._format_html_content(getattr(finding, 'impact', 'Impact not specified'))}</div>",
            f"                        </div>",
            f"                        <div class='field'>",
            f"                            <h4>Remediation</h4>",
            f"                            <div class='remediation'>{self._format_html_content(getattr(finding, 'remediation', 'Remediation not specified'))}</div>",
            f"                        </div>",
            f"                        <div class='field'>",
            f"                            <h4>References</h4>",
            f"                            <div class='references'>{self._format_references_html(getattr(finding, 'references', []))}</div>",
            f"                        </div>",
            f"                    </div>",
            f"                </article>"
        ]

    def stream_export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata, file: IO, template_dir: Optional[str] = None):
        """
        Stream findings and metadata to a file in HTML format with memory efficiency.
        
        Args:
            findings: List of VulnerabilityFinding objects
            metadata: ReportMetadata object
            file: File-like object to write to
            template_dir: Optional custom template directory
        """
        try:
            # Validate inputs
            self.validate_inputs(findings, metadata)
            
            # Write HTML header
            file.write(f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
            file.write(f"    <meta charset='UTF-8'>\n")
            file.write(f"    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
            file.write(f"    <title>{self.escape_html(metadata.title)}</title>\n")
            file.write(f"    <style>{self._get_embedded_css()}</style>\n")
            file.write(f"</head>\n<body>\n")
            file.write(f"    <div class='container'>\n")
            
            # Write header section
            file.write(f"        <header class='report-header'>\n")
            file.write(f"            <h1>{self.escape_html(metadata.title)}</h1>\n")
            file.write(f"            <div class='metadata'>\n")
            file.write(f"                <p><strong>Target:</strong> {self.escape_html(metadata.target_url)}</p>\n")
            file.write(f"                <p><strong>Scan Period:</strong> {self._format_scan_period(metadata)}</p>\n")
            file.write(f"                <p><strong>Total Findings:</strong> {len(findings)}</p>\n")
            file.write(f"                <p><strong>Critical Issues:</strong> {self._count_findings_by_severity(findings, 'Critical')}</p>\n")
            file.write(f"            </div>\n")
            file.write(f"        </header>\n")
            
            # Write main content
            file.write(f"        <main>\n")
            file.write(f"            <section class='findings-section'>\n")
            file.write(f"                <h2>Vulnerability Details</h2>\n")
            
            # Stream each finding
            for finding in findings:
                finding_html = '\n'.join(self._format_finding_html(finding))
                file.write(finding_html + '\n')
            
            # Write footer
            file.write(f"            </section>\n")
            file.write(f"        </main>\n")
            file.write(f"        <footer class='report-footer'>\n")
            file.write(f"            <h2>Report Information</h2>\n")
            file.write(f"            <ul>\n")
            file.write(f"                <li><strong>Scan Duration:</strong> {self._calculate_scan_duration(metadata)}</li>\n")
            file.write(f"                <li><strong>LogicPwn Version:</strong> {self.escape_html(getattr(metadata, 'logicpwn_version', 'Unknown'))}</li>\n")
            file.write(f"                <li><strong>Authentication:</strong> {self.escape_html(getattr(metadata, 'authenticated_user', None))}</li>\n")
            file.write(f"                <li><strong>Generated:</strong> {self.format_datetime(None)}</li>\n")
            file.write(f"            </ul>\n")
            file.write(f"        </footer>\n")
            file.write(f"    </div>\n")
            file.write(f"</body>\n</html>\n")
            
        except Exception as e:
            raise ValueError(f"Failed to stream HTML export: {e}")

    # Helper methods
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

    def _format_endpoints_html(self, endpoints: any) -> str:
        """Format endpoints for HTML display."""
        if not endpoints:
            return "<em>No endpoints specified</em>"
        
        if isinstance(endpoints, list):
            escaped_endpoints = [self.escape_html(ep) for ep in endpoints if ep is not None]
            return "<ul>" + "".join([f"<li><code>{ep}</code></li>" for ep in escaped_endpoints]) + "</ul>"
        else:
            return f"<code>{self.escape_html(endpoints)}</code>"

    def _format_html_content(self, content: any) -> str:
        """Format content with line breaks preserved."""
        escaped = self.escape_html(content)
        return escaped.replace('\n', '<br>') if escaped != "N/A" else escaped

    def _format_code_html(self, code: any) -> str:
        """Format code content for HTML."""
        return self.escape_html(code)

    def _format_references_html(self, references: any) -> str:
        """Format references as HTML links."""
        if not references:
            return "<em>No references</em>"
        
        if isinstance(references, list):
            ref_links = []
            for ref in references:
                if ref is None:
                    continue
                escaped_ref = self.escape_html(ref)
                if ref.startswith(('http://', 'https://')):
                    ref_links.append(f"<a href='{escaped_ref}' target='_blank' rel='noopener'>{escaped_ref}</a>")
                else:
                    ref_links.append(escaped_ref)
            return "<ul>" + "".join([f"<li>{link}</li>" for link in ref_links]) + "</ul>" if ref_links else "<em>No valid references</em>"
        else:
            escaped_ref = self.escape_html(references)
            if references.startswith(('http://', 'https://')):
                return f"<a href='{escaped_ref}' target='_blank' rel='noopener'>{escaped_ref}</a>"
            else:
                return escaped_ref

    def _get_severity_css_class(self, severity: str) -> str:
        """Get CSS class for severity level."""
        severity_map = {
            'critical': 'severity-critical',
            'high': 'severity-high', 
            'medium': 'severity-medium',
            'low': 'severity-low'
        }
        return severity_map.get(str(severity).lower(), 'severity-unknown')

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

    def _get_embedded_css(self) -> str:
        """Get embedded CSS for enhanced styling."""
        return """
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .report-header { border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }
        .report-header h1 { color: #2c3e50; margin: 0 0 15px 0; font-size: 2.5em; }
        .metadata p { margin: 5px 0; color: #555; }
        .findings-section h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        .finding { margin: 25px 0; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
        .finding-header { padding: 15px 20px; font-weight: bold; }
        .severity-critical .finding-header { background: #e74c3c; color: white; }
        .severity-high .finding-header { background: #e67e22; color: white; }
        .severity-medium .finding-header { background: #f39c12; color: white; }
        .severity-low .finding-header { background: #27ae60; color: white; }
        .severity-unknown .finding-header { background: #95a5a6; color: white; }
        .finding-header h3 { margin: 0; font-size: 1.3em; }
        .finding-meta { margin-top: 8px; font-size: 0.9em; opacity: 0.9; }
        .finding-content { padding: 20px; }
        .field { margin-bottom: 20px; }
        .field h4 { margin: 0 0 8px 0; color: #2c3e50; font-size: 1.1em; }
        .field div, .field pre { background: #f8f9fa; padding: 12px; border-radius: 4px; border-left: 4px solid #3498db; }
        .poc { background: #2c3e50 !important; color: #ecf0f1; font-family: 'Courier New', monospace; white-space: pre-wrap; }
        .endpoints ul, .references ul { margin: 0; padding-left: 20px; }
        .endpoints code { background: #ecf0f1; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .references a { color: #3498db; text-decoration: none; }
        .references a:hover { text-decoration: underline; }
        .report-footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; }
        .report-footer ul { list-style: none; padding: 0; }
        .report-footer li { margin: 8px 0; color: #555; }
        """
        file.write(f"<ul><li><b>Scan Duration:</b> {metadata.scan_end_time - metadata.scan_start_time}</li>\n")
        file.write(f"<li><b>LogicPwn Version:</b> {metadata.logicpwn_version}</li>\n")
        file.write(f"<li><b>Authentication:</b> {metadata.authenticated_user or 'N/A'}</li></ul>\n")
        file.write("</body></html>\n") 