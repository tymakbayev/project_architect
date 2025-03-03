"""
Tests package for Project Architect.

This package contains all tests for the Project Architect application, including
unit tests for individual components and integration tests for the complete system.

The test suite is organized into two main categories:
- Unit tests: Testing individual components in isolation
- Integration tests: Testing the interaction between components

The package uses pytest as the testing framework and provides fixtures and utilities
for setting up test environments and mocking external dependencies.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Union, Callable

# Ensure the src directory is in the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test utilities and fixtures
from requirements.txt.conftest import (
    mock_anthropic_client,
    mock_github_client,
    test_config,
    temp_output_dir,
    sample_project_description,
    sample_architecture_plan,
    sample_project_structure,
    sample_code_files
)

# Import unit test modules for easy access
from requirements.txt.unit.test_project_analyzer import TestProjectAnalyzer
from requirements.txt.unit.test_architecture_generator import TestArchitectureGenerator
from requirements.txt.unit.test_project_structure_generator import TestProjectStructureGenerator
from requirements.txt.unit.test_code_generator import TestCodeGenerator
from requirements.txt.unit.test_dependency_manager import TestDependencyManager
from requirements.txt.unit.test_anthropic_client import TestAnthropicClient
from requirements.txt.unit.test_github_client import TestGithubClient

# Import integration test modules
from requirements.txt.integration.test_project_generation import TestProjectGeneration
from requirements.txt.integration.test_api import TestAPI

# Setup test logger
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger(level=logging.DEBUG)

# Define what's available when using "from requirements.txt import *"
__all__ = [
    # Test fixtures
    'mock_anthropic_client',
    'mock_github_client',
    'test_config',
    'temp_output_dir',
    'sample_project_description',
    'sample_architecture_plan',
    'sample_project_structure',
    'sample_code_files',
    
    # Unit test classes
    'TestProjectAnalyzer',
    'TestArchitectureGenerator',
    'TestProjectStructureGenerator',
    'TestCodeGenerator',
    'TestDependencyManager',
    'TestAnthropicClient',
    'TestGithubClient',
    
    # Integration test classes
    'TestProjectGeneration',
    'TestAPI',
]

# Test package version
__version__ = "0.1.0"


def run_all_tests() -> None:
    """Run all tests in the test suite.
    
    This function provides a programmatic way to run all tests without using
    the pytest command line interface.
    
    Returns:
        None
    """
    import pytest
    pytest.main(['-xvs', os.path.dirname(__file__)])


def run_unit_tests() -> None:
    """Run only unit tests.
    
    Returns:
        None
    """
    import pytest
    pytest.main(['-xvs', os.path.join(os.path.dirname(__file__), 'unit')])


def run_integration_tests() -> None:
    """Run only integration tests.
    
    Returns:
        None
    """
    import pytest
    pytest.main(['-xvs', os.path.join(os.path.dirname(__file__), 'integration')])


def run_with_coverage() -> None:
    """Run all tests with coverage reporting.
    
    Returns:
        None
    """
    import pytest
    pytest.main(['-xvs', '--cov=src', '--cov-report=term-missing', os.path.dirname(__file__)])


# Initialize test environment if needed
if os.environ.get('INITIALIZE_TEST_ENV', 'false').lower() == 'true':
    logger.info("Initializing test environment")
    # Any additional setup that might be needed when the package is imported