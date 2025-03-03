#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the ProjectAnalyzer module.

This module contains tests for the ProjectAnalyzer class, which is responsible for
analyzing project descriptions and determining the project type, requirements, and
other key characteristics.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List

from src.core.project_analyzer import ProjectAnalyzer
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient


class TestProjectAnalyzer:
    """Test suite for the ProjectAnalyzer class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AnthropicClient for testing."""
        with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
            client_instance = mock_client.return_value
            client_instance.generate_response.return_value = json.dumps({
                "project_type": {
                    "type": "WEB_APPLICATION",
                    "frontend_framework": "React",
                    "backend_framework": "FastAPI",
                    "database": "PostgreSQL",
                    "description": "A web application with React frontend and FastAPI backend",
                    "features": ["User authentication", "Data visualization", "REST API"],
                    "complexity": "Medium"
                },
                "requirements": [
                    "User authentication and authorization",
                    "Data storage in PostgreSQL",
                    "RESTful API endpoints",
                    "Responsive UI with React"
                ]
            })
            yield client_instance

    @pytest.fixture
    def mock_github_client(self):
        """Create a mock GithubClient for testing."""
        with mock.patch('src.clients.github_client.GithubClient') as mock_client:
            client_instance = mock_client.return_value
            client_instance.search_repositories.return_value = [
                {
                    "name": "test-repo",
                    "description": "A test repository for web applications",
                    "url": "https://github.com/test/test-repo",
                    "stars": 100,
                    "forks": 20,
                    "language": "Python"
                }
            ]
            yield client_instance

    @pytest.fixture
    def project_analyzer(self, mock_anthropic_client, mock_github_client):
        """Create a ProjectAnalyzer instance with mocked clients."""
        analyzer = ProjectAnalyzer(api_key="test_api_key")
        analyzer.anthropic_client = mock_anthropic_client
        analyzer.github_client = mock_github_client
        return analyzer

    @pytest.fixture
    def sample_project_description(self):
        """Return a sample project description for testing."""
        return "A web application that allows users to track their daily expenses, categorize them, and generate reports."

    def test_init(self):
        """Test the initialization of ProjectAnalyzer."""
        # Test with API key
        analyzer = ProjectAnalyzer(api_key="test_api_key")
        assert isinstance(analyzer.anthropic_client, AnthropicClient)
        assert analyzer.anthropic_client.api_key == "test_api_key"
        
        # Test with existing client
        mock_client = mock.MagicMock()
        analyzer = ProjectAnalyzer(anthropic_client=mock_client)
        assert analyzer.anthropic_client == mock_client
        
        # Test with GitHub client
        github_client = mock.MagicMock()
        analyzer = ProjectAnalyzer(api_key="test_api_key", github_client=github_client)
        assert analyzer.github_client == github_client
        
        # Test with neither API key nor client
        with pytest.raises(ValueError):
            ProjectAnalyzer()

    def test_analyze_project_description(self, project_analyzer, sample_project_description):
        """Test analyzing a project description."""
        result = project_analyzer.analyze_project_description(sample_project_description)
        
        # Verify the result structure
        assert isinstance(result, dict)
        assert "project_type" in result
        assert "requirements" in result
        
        # Verify project_type is correctly parsed
        project_type = result["project_type"]
        assert isinstance(project_type, ProjectType)
        assert project_type.type == ProjectTypeEnum.WEB_APPLICATION
        assert project_type.frontend_framework == "React"
        assert project_type.backend_framework == "FastAPI"
        assert project_type.database == "PostgreSQL"
        assert len(project_type.features) == 3
        assert "User authentication" in project_type.features
        
        # Verify requirements are correctly parsed
        requirements = result["requirements"]
        assert isinstance(requirements, list)
        assert len(requirements) == 4
        assert "User authentication and authorization" in requirements

    def test_analyze_project_description_with_context(self, project_analyzer, sample_project_description):
        """Test analyzing a project description with additional context."""
        additional_context = {
            "preferred_language": "Python",
            "target_audience": "Financial professionals",
            "deployment_platform": "AWS"
        }
        
        result = project_analyzer.analyze_project_description(
            sample_project_description, 
            additional_context=additional_context
        )
        
        # Verify the anthropic client was called with the correct prompt
        prompt_call = project_analyzer.anthropic_client.generate_response.call_args[0][0]
        assert "preferred_language: Python" in prompt_call
        assert "target_audience: Financial professionals" in prompt_call
        assert "deployment_platform: AWS" in prompt_call
        
        # Verify the result structure
        assert isinstance(result, dict)
        assert "project_type" in result
        assert "requirements" in result

    def test_analyze_project_description_with_github_insights(self, project_analyzer, sample_project_description):
        """Test analyzing a project description with GitHub insights."""
        result = project_analyzer.analyze_project_description(
            sample_project_description, 
            use_github_insights=True
        )
        
        # Verify GitHub client was called
        project_analyzer.github_client.search_repositories.assert_called_once()
        
        # Verify the result structure
        assert isinstance(result, dict)
        assert "project_type" in result
        assert "requirements" in result
        assert "github_insights" in result
        
        # Verify GitHub insights
        github_insights = result["github_insights"]
        assert isinstance(github_insights, list)
        assert len(github_insights) == 1
        assert github_insights[0]["name"] == "test-repo"

    def test_extract_requirements(self, project_analyzer, sample_project_description):
        """Test extracting requirements from a project description."""
        requirements = project_analyzer.extract_requirements(sample_project_description)
        
        # Verify the anthropic client was called
        project_analyzer.anthropic_client.generate_response.assert_called_once()
        
        # Verify requirements
        assert isinstance(requirements, list)
        assert len(requirements) == 4
        assert "User authentication and authorization" in requirements

    def test_determine_project_type(self, project_analyzer, sample_project_description):
        """Test determining the project type from a description."""
        project_type = project_analyzer.determine_project_type(sample_project_description)
        
        # Verify the anthropic client was called
        project_analyzer.anthropic_client.generate_response.assert_called_once()
        
        # Verify project type
        assert isinstance(project_type, ProjectType)
        assert project_type.type == ProjectTypeEnum.WEB_APPLICATION
        assert project_type.frontend_framework == "React"
        assert project_type.backend_framework == "FastAPI"

    def test_get_github_insights(self, project_analyzer, sample_project_description):
        """Test getting insights from GitHub for a project description."""
        insights = project_analyzer.get_github_insights(sample_project_description)
        
        # Verify GitHub client was called
        project_analyzer.github_client.search_repositories.assert_called_once()
        
        # Verify insights
        assert isinstance(insights, list)
        assert len(insights) == 1
        assert insights[0]["name"] == "test-repo"
        assert insights[0]["stars"] == 100

    def test_analyze_project_description_error_handling(self, project_analyzer, sample_project_description):
        """Test error handling in analyze_project_description."""
        # Set up the mock to raise an exception
        project_analyzer.anthropic_client.generate_response.side_effect = Exception("API error")
        
        # Test that the method handles the exception gracefully
        with pytest.raises(Exception) as excinfo:
            project_analyzer.analyze_project_description(sample_project_description)
        
        assert "API error" in str(excinfo.value)

    def test_parse_anthropic_response(self, project_analyzer):
        """Test parsing the response from Anthropic API."""
        # Valid JSON response
        valid_response = json.dumps({
            "project_type": {
                "type": "WEB_APPLICATION",
                "frontend_framework": "React",
                "backend_framework": "FastAPI",
                "database": "PostgreSQL",
                "description": "A web application with React frontend and FastAPI backend",
                "features": ["User authentication", "Data visualization", "REST API"],
                "complexity": "Medium"
            },
            "requirements": [
                "User authentication and authorization",
                "Data storage in PostgreSQL",
                "RESTful API endpoints",
                "Responsive UI with React"
            ]
        })
        
        result = project_analyzer._parse_anthropic_response(valid_response)
        assert isinstance(result, dict)
        assert "project_type" in result
        assert "requirements" in result
        
        # Invalid JSON response
        invalid_response = "This is not a valid JSON"
        with pytest.raises(json.JSONDecodeError):
            project_analyzer._parse_anthropic_response(invalid_response)
        
        # Valid JSON but missing required fields
        incomplete_response = json.dumps({
            "requirements": ["Requirement 1", "Requirement 2"]
        })
        
        with pytest.raises(KeyError):
            project_analyzer._parse_anthropic_response(incomplete_response)

    def test_create_prompt_for_project_analysis(self, project_analyzer, sample_project_description):
        """Test creating a prompt for project analysis."""
        prompt = project_analyzer._create_prompt_for_project_analysis(
            sample_project_description,
            additional_context={"preferred_language": "Python"}
        )
        
        # Verify prompt content
        assert sample_project_description in prompt
        assert "preferred_language: Python" in prompt
        assert "JSON format" in prompt
        assert "project_type" in prompt
        assert "requirements" in prompt

    @mock.patch('os.environ.get')
    def test_init_with_env_api_key(self, mock_env_get):
        """Test initialization with API key from environment variable."""
        mock_env_get.return_value = "env_api_key"
        
        # Initialize without explicit API key
        analyzer = ProjectAnalyzer()
        
        # Verify the API key was taken from environment
        assert analyzer.anthropic_client.api_key == "env_api_key"
        mock_env_get.assert_called_with("ANTHROPIC_API_KEY", None)

    def test_analyze_with_custom_prompt_template(self, project_analyzer, sample_project_description):
        """Test analyzing with a custom prompt template."""
        custom_template = "Custom template: {project_description}"
        
        result = project_analyzer.analyze_project_description(
            sample_project_description,
            prompt_template=custom_template
        )
        
        # Verify the custom template was used
        expected_prompt = f"Custom template: {sample_project_description}"
        project_analyzer.anthropic_client.generate_response.assert_called_with(expected_prompt)
        
        # Verify the result
        assert isinstance(result, dict)
        assert "project_type" in result
        assert "requirements" in result


if __name__ == "__main__":
    pytest.main(["-v", __file__])