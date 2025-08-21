# resumate/template_loader.py
import yaml
import os
from pathlib import Path
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

class TemplateLoader:
    """Load templates from bundled resources or custom files."""
    
    def __init__(self):
        self.builtin_templates = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load all built-in templates from package."""
        try:
            import resumate.templates as templates_module
            
            # List all files in the templates directory
            template_files = [f for f in resources.contents(templates_module) 
                            if f.endswith('.yaml')]
            
            for filename in template_files:
                # Load template content just to get the name
                template_content = resources.read_text(templates_module, filename)
                template_data = yaml.safe_load(template_content)
                
                # Map the name to the actual file path
                template_name = template_data.get('name', filename.replace('.yaml', ''))
                
                # Store the PATH to the template file, not the content
                import resumate
                template_path = os.path.join(os.path.dirname(resumate.__file__), 'templates', filename)
                self.builtin_templates[template_name] = template_path
                
        except Exception as e:
            print(f"Warning: Could not load built-in templates: {e}")
    
    def resolve_template_path(self, template_identifier):
        """
        Resolve a template name or path to an actual file path.
        
        Args:
            template_identifier: Either a template name (built-in) or file path
            
        Returns:
            Actual file path to the template
        """
        # Check if it's already a valid file path
        if os.path.exists(template_identifier):
            return template_identifier
        
        # Check if it's a built-in template name
        if template_identifier in self.builtin_templates:
            return self.builtin_templates[template_identifier]
        
        # Try with .yaml extension
        yaml_path = f"{template_identifier}.yaml"
        if os.path.exists(yaml_path):
            return yaml_path
        
        # Check in templates directory relative to current path
        local_template = Path('templates') / f"{template_identifier}.yaml"
        if local_template.exists():
            return str(local_template)
        
        raise ValueError(
            f"Template '{template_identifier}' not found. "
            f"Available built-in templates: {', '.join(self.builtin_templates.keys())}"
        )
    
    def list_templates(self):
        """List all available built-in templates."""
        templates = []
        for name, path in self.builtin_templates.items():
            # Load just to get description
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            templates.append({
                'name': name,
                'description': data.get('description', 'No description'),
                'version': data.get('version', '1.0')
            })
        return templates

# Singleton instance
template_loader = TemplateLoader()