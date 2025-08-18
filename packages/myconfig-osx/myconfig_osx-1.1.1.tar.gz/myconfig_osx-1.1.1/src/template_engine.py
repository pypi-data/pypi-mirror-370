"""
Template engine for generating files from templates with variable substitution
"""

from __future__ import annotations
import os
import re
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class TemplateEngine:
    """Simple template engine with Mustache-like syntax"""
    
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "templates")
        self.logger = logging.getLogger(__name__)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return self._process_template(template_content, context)
    
    def render_to_file(self, template_name: str, context: Dict[str, Any], output_path: str) -> None:
        """Render template and write to file"""
        rendered_content = self.render_template(template_name, context)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
        
        self.logger.info(f"Generated file from template: {output_path}")
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Process template with context data"""
        # Handle conditional sections: {{#key}}...{{/key}}
        template = self._process_sections(template, context)
        
        # Handle simple variable substitution: {{variable}}
        template = self._process_variables(template, context)
        
        return template
    
    def _process_sections(self, template: str, context: Dict[str, Any]) -> str:
        """Process conditional sections"""
        # Pattern to match {{#key}}content{{/key}}
        section_pattern = r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}'
        
        def replace_section(match):
            key = match.group(1)
            content = match.group(2)
            
            if key in context and context[key]:
                # If key exists and is truthy, render the content
                if isinstance(context[key], dict):
                    # If it's a dict, use it as context for the section
                    return self._process_template(content, context[key])
                elif isinstance(context[key], list):
                    # If it's a list, render for each item
                    result = ""
                    for item in context[key]:
                        if isinstance(item, dict):
                            result += self._process_template(content, item)
                        else:
                            result += content
                    return result
                else:
                    # If it's a simple value, just render the content
                    return self._process_template(content, context)
            else:
                # If key doesn't exist or is falsy, remove the section
                return ""
        
        return re.sub(section_pattern, replace_section, template, flags=re.DOTALL)
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Process simple variable substitution"""
        def replace_variable(match):
            key = match.group(1)
            return str(context.get(key, f"{{{{key}}}}"))  # Keep original if not found
        
        # Pattern to match {{variable}}
        variable_pattern = r'\{\{(\w+)\}\}'
        return re.sub(variable_pattern, replace_variable, template)


class ExportTemplateRenderer:
    """Specialized template renderer for MyConfig exports"""
    
    def __init__(self):
        self.engine = TemplateEngine()
        self.logger = logging.getLogger(__name__)
    
    def create_readme(self, export_dir: str, context_data: Dict[str, Any]) -> None:
        """Create README.md from template"""
        readme_path = os.path.join(export_dir, "README.md")
        
        # Enhance context with helper functions
        enhanced_context = self._enhance_context(context_data)
        
        try:
            self.engine.render_to_file("README.md.template", enhanced_context, readme_path)
            self.logger.info("README.md generated successfully")
        except Exception as e:
            self.logger.error(f"Failed to generate README.md: {e}")
            # Fallback to simple text file
            self._create_fallback_readme(readme_path, context_data)
    
    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with computed values and formatting"""
        enhanced = context.copy()
        
        # Add formatting helpers
        if 'total_size' in enhanced:
            enhanced['total_size_formatted'] = self._format_size(enhanced['total_size'])
        
        # Format individual component sizes
        for component in ['dotfiles', 'defaults']:
            if component in enhanced and 'size' in enhanced[component]:
                enhanced[component]['size_formatted'] = self._format_size(enhanced[component]['size'])
        
        # Format defaults total size
        if 'defaults' in enhanced and 'total_size' in enhanced['defaults']:
            enhanced['defaults']['total_size_formatted'] = self._format_size(enhanced['defaults']['total_size'])
        
        return enhanced
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:,.1f} {unit}" if size_bytes != int(size_bytes) else f"{int(size_bytes):,} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:,.1f} TB"
    
    def _create_fallback_readme(self, readme_path: str, context: Dict[str, Any]) -> None:
        """Create a simple fallback README if template fails"""
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# MyConfig Export\n\n")
            f.write(f"Export Time: {context.get('export_time', 'Unknown')}\n")
            f.write(f"Hostname: {context.get('hostname', 'Unknown')}\n\n")
            f.write("This directory contains a MyConfig backup.\n")
            f.write("Use 'myconfig restore <this-directory>' to restore.\n")
        
        self.logger.warning("Created fallback README.md")


def create_template_context(export_dir: str) -> Dict[str, Any]:
    """Create template context by analyzing export directory"""
    from .utils import ts, host
    
    context = {
        'export_time': ts(),
        'hostname': host(),
        'version': '2.0',
        'total_components': 0,
        'total_files': 0,
        'total_size': 0
    }
    
    # Analyze system environment
    env_file = os.path.join(export_dir, "ENVIRONMENT.txt")
    if os.path.exists(env_file):
        context['system_environment'] = {
            'filename': 'ENVIRONMENT.txt',
            'size': os.path.getsize(env_file),
            'description': 'macOS version, hostname, Xcode tools info'
        }
        context['total_files'] += 1
        context['total_size'] += context['system_environment']['size']
    
    # Analyze Homebrew
    brewfile = os.path.join(export_dir, "Brewfile")
    if os.path.exists(brewfile):
        with open(brewfile, "r") as f:
            lines = f.readlines()
        
        context['homebrew'] = {
            'filename': 'Brewfile',
            'size': os.path.getsize(brewfile),
            'brew_count': len([l for l in lines if l.strip().startswith('brew ')]),
            'cask_count': len([l for l in lines if l.strip().startswith('cask ')]),
            'tap_count': len([l for l in lines if l.strip().startswith('tap ')])
        }
        
        version_file = os.path.join(export_dir, "HOMEBREW_VERSION.txt")
        if os.path.exists(version_file):
            context['homebrew']['version_file'] = 'HOMEBREW_VERSION.txt'
        
        context['total_files'] += 1
        context['total_size'] += context['homebrew']['size']
        context['total_components'] += 1
    
    # Analyze VS Code
    vscode_file = os.path.join(export_dir, "vscode_extensions.txt")
    if os.path.exists(vscode_file):
        with open(vscode_file, "r") as f:
            ext_count = len([l for l in f.readlines() if l.strip()])
        
        context['vscode'] = {
            'filename': 'vscode_extensions.txt',
            'size': os.path.getsize(vscode_file),
            'extension_count': ext_count
        }
        context['total_files'] += 1
        context['total_size'] += context['vscode']['size']
        context['total_components'] += 1
    
    # Analyze Dotfiles
    dotfiles_archive = os.path.join(export_dir, "dotfiles.tar.gz")
    if os.path.exists(dotfiles_archive):
        context['dotfiles'] = {
            'filename': 'dotfiles.tar.gz',
            'size': os.path.getsize(dotfiles_archive)
        }
        context['total_files'] += 1
        context['total_size'] += context['dotfiles']['size']
        context['total_components'] += 1
    
    # Analyze Defaults
    defaults_dir = os.path.join(export_dir, "defaults")
    if os.path.isdir(defaults_dir):
        plist_files = [f for f in os.listdir(defaults_dir) if f.endswith('.plist')]
        total_size = sum(os.path.getsize(os.path.join(defaults_dir, pf)) for pf in plist_files)
        
        # Create domain list (show first few, then "and X more")
        domain_list = ', '.join(plist_files[:3])
        if len(plist_files) > 3:
            domain_list += f" and {len(plist_files) - 3} more"
        
        context['defaults'] = {
            'directory': 'defaults/',
            'file_count': len(plist_files),
            'total_size': total_size,
            'domain_list': domain_list
        }
        context['total_files'] += len(plist_files)
        context['total_size'] += total_size
        context['total_components'] += 1
    
    # Analyze LaunchAgents
    la_dir = os.path.join(export_dir, "LaunchAgents")
    if os.path.isdir(la_dir):
        plist_files = [f for f in os.listdir(la_dir) if f.endswith('.plist')]
        context['launchagents'] = {
            'directory': 'LaunchAgents/',
            'service_count': len(plist_files)
        }
        context['total_files'] += len(plist_files)
        context['total_components'] += 1
    
    # Analyze MAS
    mas_file = os.path.join(export_dir, "mas.list")
    if os.path.exists(mas_file):
        with open(mas_file, "r") as f:
            app_count = len([l for l in f.readlines() if l.strip()])
        
        context['mas'] = {
            'filename': 'mas.list',
            'app_count': app_count
        }
        context['total_files'] += 1
        context['total_components'] += 1
    
    # Check for manifest
    manifest_file = os.path.join(export_dir, "MANIFEST.json")
    if os.path.exists(manifest_file):
        context['manifest'] = {
            'manifest_file': 'MANIFEST.json'
        }
        context['total_files'] += 1
    
    return context
