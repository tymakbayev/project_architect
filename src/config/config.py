import os
import json
from typing import Dict, Optional, Any, Union
from pathlib import Path


class Config:
    """Configuration management for the application.

    This class provides methods for loading configuration from files
    and retrieving API keys for Anthropic and GitHub services.
    """

    def __init__(self):
        """Initialize the configuration object with empty settings."""
        self.config: Dict[str, Any] = {}
        self.anthropic_api_key: Optional[str] = None
        self.anthropic_model: Optional[str] = None
        self.anthropic_max_tokens: Optional[int] = None
        self.github_token: Optional[str] = None
        self._load_from_env()

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from a file.

        Args:
            config_path: Path to the configuration file. If not specified,
                         uses the value from CONFIG_PATH environment variable
                         or 'config/default_config.json' by default.

        Returns:
            Dictionary with configuration parameters.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        if not config_path:
            config_path = os.environ.get('CONFIG_PATH', 'config/default_config.json')

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Update API keys from config if not already set from environment
            if not self.anthropic_api_key and 'clients' in self.config and 'anthropic' in self.config['clients']:
                self.anthropic_api_key = self.config['clients']['anthropic'].get('api_key')
                self.anthropic_model = self.config['clients']['anthropic'].get('model')
                self.anthropic_max_tokens = self.config['clients']['anthropic'].get('max_tokens')
            
            if not self.github_token and 'clients' in self.config and 'github' in self.config['clients']:
                self.github_token = self.config['clients']['github'].get('api_key')
            
            return self.config
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {config_path}")
            raise

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Anthropic API configuration
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.anthropic_model = os.environ.get('ANTHROPIC_MODEL')
        if 'ANTHROPIC_MAX_TOKENS' in os.environ:
            try:
                self.anthropic_max_tokens = int(os.environ.get('ANTHROPIC_MAX_TOKENS', '4000'))
            except ValueError:
                self.anthropic_max_tokens = 4000
        
        # GitHub API configuration
        self.github_token = os.environ.get('GITHUB_API_TOKEN') or os.environ.get('GITHUB_TOKEN')

    def get_anthropic_api_key(self) -> str:
        """Get the Anthropic API key.

        Returns:
            The Anthropic API key.

        Raises:
            ValueError: If the API key is not found in configuration or environment.
        """
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not found in configuration or environment. "
                             "Please set ANTHROPIC_API_KEY environment variable or provide it in config.")
        return self.anthropic_api_key

    def get_github_token(self) -> Optional[str]:
        """Get the GitHub API token.

        Returns:
            The GitHub API token, or None if not set.
        """
        return self.github_token

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Args:
            key: The configuration key.
            default: Default value to return if key is not found.

        Returns:
            The configuration value, or default if not found.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key.
            value: The value to set.
        """
        self.config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary containing all configuration values.
        """
        return self.config.copy()

    def save(self, config_path: str) -> None:
        """Save configuration to a file.

        Args:
            config_path: Path where to save the configuration.

        Raises:
            IOError: If the file cannot be written.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {config_path}")
        except IOError as e:
            print(f"Error saving configuration to {config_path}: {e}")
            raise
