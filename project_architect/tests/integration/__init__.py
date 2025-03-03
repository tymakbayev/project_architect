"""
Integration tests package for Project Architect.

This package contains integration tests for the Project Architect application.
Integration tests focus on testing the interaction between different components
and ensuring that they work together correctly as a complete system.

The integration tests verify that:
1. The entire project generation pipeline works end-to-end
2. The API endpoints function correctly
3. The CLI commands produce expected results
4. The generated projects are valid and complete
5. External service integrations (Anthropic API, GitHub API) work properly

These tests require configuration of external services and may take longer to run
than unit tests. Some tests may be skipped if the required API keys or credentials
are not available.
"""

import os
import sys
import logging
import pytest
from typing import Dict, Any, List, Optional, Callable, Generator
from pathlib import Path

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test utilities and fixtures
from tests.conftest import (
    mock_anthropic_client,
    mock_github_client,
    temp_output_dir,
    sample_project_description,
    sample_project_config,
    api_client
)

# Import application components for testing
from src.project_generator import ProjectGenerator
from src.interfaces.api import app
from src.interfaces.cli import CLI
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient
from src.config import Config

# Setup package-level logger
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

# Constants for integration tests
TEST_PROJECT_NAME = "test_project"
TEST_PROJECT_DESCRIPTION = "A simple test project for integration testing"
TEST_OUTPUT_DIR = "test_output"

# Define what's available when using "from requirements.txt import *"
__all__ = [
    'IntegrationTestBase',
    'skip_if_no_api_key',
    'skip_if_no_github_token',
    'verify_project_structure',
    'verify_project_files',
    'verify_project_dependencies',
    'run_generated_project',
    'TEST_PROJECT_NAME',
    'TEST_PROJECT_DESCRIPTION',
    'TEST_OUTPUT_DIR'
]


class IntegrationTestBase:
    """Base class for integration tests providing common functionality."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class with common resources."""
        cls.config = Config()
        cls.logger = logging.getLogger(__name__)
        
        # Create a temporary directory for test outputs
        cls.test_output_dir = Path(TEST_OUTPUT_DIR)
        cls.test_output_dir.mkdir(exist_ok=True)
    
    @classmethod
    def teardown_class(cls):
        """Clean up resources after tests are complete."""
        # Remove test output directory if it exists and is empty
        if cls.test_output_dir.exists() and not any(cls.test_output_dir.iterdir()):
            cls.test_output_dir.rmdir()
    
    def setup_method(self):
        """Set up resources before each test method."""
        # Create a unique subdirectory for this test
        self.test_dir = self.test_output_dir / f"test_{os.urandom(4).hex()}"
        self.test_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up resources after each test method."""
        # Optional: Remove test directory and its contents
        # Commented out to allow inspection of test results
        # import shutil
        # shutil.rmtree(self.test_dir, ignore_errors=True)
        pass


def skip_if_no_api_key(func: Callable) -> Callable:
    """Decorator to skip tests if no Anthropic API key is available."""
    def wrapper(*args, **kwargs):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("Anthropic API key not available")
        return func(*args, **kwargs)
    return wrapper


def skip_if_no_github_token(func: Callable) -> Callable:
    """Decorator to skip tests if no GitHub token is available."""
    def wrapper(*args, **kwargs):
        if not os.environ.get("GITHUB_TOKEN"):
            pytest.skip("GitHub token not available")
        return func(*args, **kwargs)
    return wrapper


def verify_project_structure(output_dir: Path, expected_structure: Dict[str, Any]) -> List[str]:
    """Verify that the generated project structure matches the expected structure.
    
    Args:
        output_dir: Path to the generated project directory
        expected_structure: Dictionary representing the expected structure
        
    Returns:
        List of error messages, empty if structure is valid
    """
    errors = []
    
    # Check directories
    for dir_name in expected_structure.get("directories", []):
        dir_path = output_dir / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            errors.append(f"Expected directory '{dir_name}' not found")
    
    # Check files
    for file_name in expected_structure.get("files", []):
        file_path = output_dir / file_name
        if not file_path.exists() or not file_path.is_file():
            errors.append(f"Expected file '{file_name}' not found")
    
    return errors


def verify_project_files(output_dir: Path, file_content_checks: Dict[str, List[str]]) -> List[str]:
    """Verify that the generated project files contain expected content.
    
    Args:
        output_dir: Path to the generated project directory
        file_content_checks: Dictionary mapping file paths to lists of expected content strings
        
    Returns:
        List of error messages, empty if all content checks pass
    """
    errors = []
    
    for file_path, expected_contents in file_content_checks.items():
        full_path = output_dir / file_path
        
        if not full_path.exists():
            errors.append(f"File '{file_path}' not found for content verification")
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for expected in expected_contents:
                if expected not in content:
                    errors.append(f"Expected content '{expected}' not found in '{file_path}'")
        except Exception as e:
            errors.append(f"Error reading file '{file_path}': {str(e)}")
    
    return errors


def verify_project_dependencies(output_dir: Path, expected_dependencies: List[str]) -> List[str]:
    """Verify that the generated project includes expected dependencies.
    
    Args:
        output_dir: Path to the generated project directory
        expected_dependencies: List of expected dependency names
        
    Returns:
        List of error messages, empty if all dependencies are found
    """
    errors = []
    dependency_files = [
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "package.json"
    ]
    
    # Find dependency files
    found_files = []
    for dep_file in dependency_files:
        if (output_dir / dep_file).exists():
            found_files.append(output_dir / dep_file)
    
    if not found_files:
        return ["No dependency files found in the generated project"]
    
    # Check dependencies in found files
    all_content = ""
    for file_path in found_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_content += f.read()
        except Exception as e:
            errors.append(f"Error reading dependency file '{file_path}': {str(e)}")
    
    for dependency in expected_dependencies:
        if dependency.lower() not in all_content.lower():
            errors.append(f"Expected dependency '{dependency}' not found in dependency files")
    
    return errors


def run_generated_project(output_dir: Path) -> Dict[str, Any]:
    """Attempt to run the generated project to verify it's functional.
    
    Args:
        output_dir: Path to the generated project directory
        
    Returns:
        Dictionary with results of the test run
    """
    import subprocess
    
    result = {
        "success": False,
        "output": "",
        "error": "",
        "return_code": None
    }
    
    # Try to find a main entry point
    possible_entry_points = [
        "main.py",
        "app.py",
        "src/main.py",
        "index.js",
        "src/index.js"
    ]
    
    entry_point = None
    for ep in possible_entry_points:
        if (output_dir / ep).exists():
            entry_point = ep
            break
    
    if not entry_point:
        result["error"] = "No entry point found in the generated project"
        return result
    
    # Determine how to run the entry point
    if entry_point.endswith(".py"):
        cmd = ["python", entry_point]
    elif entry_point.endswith(".js"):
        cmd = ["node", entry_point]
    else:
        result["error"] = f"Unsupported entry point: {entry_point}"
        return result
    
    # Run the command
    try:
        process = subprocess.run(
            cmd,
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=30  # Timeout after 30 seconds
        )
        
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["return_code"] = process.returncode
        result["success"] = process.returncode == 0
    except subprocess.TimeoutExpired:
        result["error"] = "Process timed out after 30 seconds"
    except Exception as e:
        result["error"] = f"Error running the generated project: {str(e)}"
    
    return result