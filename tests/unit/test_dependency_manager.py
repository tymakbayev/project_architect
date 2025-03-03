#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the DependencyManager module.

This module contains tests for the DependencyManager class, which is responsible for
analyzing project requirements and generating appropriate dependency specifications
for different technology stacks.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.core.dependency_manager import DependencyManager
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.dependency_spec import DependencySpec
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient


class TestDependencyManager:
    """Test suite for the DependencyManager class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AnthropicClient for testing."""
        with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
            client_instance = mock_client.return_value
            client_instance.generate_response.return_value = json.dumps({
                "dependencies": {
                    "python": [
                        {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"},
                        {"name": "uvicorn", "version": "^0.22.0", "purpose": "ASGI server"},
                        {"name": "sqlalchemy", "version": "^2.0.0", "purpose": "ORM"},
                        {"name": "pydantic", "version": "^1.10.7", "purpose": "Data validation"}
                    ],
                    "javascript": [
                        {"name": "react", "version": "^18.2.0", "purpose": "UI library"},
                        {"name": "axios", "version": "^1.3.6", "purpose": "HTTP client"},
                        {"name": "material-ui", "version": "^5.12.1", "purpose": "UI components"}
                    ],
                    "dev": [
                        {"name": "pytest", "version": "^7.3.1", "purpose": "Testing"},
                        {"name": "black", "version": "^23.3.0", "purpose": "Code formatting"},
                        {"name": "eslint", "version": "^8.39.0", "purpose": "JavaScript linting"}
                    ]
                },
                "package_files": {
                    "python": "requirements.txt",
                    "javascript": "package.json",
                    "dev": ["dev-requirements.txt", "package.json"]
                }
            })
            yield client_instance

    @pytest.fixture
    def mock_github_client(self):
        """Create a mock GithubClient for testing."""
        with mock.patch('src.clients.github_client.GithubClient') as mock_client:
            client_instance = mock_client.return_value
            client_instance.get_popular_dependencies.return_value = {
                "python": [
                    {"name": "fastapi", "stars": 50000, "description": "FastAPI framework"},
                    {"name": "sqlalchemy", "stars": 45000, "description": "SQL toolkit and ORM"}
                ],
                "javascript": [
                    {"name": "react", "stars": 180000, "description": "A JavaScript library for building user interfaces"},
                    {"name": "axios", "stars": 95000, "description": "Promise based HTTP client"}
                ]
            }
            yield client_instance

    @pytest.fixture
    def dependency_manager(self, mock_anthropic_client, mock_github_client):
        """Create a DependencyManager instance with mocked clients."""
        manager = DependencyManager(api_key="test_api_key")
        manager.anthropic_client = mock_anthropic_client
        manager.github_client = mock_github_client
        return manager

    @pytest.fixture
    def sample_project_type(self):
        """Return a sample ProjectType instance for testing."""
        return ProjectType(
            type=ProjectTypeEnum.WEB_APPLICATION,
            frontend_framework="React",
            backend_framework="FastAPI",
            database="PostgreSQL",
            description="A web application with React frontend and FastAPI backend",
            features=["User authentication", "Data visualization", "REST API"],
            complexity="Medium"
        )

    @pytest.fixture
    def sample_architecture_plan(self):
        """Return a sample architecture plan dictionary for testing."""
        return {
            "components": [
                {
                    "name": "Frontend",
                    "type": "UI",
                    "description": "React-based user interface",
                    "technologies": ["React", "TypeScript", "Material-UI"]
                },
                {
                    "name": "Backend API",
                    "type": "Service",
                    "description": "FastAPI-based REST API",
                    "technologies": ["FastAPI", "SQLAlchemy", "Pydantic"]
                },
                {
                    "name": "Database",
                    "type": "Storage",
                    "description": "PostgreSQL database",
                    "technologies": ["PostgreSQL"]
                }
            ]
        }

    def test_init(self):
        """Test the initialization of DependencyManager."""
        # Test with API key
        manager = DependencyManager(api_key="test_api_key")
        assert isinstance(manager.anthropic_client, AnthropicClient)
        assert manager.anthropic_client.api_key == "test_api_key"
        
        # Test with existing client
        mock_client = mock.MagicMock()
        manager = DependencyManager(anthropic_client=mock_client)
        assert manager.anthropic_client == mock_client
        
        # Test with GitHub client
        github_client = mock.MagicMock()
        manager = DependencyManager(api_key="test_api_key", github_client=github_client)
        assert manager.github_client == github_client
        
        # Test with neither API key nor client
        with pytest.raises(ValueError):
            DependencyManager()

    def test_generate_dependencies(self, dependency_manager, sample_project_type, sample_architecture_plan):
        """Test generating dependencies based on project type and architecture plan."""
        # Call the method
        dependencies = dependency_manager.generate_dependencies(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan
        )
        
        # Verify the result
        assert isinstance(dependencies, DependencySpec)
        
        # Check Python dependencies
        assert len(dependencies.python) >= 4
        assert any(dep["name"] == "fastapi" for dep in dependencies.python)
        assert any(dep["name"] == "uvicorn" for dep in dependencies.python)
        assert any(dep["name"] == "sqlalchemy" for dep in dependencies.python)
        assert any(dep["name"] == "pydantic" for dep in dependencies.python)
        
        # Check JavaScript dependencies
        assert len(dependencies.javascript) >= 3
        assert any(dep["name"] == "react" for dep in dependencies.javascript)
        assert any(dep["name"] == "axios" for dep in dependencies.javascript)
        assert any(dep["name"] == "material-ui" for dep in dependencies.javascript)
        
        # Check dev dependencies
        assert len(dependencies.dev) >= 3
        assert any(dep["name"] == "pytest" for dep in dependencies.dev)
        assert any(dep["name"] == "black" for dep in dependencies.dev)
        assert any(dep["name"] == "eslint" for dep in dependencies.dev)
        
        # Check package files
        assert dependencies.package_files["python"] == "requirements.txt"
        assert dependencies.package_files["javascript"] == "package.json"
        assert "dev-requirements.txt" in dependencies.package_files["dev"]
        assert "package.json" in dependencies.package_files["dev"]
        
        # Verify the Claude API was called with the right prompt
        dependency_manager.anthropic_client.generate_response.assert_called_once()
        call_args = dependency_manager.anthropic_client.generate_response.call_args[0][0]
        assert "dependencies" in call_args.lower()
        assert "project type" in call_args.lower()
        assert "architecture plan" in call_args.lower()

    def test_generate_dependencies_with_custom_requirements(self, dependency_manager, sample_project_type, sample_architecture_plan):
        """Test generating dependencies with custom requirements."""
        # Define custom requirements
        custom_requirements = [
            "Must support GraphQL",
            "Needs real-time updates with WebSockets",
            "Should include data visualization capabilities"
        ]
        
        # Call the method
        dependencies = dependency_manager.generate_dependencies(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            custom_requirements=custom_requirements
        )
        
        # Verify the result
        assert isinstance(dependencies, DependencySpec)
        
        # Verify the Claude API was called with the right prompt including custom requirements
        dependency_manager.anthropic_client.generate_response.assert_called_once()
        call_args = dependency_manager.anthropic_client.generate_response.call_args[0][0]
        for req in custom_requirements:
            assert req in call_args

    def test_enrich_with_github_data(self, dependency_manager, sample_project_type):
        """Test enriching dependencies with GitHub data."""
        # Create a basic dependency spec
        basic_deps = DependencySpec(
            python=[
                {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"},
                {"name": "sqlalchemy", "version": "^2.0.0", "purpose": "ORM"}
            ],
            javascript=[
                {"name": "react", "version": "^18.2.0", "purpose": "UI library"},
                {"name": "axios", "version": "^1.3.6", "purpose": "HTTP client"}
            ],
            dev=[],
            package_files={
                "python": "requirements.txt",
                "javascript": "package.json"
            }
        )
        
        # Mock the GitHub client response
        dependency_manager.github_client.get_popular_dependencies.return_value = {
            "python": [
                {"name": "fastapi", "stars": 50000, "description": "FastAPI framework"},
                {"name": "sqlalchemy", "stars": 45000, "description": "SQL toolkit and ORM"}
            ],
            "javascript": [
                {"name": "react", "stars": 180000, "description": "A JavaScript library for building user interfaces"},
                {"name": "axios", "stars": 95000, "description": "Promise based HTTP client"}
            ]
        }
        
        # Call the method
        enriched_deps = dependency_manager._enrich_with_github_data(basic_deps)
        
        # Verify the result
        assert isinstance(enriched_deps, DependencySpec)
        
        # Check Python dependencies are enriched
        python_fastapi = next(dep for dep in enriched_deps.python if dep["name"] == "fastapi")
        assert python_fastapi.get("stars") == 50000
        assert "description" in python_fastapi
        
        python_sqlalchemy = next(dep for dep in enriched_deps.python if dep["name"] == "sqlalchemy")
        assert python_sqlalchemy.get("stars") == 45000
        assert "description" in python_sqlalchemy
        
        # Check JavaScript dependencies are enriched
        js_react = next(dep for dep in enriched_deps.javascript if dep["name"] == "react")
        assert js_react.get("stars") == 180000
        assert "description" in js_react
        
        js_axios = next(dep for dep in enriched_deps.javascript if dep["name"] == "axios")
        assert js_axios.get("stars") == 95000
        assert "description" in js_axios
        
        # Verify GitHub client was called
        dependency_manager.github_client.get_popular_dependencies.assert_called_once()

    def test_generate_requirements_txt(self, dependency_manager):
        """Test generating requirements.txt content."""
        # Create a dependency spec
        deps = DependencySpec(
            python=[
                {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"},
                {"name": "uvicorn", "version": "^0.22.0", "purpose": "ASGI server"},
                {"name": "sqlalchemy", "version": "^2.0.0", "purpose": "ORM"},
                {"name": "pydantic", "version": "^1.10.7", "purpose": "Data validation"}
            ],
            javascript=[],
            dev=[],
            package_files={"python": "requirements.txt"}
        )
        
        # Call the method
        content = dependency_manager.generate_requirements_txt(deps)
        
        # Verify the result
        assert "fastapi==0.95.0" in content
        assert "uvicorn==0.22.0" in content
        assert "sqlalchemy==2.0.0" in content
        assert "pydantic==1.10.7" in content
        
        # Check format
        lines = content.strip().split("\n")
        assert len(lines) == 4
        for line in lines:
            assert "==" in line

    def test_generate_package_json(self, dependency_manager):
        """Test generating package.json content."""
        # Create a dependency spec
        deps = DependencySpec(
            python=[],
            javascript=[
                {"name": "react", "version": "^18.2.0", "purpose": "UI library"},
                {"name": "axios", "version": "^1.3.6", "purpose": "HTTP client"},
                {"name": "material-ui", "version": "^5.12.1", "purpose": "UI components"}
            ],
            dev=[
                {"name": "eslint", "version": "^8.39.0", "purpose": "JavaScript linting"},
                {"name": "jest", "version": "^29.5.0", "purpose": "Testing"}
            ],
            package_files={"javascript": "package.json"}
        )
        
        # Call the method
        content = dependency_manager.generate_package_json(deps, "test-project", "A test project")
        
        # Parse the JSON
        package_json = json.loads(content)
        
        # Verify the result
        assert package_json["name"] == "test-project"
        assert package_json["description"] == "A test project"
        assert "version" in package_json
        
        # Check dependencies
        assert "dependencies" in package_json
        assert package_json["dependencies"]["react"] == "^18.2.0"
        assert package_json["dependencies"]["axios"] == "^1.3.6"
        assert package_json["dependencies"]["material-ui"] == "^5.12.1"
        
        # Check dev dependencies
        assert "devDependencies" in package_json
        assert package_json["devDependencies"]["eslint"] == "^8.39.0"
        assert package_json["devDependencies"]["jest"] == "^29.5.0"
        
        # Check scripts
        assert "scripts" in package_json
        assert "start" in package_json["scripts"]
        assert "build" in package_json["scripts"]
        assert "test" in package_json["scripts"]

    def test_generate_dependency_files(self, dependency_manager, tmp_path):
        """Test generating dependency files."""
        # Create a dependency spec
        deps = DependencySpec(
            python=[
                {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"},
                {"name": "uvicorn", "version": "^0.22.0", "purpose": "ASGI server"}
            ],
            javascript=[
                {"name": "react", "version": "^18.2.0", "purpose": "UI library"},
                {"name": "axios", "version": "^1.3.6", "purpose": "HTTP client"}
            ],
            dev=[
                {"name": "pytest", "version": "^7.3.1", "purpose": "Testing"},
                {"name": "eslint", "version": "^8.39.0", "purpose": "JavaScript linting"}
            ],
            package_files={
                "python": "requirements.txt",
                "javascript": "package.json",
                "dev": ["dev-requirements.txt", "package.json"]
            }
        )
        
        # Create a temporary directory for output
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()
        
        # Call the method
        files = dependency_manager.generate_dependency_files(
            deps, 
            output_dir=str(output_dir),
            project_name="test-project",
            project_description="A test project"
        )
        
        # Verify the result
        assert len(files) == 2
        assert "requirements.txt" in files
        assert "package.json" in files
        
        # Check that files were created
        assert (output_dir / "requirements.txt").exists()
        assert (output_dir / "package.json").exists()
        
        # Check requirements.txt content
        requirements_content = (output_dir / "requirements.txt").read_text()
        assert "fastapi==0.95.0" in requirements_content
        assert "uvicorn==0.22.0" in requirements_content
        assert "pytest==7.3.1" in requirements_content  # Dev dependency
        
        # Check package.json content
        package_json_content = (output_dir / "package.json").read_text()
        package_json = json.loads(package_json_content)
        assert package_json["name"] == "test-project"
        assert package_json["description"] == "A test project"
        assert package_json["dependencies"]["react"] == "^18.2.0"
        assert package_json["dependencies"]["axios"] == "^1.3.6"
        assert package_json["devDependencies"]["eslint"] == "^8.39.0"

    def test_parse_claude_response(self, dependency_manager):
        """Test parsing Claude API response."""
        # Sample Claude response
        claude_response = json.dumps({
            "dependencies": {
                "python": [
                    {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"},
                    {"name": "uvicorn", "version": "^0.22.0", "purpose": "ASGI server"}
                ],
                "javascript": [
                    {"name": "react", "version": "^18.2.0", "purpose": "UI library"}
                ],
                "dev": [
                    {"name": "pytest", "version": "^7.3.1", "purpose": "Testing"}
                ]
            },
            "package_files": {
                "python": "requirements.txt",
                "javascript": "package.json",
                "dev": ["dev-requirements.txt", "package.json"]
            }
        })
        
        # Call the method
        result = dependency_manager._parse_claude_response(claude_response)
        
        # Verify the result
        assert isinstance(result, DependencySpec)
        assert len(result.python) == 2
        assert len(result.javascript) == 1
        assert len(result.dev) == 1
        assert result.package_files["python"] == "requirements.txt"
        assert result.package_files["javascript"] == "package.json"
        assert "dev-requirements.txt" in result.package_files["dev"]

    def test_parse_claude_response_invalid_json(self, dependency_manager):
        """Test parsing invalid JSON from Claude API."""
        # Invalid JSON response
        invalid_response = "This is not valid JSON"
        
        # Call the method and expect an exception
        with pytest.raises(ValueError):
            dependency_manager._parse_claude_response(invalid_response)

    def test_parse_claude_response_missing_fields(self, dependency_manager):
        """Test parsing Claude response with missing fields."""
        # Response with missing fields
        incomplete_response = json.dumps({
            "dependencies": {
                "python": [
                    {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"}
                ]
            }
            # Missing package_files
        })
        
        # Call the method
        result = dependency_manager._parse_claude_response(incomplete_response)
        
        # Verify the result has default values for missing fields
        assert isinstance(result, DependencySpec)
        assert len(result.python) == 1
        assert len(result.javascript) == 0
        assert len(result.dev) == 0
        assert result.package_files == {}

    @mock.patch('os.path.exists')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_generate_dependency_files_existing_files(self, mock_open, mock_exists, dependency_manager):
        """Test generating dependency files when files already exist."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a dependency spec
        deps = DependencySpec(
            python=[
                {"name": "fastapi", "version": "^0.95.0", "purpose": "Web framework"}
            ],
            javascript=[],
            dev=[],
            package_files={"python": "requirements.txt"}
        )
        
        # Call the method
        files = dependency_manager.generate_dependency_files(
            deps, 
            output_dir="/fake/path",
            project_name="test-project",
            project_description="A test project"
        )
        
        # Verify the result
        assert len(files) == 1
        assert "requirements.txt" in files
        
        # Verify file was written
        mock_open.assert_called_once_with('/fake/path/requirements.txt', 'w')
        mock_open().write.assert_called_once()

    def test_normalize_version(self, dependency_manager):
        """Test normalizing version strings."""
        # Test cases
        test_cases = [
            ("^0.95.0", "0.95.0"),
            ("~1.2.3", "1.2.3"),
            (">= 2.0.0", "2.0.0"),
            ("2.1.*", "2.1.0"),
            ("latest", "latest"),
            ("", ""),
            (None, "")
        ]
        
        # Test each case
        for input_version, expected_output in test_cases:
            assert dependency_manager._normalize_version(input_version) == expected_output

    def test_get_prompt_for_dependencies(self, dependency_manager, sample_project_type, sample_architecture_plan):
        """Test generating the prompt for dependencies."""
        # Call the method
        prompt = dependency_manager._get_prompt_for_dependencies(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            custom_requirements=["Support for GraphQL"]
        )
        
        # Verify the prompt contains key information
        assert "dependencies" in prompt.lower()
        assert "web application" in prompt.lower()
        assert "react" in prompt.lower()
        assert "fastapi" in prompt.lower()
        assert "postgresql" in prompt.lower()
        assert "support for graphql" in prompt.lower()
        
        # Verify the prompt asks for JSON format
        assert "json" in prompt.lower()
        assert "format" in prompt.lower()

if __name__ == "__main__":
    pytest.main(["-v", __file__])