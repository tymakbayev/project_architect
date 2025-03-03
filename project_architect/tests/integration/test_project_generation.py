#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for the Project Generation process.

This module contains integration tests for the complete project generation pipeline,
ensuring that the entire system works together correctly from project description
to final output. These tests verify that:
1. The project analyzer correctly identifies project types
2. The architecture generator creates appropriate architecture plans
3. The project structure generator builds valid directory structures
4. The code generator produces syntactically correct and functional code
5. The dependency manager identifies and includes necessary dependencies
6. The output manager correctly packages the generated project
"""

import os
import sys
import json
import shutil
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import application components for testing
from src.project_generator import ProjectGenerator
from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.core.project_structure_generator import ProjectStructureGenerator
from src.core.code_generator import CodeGenerator
from src.core.dependency_manager import DependencyManager
from src.output.project_output_manager import ProjectOutputManager
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient
from src.config import Config
from src.models.project_type import ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan
from src.models.project_structure import ProjectStructure
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec

from requirements.txt import (
    IntegrationTestBase,
    skip_if_no_api_key,
    skip_if_no_github_token,
    verify_project_structure,
    verify_project_files,
    verify_project_dependencies,
    TEST_PROJECT_NAME,
    TEST_PROJECT_DESCRIPTION,
    TEST_OUTPUT_DIR
)


class TestProjectGeneration(IntegrationTestBase):
    """Integration tests for the complete project generation pipeline."""

    @classmethod
    def setup_class(cls):
        """Set up the test class with common resources."""
        super().setup_class()
        
        # Sample project descriptions for different types of projects
        cls.project_descriptions = {
            "python_web": "A web application using FastAPI with SQLAlchemy ORM, PostgreSQL database, "
                         "JWT authentication, and Swagger documentation. Include unit tests with pytest.",
            
            "react_frontend": "A React single-page application with Redux for state management, "
                             "React Router for navigation, Material-UI for components, and Jest for testing.",
            
            "node_backend": "A Node.js REST API using Express.js, MongoDB with Mongoose, "
                           "JWT authentication, and Swagger documentation. Include unit tests with Jest.",
            
            "fullstack": "A full-stack application with a React frontend, Node.js backend using Express, "
                        "MongoDB database, and user authentication. Include Docker configuration."
        }
        
        # Expected project types for each description
        cls.expected_project_types = {
            "python_web": ProjectTypeEnum.PYTHON_WEB,
            "react_frontend": ProjectTypeEnum.REACT,
            "node_backend": ProjectTypeEnum.NODE,
            "fullstack": ProjectTypeEnum.FULLSTACK
        }

    def setup_method(self):
        """Set up resources before each test method."""
        super().setup_method()
        
        # Create a mock Anthropic client for testing
        self.mock_anthropic_client = MagicMock(spec=AnthropicClient)
        
        # Create a mock GitHub client for testing
        self.mock_github_client = MagicMock(spec=GithubClient)
        
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a configuration for testing
        self.config = Config()
        
        # Create the project generator with mock clients
        self.project_generator = ProjectGenerator(
            anthropic_client=self.mock_anthropic_client,
            github_client=self.mock_github_client,
            config=self.config
        )
        
        # Set up mock responses for the Anthropic client
        self._setup_mock_anthropic_responses()
    
    def teardown_method(self):
        """Clean up resources after each test method."""
        super().teardown_method()
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_mock_anthropic_responses(self):
        """Set up mock responses for the Anthropic client."""
        # Mock response for project type analysis
        self.mock_anthropic_client.analyze_project_type.return_value = ProjectTypeEnum.PYTHON_WEB
        
        # Mock response for architecture generation
        mock_architecture = ArchitecturePlan(
            project_type=ProjectTypeEnum.PYTHON_WEB,
            components=[
                {"name": "api", "description": "FastAPI application", "dependencies": ["fastapi", "uvicorn"]},
                {"name": "database", "description": "Database models and connection", "dependencies": ["sqlalchemy", "psycopg2-binary"]},
                {"name": "auth", "description": "Authentication and authorization", "dependencies": ["python-jose", "passlib"]},
                {"name": "utils", "description": "Utility functions", "dependencies": []}
            ],
            layers=[
                {"name": "presentation", "components": ["api"]},
                {"name": "business_logic", "components": ["auth"]},
                {"name": "data_access", "components": ["database"]},
                {"name": "common", "components": ["utils"]}
            ],
            external_dependencies=[
                {"name": "PostgreSQL", "version": "13", "purpose": "Database server"},
                {"name": "Redis", "version": "6", "purpose": "Caching (optional)"}
            ],
            deployment_considerations="Can be deployed as Docker containers or on a PaaS like Heroku."
        )
        self.mock_anthropic_client.generate_architecture.return_value = mock_architecture
        
        # Mock response for project structure generation
        mock_structure = ProjectStructure(
            root_dir=TEST_PROJECT_NAME,
            directories=[
                "app",
                "app/api",
                "app/database",
                "app/auth",
                "app/utils",
                "tests",
                "docs"
            ],
            files=[
                "app/__init__.py",
                "app/main.py",
                "app/config.py",
                "app/api/__init__.py",
                "app/api/routes.py",
                "app/database/__init__.py",
                "app/database/models.py",
                "app/database/connection.py",
                "app/auth/__init__.py",
                "app/auth/jwt.py",
                "app/utils/__init__.py",
                "app/utils/helpers.py",
                "tests/__init__.py",
                "tests/test_api.py",
                "tests/test_auth.py",
                "README.md",
                "requirements.txt",
                ".env.example",
                "Dockerfile",
                "docker-compose.yml"
            ]
        )
        self.mock_anthropic_client.generate_project_structure.return_value = mock_structure
        
        # Mock response for code generation
        mock_code_files = [
            CodeFile(
                path="app/__init__.py",
                content='"""Main application package."""\n\n__version__ = "0.1.0"'
            ),
            CodeFile(
                path="app/main.py",
                content='''"""Main FastAPI application module."""

import uvicorn
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to the API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
'''
            ),
            CodeFile(
                path="app/config.py",
                content='''"""Configuration settings for the application."""

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    PROJECT_NAME: str = "FastAPI Application"
    PROJECT_DESCRIPTION: str = "A web application using FastAPI"
    VERSION: str = "0.1.0"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/app")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        """Pydantic config."""
        env_file = ".env"

settings = Settings()
'''
            ),
            # Additional mock code files would be added here
        ]
        self.mock_anthropic_client.generate_code_files.return_value = mock_code_files
        
        # Mock response for dependency management
        mock_dependencies = [
            DependencySpec(name="fastapi", version="^0.68.0"),
            DependencySpec(name="uvicorn", version="^0.15.0"),
            DependencySpec(name="sqlalchemy", version="^1.4.23"),
            DependencySpec(name="psycopg2-binary", version="^2.9.1"),
            DependencySpec(name="python-jose", version="^3.3.0"),
            DependencySpec(name="passlib", version="^1.7.4"),
            DependencySpec(name="python-dotenv", version="^0.19.0"),
            DependencySpec(name="pydantic", version="^1.8.2"),
            DependencySpec(name="pytest", version="^6.2.5", dev=True),
            DependencySpec(name="black", version="^21.8b0", dev=True),
            DependencySpec(name="isort", version="^5.9.3", dev=True),
            DependencySpec(name="flake8", version="^3.9.2", dev=True)
        ]
        self.mock_anthropic_client.generate_dependencies.return_value = mock_dependencies

    @patch('src.output.project_output_manager.ProjectOutputManager')
    def test_end_to_end_project_generation(self, mock_output_manager_class):
        """Test the complete project generation process from description to output."""
        # Set up the mock output manager
        mock_output_manager = MagicMock()
        mock_output_manager_class.return_value = mock_output_manager
        
        # Configure the project generator
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory",
            "technology_preferences": ["python", "fastapi"],
            "include_tests": True,
            "include_documentation": True
        }
        
        # Generate the project
        result = self.project_generator.generate_project(**project_config)
        
        # Verify that all the necessary methods were called
        self.mock_anthropic_client.analyze_project_type.assert_called_once()
        self.mock_anthropic_client.generate_architecture.assert_called_once()
        self.mock_anthropic_client.generate_project_structure.assert_called_once()
        self.mock_anthropic_client.generate_code_files.assert_called_once()
        self.mock_anthropic_client.generate_dependencies.assert_called_once()
        
        # Verify that the output manager was called correctly
        mock_output_manager.create_project_files.assert_called_once()
        mock_output_manager.package_project.assert_called_once()
        
        # Verify the result
        assert result["success"] is True
        assert "project_type" in result
        assert "architecture" in result
        assert "structure" in result
        assert "code_files" in result
        assert "dependencies" in result
        assert "output_path" in result
        
        # Verify the project type
        assert result["project_type"] == ProjectTypeEnum.PYTHON_WEB

    @patch('src.core.project_analyzer.ProjectAnalyzer.analyze')
    @patch('src.core.architecture_generator.ArchitectureGenerator.generate')
    @patch('src.core.project_structure_generator.ProjectStructureGenerator.generate')
    @patch('src.core.code_generator.CodeGenerator.generate')
    @patch('src.core.dependency_manager.DependencyManager.generate')
    @patch('src.output.project_output_manager.ProjectOutputManager')
    def test_project_generation_component_integration(
        self, 
        mock_output_manager_class,
        mock_dependency_generate,
        mock_code_generate,
        mock_structure_generate,
        mock_architecture_generate,
        mock_project_analyze
    ):
        """Test the integration between actual components of the project generation pipeline."""
        # Set up the mock output manager
        mock_output_manager = MagicMock()
        mock_output_manager_class.return_value = mock_output_manager
        
        # Set up mock returns for each component
        mock_project_analyze.return_value = ProjectTypeEnum.PYTHON_WEB
        mock_architecture_generate.return_value = self.mock_anthropic_client.generate_architecture.return_value
        mock_structure_generate.return_value = self.mock_anthropic_client.generate_project_structure.return_value
        mock_code_generate.return_value = self.mock_anthropic_client.generate_code_files.return_value
        mock_dependency_generate.return_value = self.mock_anthropic_client.generate_dependencies.return_value
        
        # Create actual component instances
        project_analyzer = ProjectAnalyzer(self.mock_anthropic_client, self.mock_github_client, self.config)
        architecture_generator = ArchitectureGenerator(self.mock_anthropic_client, self.mock_github_client, self.config)
        structure_generator = ProjectStructureGenerator(self.mock_anthropic_client, self.mock_github_client, self.config)
        code_generator = CodeGenerator(self.mock_anthropic_client, self.mock_github_client, self.config)
        dependency_manager = DependencyManager(self.mock_anthropic_client, self.mock_github_client, self.config)
        
        # Create a project generator with the actual components
        project_generator = ProjectGenerator(
            anthropic_client=self.mock_anthropic_client,
            github_client=self.mock_github_client,
            config=self.config,
            project_analyzer=project_analyzer,
            architecture_generator=architecture_generator,
            structure_generator=structure_generator,
            code_generator=code_generator,
            dependency_manager=dependency_manager
        )
        
        # Configure the project generator
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory",
            "technology_preferences": ["python", "fastapi"],
            "include_tests": True,
            "include_documentation": True
        }
        
        # Generate the project
        result = project_generator.generate_project(**project_config)
        
        # Verify that all the necessary methods were called
        mock_project_analyze.assert_called_once()
        mock_architecture_generate.assert_called_once()
        mock_structure_generate.assert_called_once()
        mock_code_generate.assert_called_once()
        mock_dependency_generate.assert_called_once()
        
        # Verify that the output manager was called correctly
        mock_output_manager.create_project_files.assert_called_once()
        mock_output_manager.package_project.assert_called_once()
        
        # Verify the result
        assert result["success"] is True
        assert result["project_type"] == ProjectTypeEnum.PYTHON_WEB

    @skip_if_no_api_key
    def test_project_generation_with_real_anthropic_client(self):
        """Test project generation with the real Anthropic client (requires API key)."""
        # Create a real Anthropic client
        real_anthropic_client = AnthropicClient(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Create a project generator with the real client
        project_generator = ProjectGenerator(
            anthropic_client=real_anthropic_client,
            github_client=self.mock_github_client,
            config=self.config
        )
        
        # Configure a simple project for generation
        project_config = {
            "name": "simple_test_project",
            "description": "A simple Python CLI tool that converts CSV files to JSON format.",
            "output_dir": self.temp_dir,
            "output_format": "directory",
            "technology_preferences": ["python"],
            "include_tests": True,
            "include_documentation": False
        }
        
        # Generate the project
        result = project_generator.generate_project(**project_config)
        
        # Verify the result
        assert result["success"] is True
        assert "project_type" in result
        assert "architecture" in result
        assert "structure" in result
        assert "code_files" in result
        assert "dependencies" in result
        assert "output_path" in result
        
        # Verify the output path exists
        output_path = Path(result["output_path"])
        assert output_path.exists()
        
        # Verify some basic files exist
        assert (output_path / "README.md").exists()
        assert any(output_path.glob("**/*.py"))

    def test_project_generation_with_different_project_types(self):
        """Test project generation with different project types."""
        for project_key, description in self.project_descriptions.items():
            # Set the expected project type for this description
            self.mock_anthropic_client.analyze_project_type.return_value = self.expected_project_types[project_key]
            
            # Configure the project generator
            project_config = {
                "name": f"test_{project_key}",
                "description": description,
                "output_dir": self.temp_dir,
                "output_format": "directory",
                "include_tests": True,
                "include_documentation": True
            }
            
            # Generate the project
            result = self.project_generator.generate_project(**project_config)
            
            # Verify the result
            assert result["success"] is True
            assert result["project_type"] == self.expected_project_types[project_key]

    def test_project_generation_with_error_handling(self):
        """Test project generation with error handling for various failure scenarios."""
        # Test with Anthropic client failing at project analysis
        self.mock_anthropic_client.analyze_project_type.side_effect = Exception("API error")
        
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory"
        }
        
        # Generate the project and expect failure
        result = self.project_generator.generate_project(**project_config)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to analyze project type" in result["error"]
        
        # Reset the mock and test with architecture generation failing
        self.mock_anthropic_client.analyze_project_type.side_effect = None
        self.mock_anthropic_client.generate_architecture.side_effect = Exception("Architecture generation failed")
        
        # Generate the project and expect failure
        result = self.project_generator.generate_project(**project_config)
        assert result["success"] is False
        assert "error" in result
        assert "Failed to generate architecture" in result["error"]
        
        # Reset all mocks to normal behavior
        self._setup_mock_anthropic_responses()

    def test_project_generation_with_custom_templates(self):
        """Test project generation with custom templates."""
        # Create a custom template
        custom_template = {
            "name": "custom_python_template",
            "files": [
                {
                    "path": "custom_template.py",
                    "content": "# This is a custom template file\n\ndef main():\n    print('Hello from custom template')\n\nif __name__ == '__main__':\n    main()"
                }
            ]
        }
        
        # Configure the project generator with the custom template
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory",
            "custom_templates": [custom_template]
        }
        
        # Mock the output manager to capture the files
        with patch('src.output.project_output_manager.ProjectOutputManager') as mock_output_manager_class:
            mock_output_manager = MagicMock()
            mock_output_manager_class.return_value = mock_output_manager
            
            # Generate the project
            result = self.project_generator.generate_project(**project_config)
            
            # Verify that the custom template was included
            create_project_files_call = mock_output_manager.create_project_files.call_args[0]
            code_files = create_project_files_call[0]
            
            # Check if the custom template file is in the code files
            custom_file_paths = [file.path for file in code_files if file.path == "custom_template.py"]
            assert len(custom_file_paths) > 0

    @patch('src.output.project_output_manager.ProjectOutputManager')
    def test_project_generation_with_different_output_formats(self, mock_output_manager_class):
        """Test project generation with different output formats."""
        mock_output_manager = MagicMock()
        mock_output_manager_class.return_value = mock_output_manager
        
        # Test with directory output format
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory"
        }
        
        result = self.project_generator.generate_project(**project_config)
        assert result["success"] is True
        mock_output_manager.package_project.assert_called_with("directory")
        
        # Reset mock and test with zip output format
        mock_output_manager.reset_mock()
        project_config["output_format"] = "zip"
        
        result = self.project_generator.generate_project(**project_config)
        assert result["success"] is True
        mock_output_manager.package_project.assert_called_with("zip")
        
        # Reset mock and test with tar.gz output format
        mock_output_manager.reset_mock()
        project_config["output_format"] = "tar.gz"
        
        result = self.project_generator.generate_project(**project_config)
        assert result["success"] is True
        mock_output_manager.package_project.assert_called_with("tar.gz")

    def test_project_generation_cancellation(self):
        """Test cancellation of project generation process."""
        # Create a mock for the cancellation token
        mock_cancellation_token = MagicMock()
        mock_cancellation_token.is_cancelled.return_value = False
        
        # Configure the project generator
        project_config = {
            "name": TEST_PROJECT_NAME,
            "description": self.project_descriptions["python_web"],
            "output_dir": self.temp_dir,
            "output_format": "directory",
            "cancellation_token": mock_cancellation_token
        }
        
        # Start generation but then cancel during architecture generation
        def side_effect(*args, **kwargs):
            mock_cancellation_token.is_cancelled.return_value = True
            return self.mock_anthropic_client.generate_architecture.return_value
        
        self.mock_anthropic_client.generate_architecture.side_effect = side_effect
        
        # Generate the project and expect cancellation
        result = self.project_generator.generate_project(**project_config)
        
        # Verify the result indicates cancellation
        assert result["success"] is False
        assert "error" in result
        assert "cancelled" in result["error"].lower()


if __name__ == "__main__":
    pytest.main(["-v", __file__])