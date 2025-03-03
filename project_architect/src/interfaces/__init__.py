"""
Interfaces package for Project Architect.

This package contains the interfaces for interacting with the Project Architect system,
including a command-line interface (CLI) and a REST API. These interfaces provide
different ways to access the core functionality of the system.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import os
from pathlib import Path

# Import interface implementations
from src.interfaces.cli import CLI
from src.interfaces.api import app as api_app

# Setup package-level logger
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

__all__ = [
    'CLI',
    'api_app',
    'InterfaceManager',
    'get_interface',
]


def get_interface(interface_type: str, config: Any) -> Union[CLI, Any]:
    """Factory function to get the appropriate interface instance.
    
    Args:
        interface_type: Type of interface to create ('cli' or 'api')
        config: Configuration object containing settings
        
    Returns:
        An instance of the requested interface
        
    Raises:
        ValueError: If an unknown interface type is requested
    """
    if interface_type.lower() == 'cli':
        return CLI(config)
    elif interface_type.lower() == 'api':
        # For API, we return the FastAPI app instance which is already created
        return api_app
    else:
        raise ValueError(f"Unknown interface type: {interface_type}")


class InterfaceManager:
    """Manager class for handling different interfaces to the Project Architect system.
    
    This class provides methods to initialize, configure, and run different interfaces
    (CLI, API) for interacting with the Project Architect functionality.
    """
    
    def __init__(self, config: Any):
        """Initialize the interface manager with configuration.
        
        Args:
            config: Configuration object containing settings
        """
        self.config = config
        self._interfaces: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_interface(self, interface_type: str) -> Any:
        """Get an interface instance, creating it if necessary.
        
        Args:
            interface_type: Type of interface to retrieve ('cli' or 'api')
            
        Returns:
            An instance of the requested interface
            
        Raises:
            ValueError: If an unknown interface type is requested
        """
        interface_type = interface_type.lower()
        
        if interface_type not in self._interfaces:
            self.logger.debug(f"Creating new {interface_type} interface")
            if interface_type == 'cli':
                self._interfaces[interface_type] = CLI(self.config)
            elif interface_type == 'api':
                # For API, we use the pre-created FastAPI app instance
                self._interfaces[interface_type] = api_app
            else:
                raise ValueError(f"Unknown interface type: {interface_type}")
        
        return self._interfaces[interface_type]
    
    def run_interface(self, interface_type: str, **kwargs) -> None:
        """Run the specified interface.
        
        Args:
            interface_type: Type of interface to run ('cli' or 'api')
            **kwargs: Additional arguments to pass to the interface's run method
            
        Raises:
            ValueError: If an unknown interface type is requested
        """
        interface_type = interface_type.lower()
        
        if interface_type == 'cli':
            cli = self.get_interface('cli')
            cli.run(**kwargs)
        elif interface_type == 'api':
            import uvicorn
            
            # Default API settings
            host = kwargs.get('host', self.config.get('api_host', '127.0.0.1'))
            port = kwargs.get('port', self.config.get('api_port', 8000))
            reload = kwargs.get('reload', self.config.get('api_reload', False))
            
            self.logger.info(f"Starting API server on {host}:{port}")
            uvicorn.run("src.interfaces.api:app", host=host, port=port, reload=reload)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
    
    def get_cli(self) -> CLI:
        """Get the CLI interface instance.
        
        Returns:
            An instance of CLI
        """
        return self.get_interface('cli')
    
    def get_api(self) -> Any:
        """Get the API interface instance.
        
        Returns:
            The FastAPI app instance
        """
        return self.get_interface('api')
    
    def run_cli(self, **kwargs) -> None:
        """Run the CLI interface.
        
        Args:
            **kwargs: Additional arguments to pass to the CLI's run method
        """
        self.run_interface('cli', **kwargs)
    
    def run_api(self, **kwargs) -> None:
        """Run the API interface.
        
        Args:
            **kwargs: Additional arguments to pass to the API server
                host: Host to bind to (default: from config or '127.0.0.1')
                port: Port to bind to (default: from config or 8000)
                reload: Whether to enable auto-reload (default: from config or False)
        """
        self.run_interface('api', **kwargs)
    
    def get_available_interfaces(self) -> List[str]:
        """Get a list of available interface types.
        
        Returns:
            List of available interface type names
        """
        return ['cli', 'api']
    
    def get_interface_info(self, interface_type: str) -> Dict[str, Any]:
        """Get information about a specific interface.
        
        Args:
            interface_type: Type of interface to get info for ('cli' or 'api')
            
        Returns:
            Dictionary containing interface information
            
        Raises:
            ValueError: If an unknown interface type is requested
        """
        interface_type = interface_type.lower()
        
        if interface_type == 'cli':
            return {
                'type': 'cli',
                'description': 'Command Line Interface for Project Architect',
                'entry_point': 'src.interfaces.cli:CLI',
                'config_section': 'cli',
            }
        elif interface_type == 'api':
            return {
                'type': 'api',
                'description': 'REST API for Project Architect',
                'entry_point': 'src.interfaces.api:app',
                'config_section': 'api',
                'default_host': self.config.get('api_host', '127.0.0.1'),
                'default_port': self.config.get('api_port', 8000),
            }
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")