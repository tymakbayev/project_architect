import os
import logging
from typing import Dict, List, Optional, Any, Union
import requests
from base64 import b64decode

from src.config.config import Config

logger = logging.getLogger(__name__)

class Repository:
    """Class representing a GitHub repository."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize a Repository object from GitHub API data.
        
        Args:
            data: Dictionary containing repository data from GitHub API
        """
        self.name = data.get('name', '')
        self.full_name = data.get('full_name', '')
        self.description = data.get('description', '')
        self.url = data.get('html_url', '')
        self.api_url = data.get('url', '')
        self.stars = data.get('stargazers_count', 0)
        self.forks = data.get('forks_count', 0)
        self.language = data.get('language', '')
        self.topics = data.get('topics', [])
        self.default_branch = data.get('default_branch', 'main')

class GitHubClient:
    """Client for interacting with GitHub API.
    
    This class provides methods to search repositories, get repository structure,
    and retrieve file content from GitHub repositories.
    """
    
    def __init__(self, config: Config):
        """Initialize the GitHub client with configuration.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if config.github_token:
            self.headers["Authorization"] = f"token {config.github_token}"
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the GitHub API.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            Response data as a dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> List[Repository]:
        """Search for repositories on GitHub.
        
        Args:
            query: Search query
            sort: Sort field (stars, forks, updated)
            order: Sort order (asc, desc)
            per_page: Number of results per page
            
        Returns:
            List of Repository objects matching the search criteria
        """
        try:
            params = {
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page
            }
            
            data = self._make_request("search/repositories", params)
            repositories = [Repository(repo_data) for repo_data in data.get("items", [])]
            return repositories
        except requests.RequestException as e:
            logger.error(f"Error searching GitHub repositories: {str(e)}")
            return []
    
    def get_repository_structure(self, repo_name: str, path: str = "", ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the structure of a repository or a specific directory.
        
        Args:
            repo_name: Repository name in the format 'owner/repo'
            path: Path within the repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            List of dictionaries representing files and directories
        """
        try:
            endpoint = f"repos/{repo_name}/contents/{path}"
            params = {}
            if ref:
                params["ref"] = ref
                
            return self._make_request(endpoint, params)
        except requests.RequestException as e:
            logger.error(f"Error getting repository structure: {str(e)}")
            return []
    
    def get_file_content(self, repo_name: str, file_path: str, ref: Optional[str] = None) -> str:
        """Get the content of a file from a repository.
        
        Args:
            repo_name: Repository name in the format 'owner/repo'
            file_path: Path to the file within the repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            Content of the file as a string
            
        Raises:
            ValueError: If the file is not found or is not a file
        """
        try:
            endpoint = f"repos/{repo_name}/contents/{file_path}"
            params = {}
            if ref:
                params["ref"] = ref
                
            data = self._make_request(endpoint, params)
            
            if isinstance(data, list):
                raise ValueError(f"{file_path} is a directory, not a file")
                
            if data.get("type") != "file":
                raise ValueError(f"{file_path} is not a file")
                
            content = data.get("content", "")
            encoding = data.get("encoding")
            
            if encoding == "base64":
                return b64decode(content).decode("utf-8")
            else:
                return content
        except requests.RequestException as e:
            logger.error(f"Error getting file content: {str(e)}")
            raise ValueError(f"Could not retrieve file content: {str(e)}")