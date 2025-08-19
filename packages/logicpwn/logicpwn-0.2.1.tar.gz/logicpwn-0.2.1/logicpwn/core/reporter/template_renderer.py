from typing import Dict, Any
import os

class TemplateRenderer:
    """
    Utility for rendering report templates using Jinja2 if available, or string replacement fallback.
    Supports custom template directories for branding and localization.
    """
    def __init__(self, template_dir: str = "logicpwn/templates"):
        """
        Initialize the template renderer.
        :param template_dir: Directory containing template files.
        """
        self.template_dir = template_dir
        try:
            from jinja2 import Environment, FileSystemLoader
            self.env = Environment(loader=FileSystemLoader(self.template_dir))
        except ImportError:
            self.env = None

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        Uses Jinja2 if available, otherwise falls back to string replacement.
        :param template_name: Name of the template file.
        :param context: Dictionary of variables for template rendering.
        :return: Rendered string.
        """
        if self.env:
            template = self.env.get_template(template_name)
            return template.render(**context)
        else:
            # Fallback: simple string replacement
            path = os.path.join(self.template_dir, template_name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for k, v in context.items():
                content = content.replace(f"{{{{{k}}}}}", str(v))
            return content 