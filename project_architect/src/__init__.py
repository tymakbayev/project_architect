"""
Project Architect Package.

This package provides tools for analyzing project descriptions and generating
complete project architectures, structures, and code files for various technology stacks.

The package uses AI models from Anthropic (Claude) to analyze project requirements
and generate appropriate code and architecture plans.
"""

__version__ = "0.1.0"
__author__ = "Project Architect Team"
__license__ = "MIT"

# Import core components for easy access
from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.core.project_structure_generator import ProjectStructureGenerator
from src.core.code_generator import CodeGenerator
from src.core.dependency_manager import DependencyManager

# Import main project generator
from src.project_generator import ProjectGenerator

# Import interfaces
from src.interfaces.cli import CLI
from src.interfaces.api import app as api_app

# Import clients
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient

# Import output manager
from src.output.project_output_manager import ProjectOutputManager

# Import configuration
from src.config import Config

# Setup package-level logger
import logging
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

# Define what's available when using "from src import *"
__all__ = [
    'ProjectAnalyzer',
    'ArchitectureGenerator',
    'ProjectStructureGenerator',
    'CodeGenerator',
    'DependencyManager',
    'ProjectGenerator',
    'CLI',
    'api_app',
    'AnthropicClient',
    'GithubClient',
    'ProjectOutputManager',
    'Config',
]