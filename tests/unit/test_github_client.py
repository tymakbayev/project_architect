#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the GithubClient module.

This module contains tests for the GithubClient class, which is responsible for
interacting with the GitHub API to search repositories, fetch code examples,
and analyze project structures.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.clients.github_client import GithubClient
from src.clients.base_client import BaseClient, ClientError


class TestGithubClient:
    """Test suite for the GithubClient class."""

    @pytest.fixture
    def mock_requests(self):
        """Create a mock for the requests module."""
        with mock.patch('src.clients.github_client.requests') as mock_requests:
            # Setup default mock response
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "items": [
                    {
                        "name": "test-repo",
                        "full_name": "test-user/test-repo",
                        "html_url": "https://github.com/test-user/test-repo",
                        "description": "A test repository",
                        "stargazers_count": 100,
                        "forks_count": 20,
                        "language": "Python",
                        "owner": {
                            "login": "test-user",
                            "avatar_url": "https://github.com/test-user.png"
                        }
                    }
                ],
                "total_count": 1
            }
            mock_requests.get.return_value = mock_response
            yield mock_requests

    @pytest.fixture
    def mock_pygithub(self):
        """Create a mock for the PyGithub module."""
        with mock.patch('src.clients.github_client.Github') as mock_github:
            mock_github_instance = mock_github.return_value
            
            # Mock repository
            mock_repo = mock.MagicMock()
            mock_repo.name = "test-repo"
            mock_repo.full_name = "test-user/test-repo"
            mock_repo.html_url = "https://github.com/test-user/test-repo"
            mock_repo.description = "A test repository"
            mock_repo.stargazers_count = 100
            mock_repo.forks_count = 20
            mock_repo.language = "Python"
            
            # Mock content file
            mock_content = mock.MagicMock()
            mock_content.decoded_content = b"def test_function():\n    return 'Hello, World!'"
            mock_content.path = "test_file.py"
            mock_content.type = "file"
            
            # Mock directory content
            mock_dir_content = mock.MagicMock()
            mock_dir_content.path = "test_dir"
            mock_dir_content.type = "dir"
            
            # Setup repo.get_contents to return different content based on path
            def get_contents_side_effect(path, ref=None):
                if path == "test_dir":
                    return [mock_content, mock_dir_content]
                elif path == "test_file.py":
                    return mock_content
                else:
                    return []
            
            mock_repo.get_contents.side_effect = get_contents_side_effect
            
            # Setup get_repo to return our mock repo
            mock_github_instance.get_repo.return_value = mock_repo
            
            # Setup search_repositories to return a list with our mock repo
            mock_paginated_list = mock.MagicMock()
            mock_paginated_list.__iter__.return_value = [mock_repo]
            mock_paginated_list.totalCount = 1
            mock_github_instance.search_repositories.return_value = mock_paginated_list
            
            yield mock_github_instance

    @pytest.fixture
    def github_client(self):
        """Create a GithubClient instance for testing."""
        return GithubClient(api_key="test_api_key")

    def test_init(self):
        """Test the initialization of GithubClient."""
        # Test with API key
        client = GithubClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        assert isinstance(client, BaseClient)
        
        # Test with API key from environment
        with mock.patch.dict(os.environ, {"GITHUB_API_KEY": "env_api_key"}):
            client = GithubClient()
            assert client.api_key == "env_api_key"
        
        # Test with no API key
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                GithubClient()

    def test_search_repositories(self, github_client, mock_pygithub):
        """Test searching for repositories."""
        # Test basic search
        repos = github_client.search_repositories("test project")
        
        # Verify PyGithub was called correctly
        mock_pygithub.search_repositories.assert_called_once_with(
            "test project", sort="stars", order="desc"
        )
        
        # Verify the returned data
        assert len(repos) == 1
        assert repos[0]["name"] == "test-repo"
        assert repos[0]["full_name"] == "test-user/test-repo"
        assert repos[0]["url"] == "https://github.com/test-user/test-repo"
        assert repos[0]["description"] == "A test repository"
        assert repos[0]["stars"] == 100
        assert repos[0]["forks"] == 20
        assert repos[0]["language"] == "Python"
        
        # Test with limit
        github_client.search_repositories("test project", limit=5)
        # The mock will still return only one repo, but we should check the limit is passed
        
        # Test with language filter
        github_client.search_repositories("test project", language="Python")
        mock_pygithub.search_repositories.assert_called_with(
            "test project language:Python", sort="stars", order="desc"
        )
        
        # Test with topic filter
        github_client.search_repositories("test project", topics=["web", "api"])
        mock_pygithub.search_repositories.assert_called_with(
            "test project topic:web topic:api", sort="stars", order="desc"
        )
        
        # Test with multiple filters
        github_client.search_repositories(
            "test project", language="Python", topics=["web", "api"]
        )
        mock_pygithub.search_repositories.assert_called_with(
            "test project language:Python topic:web topic:api", sort="stars", order="desc"
        )

    def test_search_repositories_error(self, github_client, mock_pygithub):
        """Test error handling when searching repositories."""
        # Setup mock to raise an exception
        mock_pygithub.search_repositories.side_effect = Exception("API error")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.search_repositories("test project")
        
        assert "Failed to search GitHub repositories" in str(excinfo.value)

    def test_get_repository(self, github_client, mock_pygithub):
        """Test getting a specific repository."""
        repo = github_client.get_repository("test-user/test-repo")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        
        # Verify the returned data
        assert repo["name"] == "test-repo"
        assert repo["full_name"] == "test-user/test-repo"
        assert repo["url"] == "https://github.com/test-user/test-repo"
        assert repo["description"] == "A test repository"
        assert repo["stars"] == 100
        assert repo["forks"] == 20
        assert repo["language"] == "Python"

    def test_get_repository_error(self, github_client, mock_pygithub):
        """Test error handling when getting a repository."""
        # Setup mock to raise an exception
        mock_pygithub.get_repo.side_effect = Exception("Repository not found")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.get_repository("test-user/test-repo")
        
        assert "Failed to get GitHub repository" in str(excinfo.value)

    def test_get_file_content(self, github_client, mock_pygithub):
        """Test getting file content from a repository."""
        content = github_client.get_file_content("test-user/test-repo", "test_file.py")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_contents.assert_called_with("test_file.py", ref=None)
        
        # Verify the returned content
        assert content == "def test_function():\n    return 'Hello, World!'"
        
        # Test with specific branch/ref
        github_client.get_file_content("test-user/test-repo", "test_file.py", ref="main")
        mock_repo.get_contents.assert_called_with("test_file.py", ref="main")

    def test_get_file_content_error(self, github_client, mock_pygithub):
        """Test error handling when getting file content."""
        # Setup mock to raise an exception
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_contents.side_effect = Exception("File not found")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.get_file_content("test-user/test-repo", "nonexistent_file.py")
        
        assert "Failed to get file content from GitHub" in str(excinfo.value)

    def test_get_directory_structure(self, github_client, mock_pygithub):
        """Test getting directory structure from a repository."""
        structure = github_client.get_directory_structure("test-user/test-repo", "test_dir")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_contents.assert_called_with("test_dir", ref=None)
        
        # Verify the returned structure
        assert len(structure) == 2
        assert structure[0]["path"] == "test_file.py"
        assert structure[0]["type"] == "file"
        assert structure[1]["path"] == "test_dir"
        assert structure[1]["type"] == "dir"
        
        # Test with specific branch/ref
        github_client.get_directory_structure("test-user/test-repo", "test_dir", ref="main")
        mock_repo.get_contents.assert_called_with("test_dir", ref="main")

    def test_get_directory_structure_error(self, github_client, mock_pygithub):
        """Test error handling when getting directory structure."""
        # Setup mock to raise an exception
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_contents.side_effect = Exception("Directory not found")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.get_directory_structure("test-user/test-repo", "nonexistent_dir")
        
        assert "Failed to get directory structure from GitHub" in str(excinfo.value)

    def test_get_repository_structure(self, github_client, mock_pygithub):
        """Test getting the entire repository structure."""
        # Setup mock to return a more complex structure
        mock_repo = mock_pygithub.get_repo.return_value
        
        # Create mock contents for root directory
        mock_file1 = mock.MagicMock()
        mock_file1.path = "README.md"
        mock_file1.type = "file"
        
        mock_dir1 = mock.MagicMock()
        mock_dir1.path = "src"
        mock_dir1.type = "dir"
        
        # Create mock contents for src directory
        mock_file2 = mock.MagicMock()
        mock_file2.path = "src/main.py"
        mock_file2.type = "file"
        
        # Setup get_contents to return different content based on path
        def get_contents_side_effect(path, ref=None):
            if path == "":  # Root directory
                return [mock_file1, mock_dir1]
            elif path == "src":
                return [mock_file2]
            else:
                return []
        
        mock_repo.get_contents.side_effect = get_contents_side_effect
        
        # Call the method
        structure = github_client.get_repository_structure("test-user/test-repo")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_contents.assert_any_call("", ref=None)
        
        # Verify the returned structure
        assert len(structure) == 2
        assert structure[0]["path"] == "README.md"
        assert structure[0]["type"] == "file"
        assert structure[1]["path"] == "src"
        assert structure[1]["type"] == "dir"
        assert len(structure[1]["contents"]) == 1
        assert structure[1]["contents"][0]["path"] == "src/main.py"
        assert structure[1]["contents"][0]["type"] == "file"
        
        # Test with specific branch/ref
        github_client.get_repository_structure("test-user/test-repo", ref="main")
        mock_repo.get_contents.assert_any_call("", ref="main")

    def test_get_repository_structure_error(self, github_client, mock_pygithub):
        """Test error handling when getting repository structure."""
        # Setup mock to raise an exception
        mock_pygithub.get_repo.side_effect = Exception("Repository not found")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.get_repository_structure("test-user/test-repo")
        
        assert "Failed to get repository structure from GitHub" in str(excinfo.value)

    def test_search_code(self, github_client, mock_requests):
        """Test searching for code in GitHub."""
        # Setup mock response for code search
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 2,
            "items": [
                {
                    "name": "example.py",
                    "path": "src/example.py",
                    "repository": {
                        "full_name": "test-user/test-repo",
                        "html_url": "https://github.com/test-user/test-repo"
                    },
                    "html_url": "https://github.com/test-user/test-repo/blob/main/src/example.py"
                },
                {
                    "name": "test.py",
                    "path": "tests/test.py",
                    "repository": {
                        "full_name": "test-user/test-repo",
                        "html_url": "https://github.com/test-user/test-repo"
                    },
                    "html_url": "https://github.com/test-user/test-repo/blob/main/tests/test.py"
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        # Call the method
        results = github_client.search_code("fastapi app", language="Python")
        
        # Verify requests was called correctly
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args[0][0]
        assert "q=fastapi+app+language:Python" in call_args
        assert "Accept: application/vnd.github.v3+json" in mock_requests.get.call_args[1]["headers"].values()
        
        # Verify the returned results
        assert len(results) == 2
        assert results[0]["name"] == "example.py"
        assert results[0]["path"] == "src/example.py"
        assert results[0]["repository"] == "test-user/test-repo"
        assert results[0]["url"] == "https://github.com/test-user/test-repo/blob/main/src/example.py"

    def test_search_code_error(self, github_client, mock_requests):
        """Test error handling when searching code."""
        # Setup mock to raise an exception
        mock_requests.get.side_effect = Exception("API error")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.search_code("fastapi app")
        
        assert "Failed to search code on GitHub" in str(excinfo.value)

    def test_get_rate_limit(self, github_client, mock_pygithub):
        """Test getting GitHub API rate limit information."""
        # Setup mock rate limit
        mock_rate = mock.MagicMock()
        mock_rate.remaining = 4500
        mock_rate.limit = 5000
        mock_rate.reset = 1609459200  # Unix timestamp
        
        mock_rate_limit = mock.MagicMock()
        mock_rate_limit.core = mock_rate
        mock_rate_limit.search = mock_rate
        
        mock_pygithub.get_rate_limit.return_value = mock_rate_limit
        
        # Call the method
        rate_limit = github_client.get_rate_limit()
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_rate_limit.assert_called_once()
        
        # Verify the returned rate limit info
        assert rate_limit["core"]["remaining"] == 4500
        assert rate_limit["core"]["limit"] == 5000
        assert "reset_time" in rate_limit["core"]
        assert rate_limit["search"]["remaining"] == 4500
        assert rate_limit["search"]["limit"] == 5000
        assert "reset_time" in rate_limit["search"]

    def test_get_rate_limit_error(self, github_client, mock_pygithub):
        """Test error handling when getting rate limit."""
        # Setup mock to raise an exception
        mock_pygithub.get_rate_limit.side_effect = Exception("API error")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.get_rate_limit()
        
        assert "Failed to get GitHub API rate limit" in str(excinfo.value)

    def test_analyze_repository_technologies(self, github_client, mock_pygithub):
        """Test analyzing repository technologies."""
        # Setup mock languages
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_languages.return_value = {
            "Python": 10000,
            "JavaScript": 5000,
            "HTML": 2000,
            "CSS": 1000
        }
        
        # Call the method
        technologies = github_client.analyze_repository_technologies("test-user/test-repo")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_languages.assert_called_once()
        
        # Verify the returned technologies
        assert technologies["languages"] == {
            "Python": 10000,
            "JavaScript": 5000,
            "HTML": 2000,
            "CSS": 1000
        }
        assert technologies["primary_language"] == "Python"
        assert technologies["language_breakdown"] == {
            "Python": 55.56,
            "JavaScript": 27.78,
            "HTML": 11.11,
            "CSS": 5.56
        }

    def test_analyze_repository_technologies_error(self, github_client, mock_pygithub):
        """Test error handling when analyzing repository technologies."""
        # Setup mock to raise an exception
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_languages.side_effect = Exception("API error")
        
        # Test that ClientError is raised with appropriate message
        with pytest.raises(ClientError) as excinfo:
            github_client.analyze_repository_technologies("test-user/test-repo")
        
        assert "Failed to analyze repository technologies" in str(excinfo.value)

    def test_find_similar_projects(self, github_client, mock_pygithub):
        """Test finding similar projects based on description."""
        # This method uses search_repositories internally, which we've already tested
        # So we'll just verify it calls search_repositories with the right parameters
        
        with mock.patch.object(github_client, 'search_repositories') as mock_search:
            mock_search.return_value = [
                {
                    "name": "test-repo",
                    "full_name": "test-user/test-repo",
                    "url": "https://github.com/test-user/test-repo",
                    "description": "A test repository",
                    "stars": 100,
                    "forks": 20,
                    "language": "Python"
                }
            ]
            
            # Call the method
            similar_projects = github_client.find_similar_projects(
                "A web application with user authentication",
                language="Python",
                limit=5
            )
            
            # Verify search_repositories was called correctly
            mock_search.assert_called_once_with(
                "A web application with user authentication",
                language="Python",
                limit=5
            )
            
            # Verify the returned projects
            assert len(similar_projects) == 1
            assert similar_projects[0]["name"] == "test-repo"

    def test_get_project_dependencies(self, github_client, mock_pygithub):
        """Test extracting project dependencies from a repository."""
        # Setup mock file content for requirements.txt
        mock_content = mock.MagicMock()
        mock_content.decoded_content = b"fastapi==0.68.0\npydantic>=1.8.0\nuvicorn[standard]>=0.12.0\n"
        
        mock_repo = mock_pygithub.get_repo.return_value
        
        # Setup get_contents to return our mock content for requirements.txt
        def get_contents_side_effect(path, ref=None):
            if path == "requirements.txt":
                return mock_content
            elif path == "package.json":
                raise Exception("File not found")
            else:
                raise Exception("File not found")
        
        mock_repo.get_contents.side_effect = get_contents_side_effect
        
        # Call the method
        dependencies = github_client.get_project_dependencies("test-user/test-repo")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_contents.assert_any_call("requirements.txt", ref=None)
        
        # Verify the returned dependencies
        assert "python" in dependencies
        assert len(dependencies["python"]) == 3
        assert dependencies["python"][0]["name"] == "fastapi"
        assert dependencies["python"][0]["version"] == "==0.68.0"
        assert dependencies["python"][1]["name"] == "pydantic"
        assert dependencies["python"][1]["version"] == ">=1.8.0"
        assert dependencies["python"][2]["name"] == "uvicorn[standard]"
        assert dependencies["python"][2]["version"] == ">=0.12.0"

    def test_get_project_dependencies_package_json(self, github_client, mock_pygithub):
        """Test extracting project dependencies from package.json."""
        # Setup mock file content for package.json
        package_json_content = {
            "dependencies": {
                "react": "^17.0.2",
                "react-dom": "^17.0.2",
                "axios": "^0.21.1"
            },
            "devDependencies": {
                "jest": "^27.0.6",
                "eslint": "^7.32.0"
            }
        }
        
        mock_content = mock.MagicMock()
        mock_content.decoded_content = json.dumps(package_json_content).encode()
        
        mock_repo = mock_pygithub.get_repo.return_value
        
        # Setup get_contents to return our mock content for package.json
        def get_contents_side_effect(path, ref=None):
            if path == "requirements.txt":
                raise Exception("File not found")
            elif path == "package.json":
                return mock_content
            else:
                raise Exception("File not found")
        
        mock_repo.get_contents.side_effect = get_contents_side_effect
        
        # Call the method
        dependencies = github_client.get_project_dependencies("test-user/test-repo")
        
        # Verify PyGithub was called correctly
        mock_pygithub.get_repo.assert_called_once_with("test-user/test-repo")
        mock_repo.get_contents.assert_any_call("package.json", ref=None)
        
        # Verify the returned dependencies
        assert "javascript" in dependencies
        assert "dependencies" in dependencies["javascript"]
        assert "devDependencies" in dependencies["javascript"]
        assert len(dependencies["javascript"]["dependencies"]) == 3
        assert dependencies["javascript"]["dependencies"][0]["name"] == "react"
        assert dependencies["javascript"]["dependencies"][0]["version"] == "^17.0.2"
        assert len(dependencies["javascript"]["devDependencies"]) == 2
        assert dependencies["javascript"]["devDependencies"][0]["name"] == "jest"
        assert dependencies["javascript"]["devDependencies"][0]["version"] == "^27.0.6"

    def test_get_project_dependencies_error(self, github_client, mock_pygithub):
        """Test error handling when getting project dependencies."""
        # Setup mock to raise an exception for all dependency files
        mock_repo = mock_pygithub.get_repo.return_value
        mock_repo.get_contents.side_effect = Exception("File not found")
        
        # Call the method - it should return an empty dict, not raise an error
        dependencies = github_client.get_project_dependencies("test-user/test-repo")
        
        # Verify the returned dependencies are empty
        assert dependencies == {}

    def test_get_project_structure_stats(self, github_client):
        """Test calculating statistics from a project structure."""
        # Create a mock project structure
        structure = [
            {"path": "README.md", "type": "file"},
            {"path": "requirements.txt", "type": "file"},
            {
                "path": "src", 
                "type": "dir",
                "contents": [
                    {"path": "src/main.py", "type": "file"},
                    {"path": "src/utils.py", "type": "file"},
                    {
                        "path": "src/models", 
                        "type": "dir",
                        "contents": [
                            {"path": "src/models/user.py", "type": "file"},
                            {"path": "src/models/item.py", "type": "file"}
                        ]
                    }
                ]
            },
            {
                "path": "tests", 
                "type": "dir",
                "contents": [
                    {"path": "tests/test_main.py", "type": "file"},
                    {"path": "tests/test_utils.py", "type": "file"}
                ]
            }
        ]
        
        # Call the method with our mock structure
        with mock.patch.object(github_client, 'get_repository_structure') as mock_get_structure:
            mock_get_structure.return_value = structure
            
            stats = github_client.get_project_structure_stats("test-user/test-repo")
            
            # Verify get_repository_structure was called
            mock_get_structure.assert_called_once_with("test-user/test-repo", ref=None)
            
            # Verify the returned stats
            assert stats["total_files"] == 8
            assert stats["total_directories"] == 3
            assert stats["directory_breakdown"] == {
                "root": 2,
                "src": 2,
                "src/models": 2,
                "tests": 2
            }
            assert stats["max_depth"] == 3  # root -> src -> models
            assert stats["file_extensions"] == {
                ".md": 1,
                ".txt": 1,
                ".py": 6
            }

    def test_get_project_structure_stats_error(self, github_client):
        """Test error handling when getting project structure stats."""
        # Setup mock to raise an exception
        with mock.patch.object(github_client, 'get_repository_structure') as mock_get_structure:
            mock_get_structure.side_effect = ClientError("Failed to get repository structure")
            
            # Test that ClientError is raised with appropriate message
            with pytest.raises(ClientError) as excinfo:
                github_client.get_project_structure_stats("test-user/test-repo")
            
            assert "Failed to get project structure statistics" in str(excinfo.value)


if __name__ == "__main__":
    pytest.main(["-v", __file__])