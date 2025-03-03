"""
Templates package for Project Architect.

This package contains template modules for different technology stacks supported by
the Project Architect. These templates provide base structures, common patterns, and
code snippets that are used by the code generator to create consistent and idiomatic
code for various project types.

Templates are organized by technology stack (Python, React, Node.js, etc.) and provide
both structural templates (directory layouts, file organization) and code templates
(common patterns, boilerplate code, configuration files).
"""

from typing import Dict, Any, List, Optional, Union, Callable, Type
import logging
import os
import json
import importlib
from pathlib import Path
from enum import Enum, auto

# Import template modules
from src.templates.python_templates import PythonTemplates
from src.templates.react_templates import ReactTemplates
from src.templates.node_templates import NodeTemplates

# Setup package-level logger
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

__all__ = [
    'PythonTemplates',
    'ReactTemplates',
    'NodeTemplates',
    'TemplateManager',
    'TemplateType',
    'get_template_for_project_type',
    'render_template',
]


class TemplateType(Enum):
    """Enumeration of supported template types."""
    PYTHON = auto()
    REACT = auto()
    NODE = auto()
    DJANGO = auto()
    FLASK = auto()
    FASTAPI = auto()
    EXPRESS = auto()
    NEXTJS = auto()
    ANGULAR = auto()
    VUE = auto()
    SPRING_BOOT = auto()
    DOTNET = auto()
    GENERIC = auto()


# Mapping from project types to template classes
TEMPLATE_MAP = {
    'python': PythonTemplates,
    'react': ReactTemplates,
    'node': NodeTemplates,
    'django': PythonTemplates,  # Django uses Python templates with specialization
    'flask': PythonTemplates,   # Flask uses Python templates with specialization
    'fastapi': PythonTemplates, # FastAPI uses Python templates with specialization
    'express': NodeTemplates,   # Express uses Node templates with specialization
    'nextjs': ReactTemplates,   # Next.js uses React templates with specialization
}


def get_template_for_project_type(project_type: str) -> Any:
    """Get the appropriate template class for a given project type.
    
    Args:
        project_type: The type of project (e.g., 'python', 'react', 'node')
        
    Returns:
        The template class for the specified project type
        
    Raises:
        ValueError: If the project type is not supported
    """
    project_type = project_type.lower()
    
    if project_type not in TEMPLATE_MAP:
        logger.warning(f"No specific template for project type '{project_type}', using generic templates")
        # Default to Python templates as a fallback
        return PythonTemplates
    
    return TEMPLATE_MAP[project_type]


def render_template(template_name: str, context: Dict[str, Any], project_type: str) -> str:
    """Render a template with the given context.
    
    Args:
        template_name: The name of the template to render
        context: The context data to use for rendering
        project_type: The type of project (e.g., 'python', 'react', 'node')
        
    Returns:
        The rendered template as a string
        
    Raises:
        ValueError: If the template is not found
    """
    template_class = get_template_for_project_type(project_type)
    
    if not hasattr(template_class, template_name):
        raise ValueError(f"Template '{template_name}' not found for project type '{project_type}'")
    
    template_method = getattr(template_class, template_name)
    return template_method(context)


class TemplateManager:
    """Manages templates for different project types and provides rendering capabilities.
    
    This class serves as a central point for accessing and rendering templates for
    different project types. It handles template loading, caching, and rendering.
    """
    
    def __init__(self):
        """Initialize the template manager."""
        self.templates: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load all available templates
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all available template classes."""
        self.templates = {
            'python': PythonTemplates(),
            'react': ReactTemplates(),
            'node': NodeTemplates(),
            # Add more template types as they become available
        }
        
        # Add aliases for specialized frameworks
        self.templates['django'] = self.templates['python']
        self.templates['flask'] = self.templates['python']
        self.templates['fastapi'] = self.templates['python']
        self.templates['express'] = self.templates['node']
        self.templates['nextjs'] = self.templates['react']
        
        self.logger.debug(f"Loaded templates for: {', '.join(self.templates.keys())}")
    
    def get_template(self, project_type: str) -> Any:
        """Get the template instance for a specific project type.
        
        Args:
            project_type: The type of project (e.g., 'python', 'react', 'node')
            
        Returns:
            The template instance for the specified project type
            
        Raises:
            ValueError: If the project type is not supported
        """
        project_type = project_type.lower()
        
        if project_type not in self.templates:
            self.logger.warning(f"No specific template for project type '{project_type}', using python templates")
            return self.templates['python']
        
        return self.templates[project_type]
    
    def render(self, template_name: str, context: Dict[str, Any], project_type: str) -> str:
        """Render a template with the given context.
        
        Args:
            template_name: The name of the template to render
            context: The context data to use for rendering
            project_type: The type of project (e.g., 'python', 'react', 'node')
            
        Returns:
            The rendered template as a string
            
        Raises:
            ValueError: If the template is not found
        """
        template = self.get_template(project_type)
        
        if not hasattr(template, template_name):
            raise ValueError(f"Template '{template_name}' not found for project type '{project_type}'")
        
        template_method = getattr(template, template_name)
        return template_method(context)
    
    def list_available_templates(self, project_type: str) -> List[str]:
        """List all available templates for a specific project type.
        
        Args:
            project_type: The type of project (e.g., 'python', 'react', 'node')
            
        Returns:
            A list of available template names
            
        Raises:
            ValueError: If the project type is not supported
        """
        template = self.get_template(project_type)
        
        # Get all public methods (templates) from the template class
        return [
            method for method in dir(template)
            if callable(getattr(template, method)) and not method.startswith('_')
        ]
    
    def get_template_metadata(self, template_name: str, project_type: str) -> Dict[str, Any]:
        """Get metadata for a specific template.
        
        Args:
            template_name: The name of the template
            project_type: The type of project (e.g., 'python', 'react', 'node')
            
        Returns:
            A dictionary containing template metadata
            
        Raises:
            ValueError: If the template is not found
        """
        template = self.get_template(project_type)
        
        if not hasattr(template, template_name):
            raise ValueError(f"Template '{template_name}' not found for project type '{project_type}'")
        
        template_method = getattr(template, template_name)
        
        # Extract metadata from docstring if available
        metadata = {
            'name': template_name,
            'description': template_method.__doc__ or "No description available",
            'project_type': project_type,
        }
        
        return metadata


# Create a singleton instance of the template manager
template_manager = TemplateManager()