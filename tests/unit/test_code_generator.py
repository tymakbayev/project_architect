#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the CodeGenerator module.

This module contains tests for the CodeGenerator class, which is responsible for
generating code files based on project architecture and structure. The tests verify
that the CodeGenerator correctly produces code files with appropriate content for
different technology stacks and project types.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.core.code_generator import CodeGenerator
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.models.project_structure import ProjectStructure, FileNode, DirectoryNode
from src.models.code_file import CodeFile
from src.clients.anthropic_client import AnthropicClient


class TestCodeGenerator:
    """Test suite for the CodeGenerator class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AnthropicClient for testing."""
        with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
            client_instance = mock_client.return_value
            
            # Configure the mock to return different responses based on input
            def mock_generate_response(prompt, **kwargs):
                if "Python" in prompt and "main.py" in prompt:
                    return """```python
def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
```"""
                elif "React" in prompt and "App.js" in prompt:
                    return """```javascript
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Hello, React!</h1>
      </header>
    </div>
  );
}

export default App;
```"""
                elif "Node" in prompt and "server.js" in prompt:
                    return """```javascript
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello, Node!');
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```"""
                else:
                    return """```
// Default mock code
console.log("Mock code generated");
```"""
            
            client_instance.generate_response.side_effect = mock_generate_response
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
                    responsibilities=["Process requests", "Interact with database"],
                    technologies=["FastAPI", "Python", "SQLAlchemy"]
                ),
                Component(
                    name="Database",
                    type="Storage",
                    description="PostgreSQL database",
                    responsibilities=["Store application data"],
                    technologies=["PostgreSQL"]
                )
            ],
            dependencies=[
                Dependency(
                    source="Frontend",
                    target="Backend API",
                    type="HTTP/REST",
                    description="Frontend calls Backend API endpoints"
                ),
                Dependency(
                    source="Backend API",
                    target="Database",
                    type="SQL",
                    description="Backend API queries the database"
                )
            ],
            data_flows=[
                DataFlow(
                    source="Frontend",
                    target="Backend API",
                    description="User requests and form submissions",
                    data_format="JSON"
                ),
                DataFlow(
                    source="Backend API",
                    target="Frontend",
                    description="API responses with data",
                    data_format="JSON"
                ),
                DataFlow(
                    source="Backend API",
                    target="Database",
                    description="Database queries and updates",
                    data_format="SQL"
                ),
                DataFlow(
                    source="Database",
                    target="Backend API",
                    description="Query results",
                    data_format="Records"
                )
            ]
        )

    @pytest.fixture
    def sample_project_structure(self):
        """Return a sample ProjectStructure instance for testing."""
        return ProjectStructure(
            root=DirectoryNode(
                name="expense_tracker",
                children=[
                    DirectoryNode(
                        name="frontend",
                        children=[
                            DirectoryNode(
                                name="src",
                                children=[
                                    FileNode(name="App.js", file_type="javascript"),
                                    FileNode(name="index.js", file_type="javascript"),
                                    DirectoryNode(
                                        name="components",
                                        children=[
                                            FileNode(name="Dashboard.js", file_type="javascript"),
                                            FileNode(name="ExpenseForm.js", file_type="javascript")
                                        ]
                                    )
                                ]
                            ),
                            FileNode(name="package.json", file_type="json")
                        ]
                    ),
                    DirectoryNode(
                        name="backend",
                        children=[
                            FileNode(name="main.py", file_type="python"),
                            DirectoryNode(
                                name="api",
                                children=[
                                    FileNode(name="routes.py", file_type="python"),
                                    FileNode(name="models.py", file_type="python")
                                ]
                            ),
                            DirectoryNode(
                                name="db",
                                children=[
                                    FileNode(name="database.py", file_type="python"),
                                    FileNode(name="schemas.py", file_type="python")
                                ]
                            )
                        ]
                    ),
                    FileNode(name="README.md", file_type="markdown"),
                    FileNode(name="docker-compose.yml", file_type="yaml")
                ]
            )
        )

    @pytest.fixture
    def code_generator(self, mock_anthropic_client):
        """Create a CodeGenerator instance with mocked client."""
        generator = CodeGenerator(api_key="test_api_key")
        generator.anthropic_client = mock_anthropic_client
        return generator

    def test_init(self):
        """Test the initialization of CodeGenerator."""
        # Test with API key
        generator = CodeGenerator(api_key="test_api_key")
        assert isinstance(generator.anthropic_client, AnthropicClient)
        assert generator.anthropic_client.api_key == "test_api_key"
        
        # Test with existing client
        mock_client = mock.MagicMock()
        generator = CodeGenerator(anthropic_client=mock_client)
        assert generator.anthropic_client == mock_client
        
        # Test with neither API key nor client
        with pytest.raises(ValueError):
            CodeGenerator()

    def test_generate_code_files(self, code_generator, sample_project_type, sample_architecture_plan, sample_project_structure):
        """Test generating code files for a project."""
        code_files = code_generator.generate_code_files(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_structure=sample_project_structure
        )
        
        # Verify the result is a list of CodeFile objects
        assert isinstance(code_files, list)
        assert all(isinstance(file, CodeFile) for file in code_files)
        
        # Verify the number of code files matches the number of FileNodes in the structure
        expected_file_count = self._count_file_nodes(sample_project_structure.root)
        assert len(code_files) == expected_file_count
        
        # Verify that each file has content
        for code_file in code_files:
            assert code_file.path is not None
            assert code_file.content is not None
            assert len(code_file.content) > 0
        
        # Verify specific files exist
        file_paths = [file.path for file in code_files]
        assert "expense_tracker/frontend/src/App.js" in file_paths
        assert "expense_tracker/backend/main.py" in file_paths
        assert "expense_tracker/README.md" in file_paths

    def test_generate_file_content(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test generating content for a specific file."""
        # Test Python file
        python_content = code_generator.generate_file_content(
            file_path="backend/main.py",
            file_type="python",
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            context="Main entry point for the FastAPI backend application."
        )
        
        assert "def main" in python_content
        assert "if __name__ == \"__main__\"" in python_content
        
        # Test React file
        react_content = code_generator.generate_file_content(
            file_path="frontend/src/App.js",
            file_type="javascript",
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            context="Main React component for the frontend application."
        )
        
        assert "import React" in react_content
        assert "function App" in react_content
        assert "export default App" in react_content
        
        # Test Node file
        node_content = code_generator.generate_file_content(
            file_path="server.js",
            file_type="javascript",
            project_type=ProjectType(
                type=ProjectTypeEnum.WEB_APPLICATION,
                frontend_framework="React",
                backend_framework="Node.js",
                database="MongoDB",
                description="A web application with React frontend and Node.js backend",
                features=["REST API"],
                complexity="Medium"
            ),
            architecture_plan=sample_architecture_plan,
            context="Express.js server for the Node.js backend."
        )
        
        assert "const express" in node_content
        assert "app.listen" in node_content

    def test_determine_file_type(self, code_generator):
        """Test determining file type from file extension."""
        assert code_generator._determine_file_type("app.py") == "python"
        assert code_generator._determine_file_type("index.js") == "javascript"
        assert code_generator._determine_file_type("styles.css") == "css"
        assert code_generator._determine_file_type("schema.json") == "json"
        assert code_generator._determine_file_type("README.md") == "markdown"
        assert code_generator._determine_file_type("Dockerfile") == "docker"
        assert code_generator._determine_file_type("unknown.xyz") == "text"

    def test_create_prompt_for_file(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test creating a prompt for generating file content."""
        prompt = code_generator._create_prompt_for_file(
            file_path="backend/api/routes.py",
            file_type="python",
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            context="API route definitions for the FastAPI backend."
        )
        
        # Verify the prompt contains key information
        assert "backend/api/routes.py" in prompt
        assert "Python" in prompt
        assert "FastAPI" in prompt
        assert "API route definitions" in prompt
        
        # Verify architecture components are included
        assert "Frontend" in prompt
        assert "Backend API" in prompt
        assert "Database" in prompt

    def test_extract_code_from_response(self, code_generator):
        """Test extracting code from Claude's response."""
        # Test with code block
        response_with_block = """Here's the code for your file:

```python
def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
```

This is a simple Python script that prints "Hello, world!" when executed."""

        code = code_generator._extract_code_from_response(response_with_block)
        assert code == 'def hello_world():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    hello_world()'
        
        # Test with multiple code blocks (should take the first one)
        response_with_multiple_blocks = """Here's the main code:

```python
def main():
    print("Main function")
```

And here's an alternative:

```python
def alternative():
    print("Alternative function")
```"""

        code = code_generator._extract_code_from_response(response_with_multiple_blocks)
        assert code == 'def main():\n    print("Main function")'
        
        # Test with no code block
        response_without_block = "Here's some text without any code blocks."
        code = code_generator._extract_code_from_response(response_without_block)
        assert code == response_without_block

    def test_handle_special_files(self, code_generator, sample_project_type):
        """Test handling special files like package.json, requirements.txt, etc."""
        # Test package.json
        package_json = code_generator._handle_special_files(
            "package.json",
            sample_project_type,
            {"name": "test-project", "dependencies": {}}
        )
        assert "dependencies" in package_json
        assert "react" in package_json.lower()
        
        # Test requirements.txt
        requirements_txt = code_generator._handle_special_files(
            "requirements.txt",
            sample_project_type,
            ""
        )
        assert "fastapi" in requirements_txt.lower()
        assert "uvicorn" in requirements_txt.lower()
        
        # Test README.md
        readme_md = code_generator._handle_special_files(
            "README.md",
            sample_project_type,
            "# Project Title"
        )
        assert "# Project Title" in readme_md
        assert "web application" in readme_md.lower()
        
        # Test non-special file (should return original content)
        original_content = "function test() { return true; }"
        result = code_generator._handle_special_files(
            "test.js",
            sample_project_type,
            original_content
        )
        assert result == original_content

    def test_generate_code_files_with_empty_structure(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test generating code files with an empty project structure."""
        empty_structure = ProjectStructure(
            root=DirectoryNode(name="empty_project", children=[])
        )
        
        code_files = code_generator.generate_code_files(
            project_type=sample_project_type,
            architecture_plan=sample_architecture_plan,
            project_structure=empty_structure
        )
        
        assert isinstance(code_files, list)
        assert len(code_files) == 0

    def test_generate_code_files_with_error(self, code_generator, sample_project_type, sample_architecture_plan, sample_project_structure):
        """Test handling errors during code file generation."""
        # Mock the generate_file_content method to raise an exception
        with mock.patch.object(code_generator, 'generate_file_content', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as excinfo:
                code_generator.generate_code_files(
                    project_type=sample_project_type,
                    architecture_plan=sample_architecture_plan,
                    project_structure=sample_project_structure
                )
            
            assert "Test error" in str(excinfo.value)

    def _count_file_nodes(self, node):
        """Helper method to count the number of FileNodes in a directory structure."""
        if isinstance(node, FileNode):
            return 1
        elif isinstance(node, DirectoryNode):
            return sum(self._count_file_nodes(child) for child in node.children)
        return 0

    def test_generate_code_with_templates(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test generating code using templates."""
        # Mock the template system
        with mock.patch('src.templates.python_templates.get_template') as mock_get_template:
            mock_template = mock.MagicMock()
            mock_template.render.return_value = "# Generated from template\ndef template_function():\n    pass"
            mock_get_template.return_value = mock_template
            
            # Test with template
            with mock.patch.object(code_generator, '_should_use_template', return_value=True):
                content = code_generator.generate_file_content(
                    file_path="backend/models.py",
                    file_type="python",
                    project_type=sample_project_type,
                    architecture_plan=sample_architecture_plan,
                    context="Database models"
                )
                
                assert "# Generated from template" in content
                assert "def template_function" in content

    def test_should_use_template(self, code_generator):
        """Test the logic for determining if a template should be used."""
        # Common files that should use templates
        assert code_generator._should_use_template("package.json", "json") is True
        assert code_generator._should_use_template("requirements.txt", "text") is True
        assert code_generator._should_use_template("Dockerfile", "docker") is True
        assert code_generator._should_use_template("docker-compose.yml", "yaml") is True
        
        # Framework-specific files that often use templates
        assert code_generator._should_use_template("app.py", "python") is True
        assert code_generator._should_use_template("index.js", "javascript") is True
        assert code_generator._should_use_template("App.js", "javascript") is True
        
        # Custom files that typically don't use templates
        assert code_generator._should_use_template("custom_logic.py", "python") is False
        assert code_generator._should_use_template("specific_component.js", "javascript") is False

    def test_process_file_node(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test processing a single file node."""
        file_node = FileNode(name="test.py", file_type="python")
        
        with mock.patch.object(code_generator, 'generate_file_content', return_value="def test(): pass"):
            code_file = code_generator._process_file_node(
                file_node=file_node,
                path_prefix="src",
                project_type=sample_project_type,
                architecture_plan=sample_architecture_plan
            )
            
            assert code_file.path == "src/test.py"
            assert code_file.content == "def test(): pass"
            assert code_file.file_type == "python"

    def test_process_directory_node(self, code_generator, sample_project_type, sample_architecture_plan):
        """Test processing a directory node with nested files."""
        dir_node = DirectoryNode(
            name="test_dir",
            children=[
                FileNode(name="file1.py", file_type="python"),
                FileNode(name="file2.js", file_type="javascript"),
                DirectoryNode(
                    name="nested_dir",
                    children=[
                        FileNode(name="nested_file.py", file_type="python")
                    ]
                )
            ]
        )
        
        with mock.patch.object(code_generator, 'generate_file_content', return_value="mock content"):
            code_files = code_generator._process_directory_node(
                dir_node=dir_node,
                path_prefix="src",
                project_type=sample_project_type,
                architecture_plan=sample_architecture_plan
            )
            
            assert len(code_files) == 3
            file_paths = [file.path for file in code_files]
            assert "src/test_dir/file1.py" in file_paths
            assert "src/test_dir/file2.js" in file_paths
            assert "src/test_dir/nested_dir/nested_file.py" in file_paths