#!/usr/bin/env python3
"""
Template Manager for GitHub Actions workflows

Provides fast, token-efficient workflow generation using pre-built templates
instead of generating everything through Claude.
"""

import os
from pathlib import Path
from typing import Dict, Optional

class TemplateManager:
    def __init__(self, templates_dir: str = None):
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to templates directory relative to this file
            self.templates_dir = Path(__file__).parent
        
    def get_template(self, project_type: str) -> Optional[str]:
        """Get the CI template for a specific project type."""
        template_map = {
            'python': 'python-ci.yml',
            'node': 'node-ci.yml', 
            'rust': 'rust-ci.yml',
            'go': 'go-ci.yml',
            'java': 'java-ci.yml',
            'php': 'php-ci.yml',
            'ruby': 'ruby-ci.yml',
            'dotnet': 'dotnet-ci.yml',
            'generic': 'generic-ci.yml'
        }
        
        template_file = template_map.get(project_type, 'generic-ci.yml')
        template_path = self.templates_dir / template_file
        
        if template_path.exists():
            return template_path.read_text()
        return None
    
    def get_security_template(self) -> Optional[str]:
        """Get the security scanning template."""
        security_path = self.templates_dir / 'security.yml'
        if security_path.exists():
            return security_path.read_text()
        return None
    
    def list_templates(self) -> Dict[str, str]:
        """List all available templates."""
        templates = {}
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob('*.yml'):
                templates[template_file.stem] = str(template_file)
        return templates
    
    def customize_template(self, template_content: str, project_name: str = None) -> str:
        """Apply basic customizations to template."""
        if project_name:
            # Could add project-specific customizations here
            pass
        return template_content

# Usage example:
if __name__ == "__main__":
    tm = TemplateManager()
    
    # Get Python template
    python_template = tm.get_template('python')
    print("Python Template:")
    print(python_template)
    
    # List all templates
    print("\nAvailable templates:")
    for name, path in tm.list_templates().items():
        print(f"  {name}: {path}")