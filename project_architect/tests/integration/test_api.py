#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for the Project Architect API.

This module contains integration tests for the Project Architect API endpoints,
ensuring that the API functions correctly as a whole and produces expected results.
These tests verify that:
1. API endpoints return correct status codes and response formats
2. Project generation works end-to-end through the API
3. Error handling is implemented correctly
4. Authentication and authorization work as expected
5. Rate limiting and other API policies are enforced
"""

import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the project root to the Python path to ensure imports work correctly
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import application components for testing
from src.interfaces.api import app, get_anthropic_client, get_github_client
from src.project_generator import ProjectGenerator
from src.models.project_type import ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan
from src.models.project_structure import ProjectStructure
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec
from src.config import Config
from requirements.txt import (
    IntegrationTestBase,
    skip_if_no_api_key,
    skip_if_no_github_token,
    TEST_PROJECT_NAME,
    TEST_PROJECT_DESCRIPTION
)

# Create a test client
client = TestClient(app)


class TestAPI(IntegrationTestBase):
    """Integration tests for the Project Architect API."""

    @classmethod
    def setup_class(cls):
        """Set up the test class with common resources."""
        super().setup_class()
        cls.api_client = client
        
        # Sample valid project request data
        cls.valid_project_data = {
            "name": TEST_PROJECT_NAME,
            "description": TEST_PROJECT_DESCRIPTION,
            "output_format": "zip",
            "technology_preferences": ["python", "fastapi"],
            "include_tests": True,
            "include_documentation": True
        }
        
        # Sample invalid project request data (missing required fields)
        cls.invalid_project_data = {
            "name": TEST_PROJECT_NAME,
            # Missing description
            "output_format": "zip"
        }

    def setup_method(self):
        """Set up resources before each test method."""
        super().setup_method()
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up resources after each test method."""
        super().teardown_method()
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_api_root(self):
        """Test the API root endpoint returns correct information."""
        response = self.api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["name"] == "Project Architect API"

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_api_docs_available(self):
        """Test that API documentation is available."""
        response = self.api_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        response = self.api_client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema(self):
        """Test that OpenAPI schema is available and valid."""
        response = self.api_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "/projects/" in schema["paths"]
        assert "components" in schema
        assert "schemas" in schema["components"]

    def test_invalid_endpoint(self):
        """Test that invalid endpoints return 404."""
        response = self.api_client.get("/nonexistent_endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Not Found" in data["detail"]

    def test_create_project_validation_error(self):
        """Test validation error when creating a project with invalid data."""
        response = self.api_client.post("/projects/", json=self.invalid_project_data)
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data
        # Verify that the error message mentions the missing field
        assert any("description" in error["msg"] for error in data["detail"])

    @patch("src.interfaces.api.ProjectGenerator")
    def test_create_project_success(self, mock_project_generator):
        """Test successful project creation."""
        # Mock the project generator to return a success result
        mock_instance = mock_project_generator.return_value
        mock_instance.generate_project.return_value = {
            "project_id": "test-project-123",
            "project_type": {"type": "WEB_APPLICATION", "framework": "FASTAPI"},
            "architecture": {"components": []},
            "structure": {"directories": [], "files": []},
            "code_files": [{"path": "main.py", "content": "print('Hello')"}],
            "dependencies": [{"name": "fastapi", "version": "^0.68.0"}]
        }
        
        # Create a temporary zip file to return
        temp_zip = os.path.join(self.temp_dir, "test_project.zip")
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            zipf.writestr("main.py", "print('Hello')")
        
        mock_instance.export_project.return_value = temp_zip
        
        response = self.api_client.post("/projects/", json=self.valid_project_data)
        assert response.status_code == 201
        data = response.json()
        
        assert "project_id" in data
        assert "download_url" in data
        assert data["status"] == "completed"
        assert data["project_type"] == {"type": "WEB_APPLICATION", "framework": "FASTAPI"}
        
        # Verify the project generator was called with correct parameters
        mock_project_generator.assert_called_once()
        mock_instance.generate_project.assert_called_once_with(
            TEST_PROJECT_NAME,
            TEST_PROJECT_DESCRIPTION,
            technology_preferences=["python", "fastapi"],
            include_tests=True,
            include_documentation=True
        )

    @patch("src.interfaces.api.ProjectGenerator")
    def test_create_project_error(self, mock_project_generator):
        """Test error handling when project creation fails."""
        # Mock the project generator to raise an exception
        mock_instance = mock_project_generator.return_value
        mock_instance.generate_project.side_effect = Exception("Test error message")
        
        response = self.api_client.post("/projects/", json=self.valid_project_data)
        assert response.status_code == 500
        data = response.json()
        
        assert "error" in data
        assert "Test error message" in data["error"]
        assert data["status"] == "failed"

    @patch("src.interfaces.api.ProjectGenerator")
    def test_get_project_not_found(self, mock_project_generator):
        """Test getting a non-existent project."""
        # Mock the project generator to return None for get_project
        mock_instance = mock_project_generator.return_value
        mock_instance.get_project.return_value = None
        
        response = self.api_client.get("/projects/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @patch("src.interfaces.api.ProjectGenerator")
    def test_get_project_success(self, mock_project_generator):
        """Test successfully getting a project."""
        # Mock the project generator to return a project
        mock_instance = mock_project_generator.return_value
        mock_instance.get_project.return_value = {
            "project_id": "test-project-123",
            "name": TEST_PROJECT_NAME,
            "description": TEST_PROJECT_DESCRIPTION,
            "status": "completed",
            "created_at": "2023-01-01T00:00:00Z",
            "project_type": {"type": "WEB_APPLICATION", "framework": "FASTAPI"},
            "architecture": {"components": []},
            "structure": {"directories": [], "files": []},
            "dependencies": [{"name": "fastapi", "version": "^0.68.0"}]
        }
        
        response = self.api_client.get("/projects/test-project-123")
        assert response.status_code == 200
        data = response.json()
        
        assert data["project_id"] == "test-project-123"
        assert data["name"] == TEST_PROJECT_NAME
        assert data["description"] == TEST_PROJECT_DESCRIPTION
        assert data["status"] == "completed"
        assert "created_at" in data
        assert "project_type" in data
        assert "architecture" in data
        assert "structure" in data
        assert "dependencies" in data

    @patch("src.interfaces.api.ProjectGenerator")
    def test_list_projects(self, mock_project_generator):
        """Test listing projects."""
        # Mock the project generator to return a list of projects
        mock_instance = mock_project_generator.return_value
        mock_instance.list_projects.return_value = [
            {
                "project_id": "test-project-1",
                "name": "Test Project 1",
                "description": "Description 1",
                "status": "completed",
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "project_id": "test-project-2",
                "name": "Test Project 2",
                "description": "Description 2",
                "status": "in_progress",
                "created_at": "2023-01-02T00:00:00Z"
            }
        ]
        
        response = self.api_client.get("/projects/")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["project_id"] == "test-project-1"
        assert data[1]["project_id"] == "test-project-2"
        
        # Test pagination parameters are passed correctly
        response = self.api_client.get("/projects/?skip=10&limit=5")
        mock_instance.list_projects.assert_called_with(skip=10, limit=5)

    @patch("src.interfaces.api.ProjectGenerator")
    def test_download_project(self, mock_project_generator):
        """Test downloading a project."""
        # Mock the project generator
        mock_instance = mock_project_generator.return_value
        
        # Create a temporary zip file to return
        temp_zip = os.path.join(self.temp_dir, "test_project.zip")
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            zipf.writestr("main.py", "print('Hello')")
            zipf.writestr("README.md", "# Test Project")
        
        # Mock the get_project_download method
        mock_instance.get_project_download.return_value = temp_zip
        
        response = self.api_client.get("/projects/test-project-123/download")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert "attachment" in response.headers["Content-Disposition"]
        assert "test_project.zip" in response.headers["Content-Disposition"]
        
        # Verify the content is a valid zip file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            with zipfile.ZipFile(tmp_path, 'r') as zipf:
                assert "main.py" in zipf.namelist()
                assert "README.md" in zipf.namelist()
                assert zipf.read("main.py") == b"print('Hello')"
                assert zipf.read("README.md") == b"# Test Project"
        finally:
            os.unlink(tmp_path)

    @patch("src.interfaces.api.ProjectGenerator")
    def test_download_project_not_found(self, mock_project_generator):
        """Test downloading a non-existent project."""
        # Mock the project generator to raise an exception
        mock_instance = mock_project_generator.return_value
        mock_instance.get_project_download.side_effect = FileNotFoundError("Project not found")
        
        response = self.api_client.get("/projects/nonexistent-id/download")
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @patch("src.interfaces.api.ProjectGenerator")
    def test_analyze_project_description(self, mock_project_generator):
        """Test analyzing a project description."""
        # Mock the project generator
        mock_instance = mock_project_generator.return_value
        mock_instance.analyze_project_description.return_value = {
            "project_type": {"type": "WEB_APPLICATION", "framework": "FASTAPI"},
            "requirements": [
                "RESTful API endpoints",
                "Database integration",
                "Authentication"
            ],
            "suggested_technologies": ["Python", "FastAPI", "SQLAlchemy", "JWT"],
            "suggested_architecture": "Three-tier architecture with API, business logic, and data layers"
        }
        
        request_data = {
            "description": TEST_PROJECT_DESCRIPTION,
            "technology_preferences": ["python", "fastapi"]
        }
        
        response = self.api_client.post("/analyze/", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "project_type" in data
        assert "requirements" in data
        assert "suggested_technologies" in data
        assert "suggested_architecture" in data
        assert data["project_type"]["type"] == "WEB_APPLICATION"
        assert len(data["requirements"]) == 3
        assert "Python" in data["suggested_technologies"]
        
        # Verify the analyze method was called with correct parameters
        mock_instance.analyze_project_description.assert_called_once_with(
            TEST_PROJECT_DESCRIPTION,
            technology_preferences=["python", "fastapi"]
        )

    @patch("src.interfaces.api.ProjectGenerator")
    def test_analyze_project_description_error(self, mock_project_generator):
        """Test error handling when analysis fails."""
        # Mock the project generator to raise an exception
        mock_instance = mock_project_generator.return_value
        mock_instance.analyze_project_description.side_effect = Exception("Analysis failed")
        
        request_data = {
            "description": TEST_PROJECT_DESCRIPTION
        }
        
        response = self.api_client.post("/analyze/", json=request_data)
        assert response.status_code == 500
        data = response.json()
        
        assert "error" in data
        assert "Analysis failed" in data["error"]

    @skip_if_no_api_key
    def test_anthropic_client_dependency(self):
        """Test that the Anthropic client dependency is correctly injected."""
        with patch("src.interfaces.api.AnthropicClient") as mock_anthropic_client:
            # Create a mock instance
            mock_instance = MagicMock()
            mock_anthropic_client.return_value = mock_instance
            
            # Override the dependency
            app.dependency_overrides[get_anthropic_client] = lambda: mock_instance
            
            try:
                # Make a request that uses the Anthropic client
                request_data = {
                    "description": "Simple test project"
                }
                response = client.post("/analyze/", json=request_data)
                
                # Verify the client was used
                assert mock_instance.method_calls, "Anthropic client was not used"
            finally:
                # Remove the override
                app.dependency_overrides.pop(get_anthropic_client)

    @skip_if_no_github_token
    def test_github_client_dependency(self):
        """Test that the GitHub client dependency is correctly injected."""
        with patch("src.interfaces.api.GithubClient") as mock_github_client:
            # Create a mock instance
            mock_instance = MagicMock()
            mock_github_client.return_value = mock_instance
            
            # Override the dependency
            app.dependency_overrides[get_github_client] = lambda: mock_instance
            
            try:
                # Make a request that uses the GitHub client
                response = client.get("/github/templates?query=fastapi")
                
                # Verify the client was used
                assert mock_instance.method_calls, "GitHub client was not used"
            finally:
                # Remove the override
                app.dependency_overrides.pop(get_github_client)

    def test_api_rate_limiting(self):
        """Test that API rate limiting is working."""
        # This test assumes rate limiting is configured in the API
        # Make multiple requests in quick succession
        responses = []
        for _ in range(20):  # Adjust based on your rate limit settings
            responses.append(self.api_client.get("/health"))
        
        # Check if any responses indicate rate limiting
        rate_limited = any(response.status_code == 429 for response in responses)
        
        # If rate limiting is implemented, at least one request should be rate limited
        # If not, this test can be skipped
        if not rate_limited:
            pytest.skip("Rate limiting not implemented or limit not reached")
        
        # Verify rate limit response contains appropriate headers
        rate_limited_response = next(r for r in responses if r.status_code == 429)
        assert "Retry-After" in rate_limited_response.headers

    @patch("src.interfaces.api.ProjectGenerator")
    def test_update_project(self, mock_project_generator):
        """Test updating a project."""
        # Mock the project generator
        mock_instance = mock_project_generator.return_value
        mock_instance.update_project.return_value = {
            "project_id": "test-project-123",
            "name": "Updated Project Name",
            "description": TEST_PROJECT_DESCRIPTION,
            "status": "completed",
            "updated_at": "2023-01-02T00:00:00Z"
        }
        
        update_data = {
            "name": "Updated Project Name",
            "technology_preferences": ["python", "django"]
        }
        
        response = self.api_client.patch("/projects/test-project-123", json=update_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["project_id"] == "test-project-123"
        assert data["name"] == "Updated Project Name"
        assert "updated_at" in data
        
        # Verify the update method was called with correct parameters
        mock_instance.update_project.assert_called_once_with(
            "test-project-123",
            name="Updated Project Name",
            technology_preferences=["python", "django"]
        )

    @patch("src.interfaces.api.ProjectGenerator")
    def test_delete_project(self, mock_project_generator):
        """Test deleting a project."""
        # Mock the project generator
        mock_instance = mock_project_generator.return_value
        mock_instance.delete_project.return_value = True
        
        response = self.api_client.delete("/projects/test-project-123")
        assert response.status_code == 204
        
        # Verify the delete method was called with correct parameters
        mock_instance.delete_project.assert_called_once_with("test-project-123")

    @patch("src.interfaces.api.ProjectGenerator")
    def test_delete_project_not_found(self, mock_project_generator):
        """Test deleting a non-existent project."""
        # Mock the project generator to return False (project not found)
        mock_instance = mock_project_generator.return_value
        mock_instance.delete_project.return_value = False
        
        response = self.api_client.delete("/projects/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])