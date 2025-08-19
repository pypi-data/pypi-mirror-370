from typing import List, Any, Optional, IO
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
import re

class BaseExporter:
    """
    Base exporter class with enhanced validation and error handling.
    """
    
    def export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> str:
        """
        Export findings and metadata to string format.
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata
            
        Returns:
            Formatted string output
            
        Raises:
            ValueError: If input data is invalid
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement export method")
    
    def stream_export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata, file: IO) -> None:
        """
        Stream export findings to file (optional for subclasses).
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata  
            file: File-like object to write to
        """
        # Default implementation writes export() result to file
        content = self.export(findings, metadata)
        file.write(content)
    
    def validate_inputs(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> None:
        """
        Validate input data for export.
        
        Args:
            findings: List of vulnerability findings
            metadata: Report metadata
            
        Raises:
            ValueError: If validation fails
            TypeError: If input types are incorrect
        """
        # Validate findings
        if not isinstance(findings, list):
            raise TypeError("findings must be a list")
        
        # Validate metadata
        if metadata is None:
            raise ValueError("metadata cannot be None")
        
        # Validate required metadata fields
        required_fields = ['title', 'target_url', 'scan_start_time', 'scan_end_time']
        for field in required_fields:
            if not hasattr(metadata, field):
                raise ValueError(f"metadata missing required field: {field}")
            
            value = getattr(metadata, field)
            if value is None:
                raise ValueError(f"metadata.{field} cannot be None")
            
            if field in ['title', 'target_url'] and not str(value).strip():
                raise ValueError(f"metadata.{field} cannot be empty")
    
    def sanitize_text(self, text: Any) -> str:
        """
        Safely sanitize text for output with None handling.
        
        Args:
            text: Input text (can be None)
            
        Returns:
            Sanitized string
        """
        if text is None:
            return "N/A"
        
        text_str = str(text)
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text_str)
        
        return sanitized.strip() if sanitized.strip() else "N/A"
    
    def escape_html(self, text: Any) -> str:
        """
        Escape HTML special characters to prevent injection.
        
        Args:
            text: Input text
            
        Returns:
            HTML-escaped string
        """
        if text is None:
            return "N/A"
        
        text_str = str(text)
        
        # HTML escape mappings
        html_escape_table = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;"
        }
        
        for char, escape in html_escape_table.items():
            text_str = text_str.replace(char, escape)
        
        return self.sanitize_text(text_str)
    
    def format_datetime(self, dt) -> str:
        """
        Format datetime for consistent display.
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted datetime string
        """
        if dt is None:
            return "N/A"
        
        try:
            # Handle both datetime objects and ISO strings
            if hasattr(dt, 'isoformat'):
                return dt.isoformat()
            else:
                return str(dt)
        except Exception:
            return "N/A"
    
    def safe_join(self, items: Any, separator: str = ", ") -> str:
        """
        Safely join list items with None handling.
        
        Args:
            items: List of items to join
            separator: Separator string
            
        Returns:
            Joined string
        """
        if items is None:
            return "N/A"
        
        if not isinstance(items, list):
            return self.sanitize_text(items)
        
        if not items:
            return "N/A"
        
        # Filter out None values and sanitize
        clean_items = [self.sanitize_text(item) for item in items if item is not None]
        
        return separator.join(clean_items) if clean_items else "N/A"


def get_exporter(format: str) -> BaseExporter:
    """
    Factory function to get exporter instance with enhanced validation.
    
    Args:
        format: Export format (json, html, markdown, md)
        
    Returns:
        BaseExporter instance
        
    Raises:
        ValueError: If format is unsupported
        TypeError: If format is not string
    """
    if not isinstance(format, str):
        raise TypeError("format must be a string")
    
    format = format.lower().strip()
    
    if not format:
        raise ValueError("format cannot be empty")
    
    if format in ("md", "markdown"):
        from .markdown_exporter import MarkdownExporter
        return MarkdownExporter()
    elif format == "json":
        from .json_exporter import JSONExporter
        return JSONExporter()
    elif format == "html":
        from .html_exporter import HTMLExporter
        return HTMLExporter()
    else:
        supported_formats = ["json", "html", "markdown", "md"]
        raise ValueError(f"Unsupported export format: {format}. Supported formats: {supported_formats}") 