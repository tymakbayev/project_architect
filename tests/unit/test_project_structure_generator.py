#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the ProjectStructureGenerator module.

This module contains tests for the ProjectStructureGenerator class, which is responsible for
generating the directory and file structure for a project based on its architecture plan
and project type.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.core.project_structure_generator import ProjectStructureGenerator
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component
from src.models.project_structure import ProjectStructure, DirectoryNode, FileNode
from src.clients.anthropic_client import AnthropicClient


class TestProjectStructureGenerator:
    """Test suite for the ProjectStructureGenerator class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AnthropicClient for testing."""
        with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
            client_instance = mock_client.return_value
            client_instance.generate_response.return_value = json.dumps({
                "root_directory": "expense_tracker",
                "directories": [
                    "frontend",
                    "backend",
                    "docs",
                    "frontend/src",
                    "frontend/public",
                    "frontend/src/components",
                    "frontend/src/pages",
                    "frontend/src/utils",
                    "backend/app",
                    "backend/tests",
                    "backend/app/models",
                    "backend/app/api",
                    "backend/app/services"
                ],
                "files": [
                    "README.md",
                    "docker-compose.yml",
                    ".gitignore",
                    "frontend/package.json",
                    "frontend/tsconfig.json",
                    "frontend/src/index.tsx",
                    "frontend/src/App.tsx",
                    "frontend/src/components/Navbar.tsx",
                    "frontend/src/pages/Dashboard.tsx",
                    "backend/requirements.txt",
                    "backend/app/main.py",
                    "backend/app/models/user.py",
                    "backend/app/api/auth.py",
                    "docs/API.md"
                ]
            })
            yield client_instance

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
        """Return a sample ArchitecturePlan instance for testing."""
        return ArchitecturePlan(
            components=[
                Component(
                    name="Frontend",
                    type="UI",
                    description="React-based user interface",
                    responsibilities=["Display data", "Handle user input"],
                    technologies=["React", "TypeScript", "Material-UI"]
                ),
                Component(
                    name="Backend API",
                    type="Service",
                    description="FastAPI-based REST API",
                    responsibilities=["Process requests", "Manage data"],
                    technologies=["FastAPI", "Python", "SQLAlchemy"]
                ),
                Component(
                    name="Database",
                    type="Storage",
                    description="PostgreSQL database",
                    responsibilities=["Store data"],
                    technologies=["PostgreSQL"]
                )
            ],
            dependencies=[],
            data_flows=[]
        )

    @pytest.fixture
    def project_structure_generator(self, mock_anthropic_client):
        """Create a ProjectStructureGenerator instance with mocked client."""
        generator = ProjectStructureGenerator(api_key="test_api_key")
        generator.anthropic_client = mock_anthropic_client
        return generator

    def test_init(self):
        """Test the initialization of ProjectStructureGenerator."""
        # Test with API key
        generator = ProjectStructureGenerator(api_key="test_api_key")
        assert isinstance(generator.anthropic_client, AnthropicClient)
        assert generator.anthropic_client.api_key == "test_api_key"
        
        # Test with existing client
        mock_client = mock.MagicMock()
        generator = ProjectStructureGenerator(anthropic_client=mock_client)
        assert generator.anthropic_client == mock_client
        
        # Test with neither API key nor client
        with pytest.raises(ValueError):
            ProjectStructureGenerator()

    def test_generate_project_structure(self, project_structure_generator, sample_project_type, sample_architecture_plan):
        """Test generating a project structure from a project type and architecture plan."""
        project_structure = project_structure_generator.generate_project_structure(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_name="expense_tracker"
        )
        
        # Verify the result is a ProjectStructure instance
        assert isinstance(project_structure, ProjectStructure)
        
        # Verify the root directory name
        assert project_structure.root_directory == "expense_tracker"
        
        # Verify the structure contains expected directories and files
        assert any(d.path == "frontend" for d in project_structure.directories)
        assert any(d.path == "backend" for d in project_structure.directories)
        assert any(d.path == "docs" for d in project_structure.directories)
        assert any(f.path == "README.md" for f in project_structure.files)
        assert any(f.path == "docker-compose.yml" for f in project_structure.files)
        
        # Verify the client was called with the correct prompt
        project_structure_generator.anthropic_client.generate_response.assert_called_once()
        call_args = project_structure_generator.anthropic_client.generate_response.call_args[0][0]
        assert "project structure" in call_args.lower()
        assert "React" in call_args
        assert "FastAPI" in call_args
        assert "PostgreSQL" in call_args

    def test_generate_project_structure_with_custom_name(self, project_structure_generator, sample_project_type, sample_architecture_plan):
        """Test generating a project structure with a custom project name."""
        project_structure = project_structure_generator.generate_project_structure(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_name="custom_project_name"
        )
        
        # Verify the custom project name is used
        assert project_structure.root_directory == "custom_project_name"

    def test_parse_structure_response(self, project_structure_generator):
        """Test parsing the structure response from the AI model."""
        response_json = {
            "root_directory": "test_project",
            "directories": [
                "src",
                "tests",
                "docs",
                "src/components",
                "src/utils"
            ],
            "files": [
                "README.md",
                "package.json",
                "src/index.js",
                "src/components/App.js",
                "tests/App.test.js"
            ]
        }
        
        project_structure = project_structure_generator._parse_structure_response(
            json.dumps(response_json)
        )
        
        # Verify the result is a ProjectStructure instance
        assert isinstance(project_structure, ProjectStructure)
        
        # Verify the root directory name
        assert project_structure.root_directory == "test_project"
        
        # Verify the directories are parsed correctly
        assert len(project_structure.directories) == 5
        assert any(d.path == "src" for d in project_structure.directories)
        assert any(d.path == "src/components" for d in project_structure.directories)
        
        # Verify the files are parsed correctly
        assert len(project_structure.files) == 5
        assert any(f.path == "README.md" for f in project_structure.files)
        assert any(f.path == "src/components/App.js" for f in project_structure.files)

    def test_parse_structure_response_invalid_json(self, project_structure_generator):
        """Test parsing an invalid JSON response."""
        with pytest.raises(json.JSONDecodeError):
            project_structure_generator._parse_structure_response("invalid json")

    def test_parse_structure_response_missing_fields(self, project_structure_generator):
        """Test parsing a response with missing required fields."""
        # Missing root_directory
        response_json = {
            "directories": ["src"],
            "files": ["README.md"]
        }
        
        with pytest.raises(KeyError):
            project_structure_generator._parse_structure_response(json.dumps(response_json))
        
        # Missing directories
        response_json = {
            "root_directory": "test_project",
            "files": ["README.md"]
        }
        
        with pytest.raises(KeyError):
            project_structure_generator._parse_structure_response(json.dumps(response_json))
        
        # Missing files
        response_json = {
            "root_directory": "test_project",
            "directories": ["src"]
        }
        
        with pytest.raises(KeyError):
            project_structure_generator._parse_structure_response(json.dumps(response_json))

    def test_create_directory_node(self, project_structure_generator):
        """Test creating a DirectoryNode from a path."""
        # Test simple directory
        node = project_structure_generator._create_directory_node("src")
        assert isinstance(node, DirectoryNode)
        assert node.path == "src"
        assert node.name == "src"
        assert node.parent_path is None
        
        # Test nested directory
        node = project_structure_generator._create_directory_node("src/components")
        assert isinstance(node, DirectoryNode)
        assert node.path == "src/components"
        assert node.name == "components"
        assert node.parent_path == "src"

    def test_create_file_node(self, project_structure_generator):
        """Test creating a FileNode from a path."""
        # Test root file
        node = project_structure_generator._create_file_node("README.md")
        assert isinstance(node, FileNode)
        assert node.path == "README.md"
        assert node.name == "README.md"
        assert node.parent_path is None
        
        # Test nested file
        node = project_structure_generator._create_file_node("src/index.js")
        assert isinstance(node, FileNode)
        assert node.path == "src/index.js"
        assert node.name == "index.js"
        assert node.parent_path == "src"

    @mock.patch('src.core.project_structure_generator.ProjectStructureGenerator._create_prompt')
    def test_generate_project_structure_prompt_customization(self, mock_create_prompt, project_structure_generator, sample_project_type, sample_architecture_plan):
        """Test that the prompt for generating project structure can be customized."""
        mock_create_prompt.return_value = "Custom prompt"
        
        project_structure_generator.generate_project_structure(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_name="test_project"
        )
        
        # Verify the custom prompt was used
        project_structure_generator.anthropic_client.generate_response.assert_called_once_with("Custom prompt")
        mock_create_prompt.assert_called_once()

    def test_create_prompt(self, project_structure_generator, sample_project_type, sample_architecture_plan):
        """Test creating a prompt for the AI model."""
        prompt = project_structure_generator._create_prompt(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_name="test_project"
        )
        
        # Verify the prompt contains key information
        assert "test_project" in prompt
        assert "React" in prompt
        assert "FastAPI" in prompt
        assert "PostgreSQL" in prompt
        assert "Frontend" in prompt
        assert "Backend API" in prompt
        assert "Database" in prompt
        assert "JSON" in prompt

    def test_handle_ai_error(self, project_structure_generator, sample_project_type, sample_architecture_plan):
        """Test handling errors from the AI client."""
        # Setup the client to raise an exception
        project_structure_generator.anthropic_client.generate_response.side_effect = Exception("API error")
        
        # Test that the error is properly caught and re-raised
        with pytest.raises(Exception) as excinfo:
            project_structure_generator.generate_project_structure(
                project_type=sample_project_type,
                architecture_plan=sample_architecture_plan,
                project_name="test_project"
            )
        
        assert "Error generating project structure" in str(excinfo.value)

    def test_generate_project_structure_with_empty_architecture(self, project_structure_generator, sample_project_type):
        """Test generating a project structure with an empty architecture plan."""
        empty_architecture = ArchitecturePlan(components=[], dependencies=[], data_flows=[])
        
        project_structure = project_structure_generator.generate_project_structure(
            project_type=sample_project_type,
            architecture_plan=empty_architecture,
            project_name="test_project"
        )
        
        # Verify the result is still a valid ProjectStructure
        assert isinstance(project_structure, ProjectStructure)
        assert project_structure.root_directory == "test_project"

    def test_generate_project_structure_with_different_project_types(self, project_structure_generator, sample_architecture_plan):
        """Test generating project structures for different project types."""
        # Test with a CLI application
        cli_project_type = ProjectType(
            type=ProjectTypeEnum.CLI_APPLICATION,
            frontend_framework=None,
            backend_framework="Python",
            database=None,
            description="A command-line tool",
            features=["File processing", "Data analysis"],
            complexity="Low"
        )
        
        project_structure = project_structure_generator.generate_project_structure(
            project_type=cli_project_type,
            architecture_plan=sample_architecture_plan,
            project_name="cli_tool"
        )
        
        assert isinstance(project_structure, ProjectStructure)
        assert project_structure.root_directory == "cli_tool"
        
        # Verify the prompt contained CLI-specific information
        call_args = project_structure_generator.anthropic_client.generate_response.call_args[0][0]
        assert "CLI_APPLICATION" in call_args or "command-line" in call_args.lower()

    def test_sort_directories_by_depth(self, project_structure_generator):
        """Test sorting directories by depth to ensure parent directories are created first."""
        directories = [
            "src/components/ui",
            "tests",
            "src",
            "src/components",
            "docs/api"
        ]
        
        sorted_dirs = project_structure_generator._sort_directories_by_depth(directories)
        
        # Verify the directories are sorted by depth (number of path segments)
        expected_order = [
            "src",
            "tests",
            "src/components",
            "docs/api",
            "src/components/ui"
        ]
        
        assert sorted_dirs == expected_order

    def test_validate_structure(self, project_structure_generator):
        """Test validating the generated project structure."""
        # Valid structure
        valid_structure = ProjectStructure(
            root_directory="test_project",
            directories=[
                DirectoryNode(path="src", name="src", parent_path=None),
                DirectoryNode(path="src/components", name="components", parent_path="src")
            ],
            files=[
                FileNode(path="README.md", name="README.md", parent_path=None),
                FileNode(path="src/index.js", name="index.js", parent_path="src")
            ]
        )
        
        # This should not raise an exception
        project_structure_generator._validate_structure(valid_structure)
        
        # Invalid structure - file in non-existent directory
        invalid_structure = ProjectStructure(
            root_directory="test_project",
            directories=[
                DirectoryNode(path="src", name="src", parent_path=None)
            ],
            files=[
                FileNode(path="README.md", name="README.md", parent_path=None),
                FileNode(path="src/components/App.js", name="App.js", parent_path="src/components")
            ]
        )
        
        with pytest.raises(ValueError) as excinfo:
            project_structure_generator._validate_structure(invalid_structure)
        
        assert "Parent directory not found" in str(excinfo.value)