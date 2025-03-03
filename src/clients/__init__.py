"""
Clients package for Project Architect.

This package contains client implementations for external services used by the Project Architect,
including Anthropic's Claude API and GitHub API. These clients handle communication with external
services, providing a clean interface for the rest of the application.
"""

from typing import Dict, Any, Optional, List, Union
import logging

# Import client implementations
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient
from src.clients.base_client import BaseClient

# Setup package-level logger
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

__all__ = [
    'AnthropicClient',
    'GithubClient',
    'BaseClient',
    'get_client',
    'ClientFactory'
]


def get_client(client_type: str, config: Any) -> Union[AnthropicClient, GithubClient]:
    """Factory function to get the appropriate client instance.
    
    Args:
        client_type: Type of client to create ('anthropic' or 'github')
        config: Configuration object containing API keys and settings
        
    Returns:
        An instance of the requested client
        
    Raises:
        ValueError: If an unknown client type is requested
    """
    if client_type.lower() == 'anthropic':
        return AnthropicClient(config)
    elif client_type.lower() == 'github':
        return GithubClient(config)
    else:
        raise ValueError(f"Unknown client type: {client_type}")


class ClientFactory:
    """Factory class for creating and managing client instances.
    
    This class provides methods to create, cache, and retrieve client instances
    for various external services used by the Project Architect.
    """
    
    def __init__(self, config: Any):
        """Initialize the client factory with configuration.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self._clients: Dict[str, Union[AnthropicClient, GithubClient]] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_client(self, client_type: str) -> Union[AnthropicClient, GithubClient]:
        """Get a client instance, creating it if necessary.
        
        Args:
            client_type: Type of client to retrieve ('anthropic' or 'github')
            
        Returns:
            An instance of the requested client
            
        Raises:
            ValueError: If an unknown client type is requested
        """
        client_type = client_type.lower()
        
        if client_type not in self._clients:
            self.logger.debug(f"Creating new {client_type} client")
            if client_type == 'anthropic':
                self._clients[client_type] = AnthropicClient(self.config)
            elif client_type == 'github':
                self._clients[client_type] = GithubClient(self.config)
            else:
                raise ValueError(f"Unknown client type: {client_type}")
        
        return self._clients[client_type]
    
    def get_anthropic_client(self) -> AnthropicClient:
        """Get an Anthropic client instance.
        
        Returns:
            An instance of AnthropicClient
        """
        return self.get_client('anthropic')
    
    def get_github_client(self) -> GithubClient:
        """Get a GitHub client instance.
        
        Returns:
            An instance of GithubClient
        """
        return self.get_client('github')
    
    def reset_client(self, client_type: str) -> None:
        """Reset a client instance, forcing a new one to be created on next request.
        
        Args:
            client_type: Type of client to reset ('anthropic' or 'github')
            
        Raises:
            ValueError: If an unknown client type is requested
        """
        client_type = client_type.lower()
        
        if client_type not in ['anthropic', 'github']:
            raise ValueError(f"Unknown client type: {client_type}")
        
        if client_type in self._clients:
            self.logger.debug(f"Resetting {client_type} client")
            del self._clients[client_type]
    
    def reset_all_clients(self) -> None:
        """Reset all client instances."""
        self.logger.debug("Resetting all clients")
        self._clients.clear()