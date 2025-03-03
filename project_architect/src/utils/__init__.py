"""
Utils package for Project Architect.

This package contains utility modules that provide common functionality used across
the Project Architect application, including logging, validation, and helper functions.
These utilities are designed to be reusable components that simplify and standardize
common operations throughout the codebase.
"""

from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, cast
import logging
import os
import json
import re
import time
import functools
import hashlib
from pathlib import Path

# Import utility modules
from src.utils.logger import setup_logger, get_logger, configure_logging
from src.utils.validators import (
    validate_project_name,
    validate_project_description,
    validate_file_path,
    validate_directory_path,
    validate_json,
    validate_yaml,
    validate_api_key,
    is_valid_python_identifier,
    is_valid_version_string
)
from src.utils.helpers import (
    load_json_file,
    save_json_file,
    load_yaml_file,
    save_yaml_file,
    ensure_directory_exists,
    sanitize_filename,
    merge_dicts,
    deep_update,
    camel_to_snake,
    snake_to_camel,
    get_file_extension,
    is_binary_file,
    calculate_file_hash,
    retry_with_backoff
)

# Setup package-level logger
logger = logging.getLogger(__name__)
setup_logger()

# Define what's available when using "from src.utils import *"
__all__ = [
    # Logger functions
    'setup_logger',
    'get_logger',
    'configure_logging',
    
    # Validator functions
    'validate_project_name',
    'validate_project_description',
    'validate_file_path',
    'validate_directory_path',
    'validate_json',
    'validate_yaml',
    'validate_api_key',
    'is_valid_python_identifier',
    'is_valid_version_string',
    
    # Helper functions
    'load_json_file',
    'save_json_file',
    'load_yaml_file',
    'save_yaml_file',
    'ensure_directory_exists',
    'sanitize_filename',
    'merge_dicts',
    'deep_update',
    'camel_to_snake',
    'snake_to_camel',
    'get_file_extension',
    'is_binary_file',
    'calculate_file_hash',
    'retry_with_backoff',
    
    # Constants
    'DEFAULT_ENCODING',
    'SUPPORTED_PROJECT_TYPES',
    'SUPPORTED_FILE_EXTENSIONS',
]

# Common constants used across the application
DEFAULT_ENCODING = 'utf-8'
SUPPORTED_PROJECT_TYPES = ['python', 'javascript', 'typescript', 'react', 'node', 'web', 'django', 'flask']
SUPPORTED_FILE_EXTENSIONS = {
    'python': ['.py', '.pyi', '.pyx', '.pyd'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'typescript': ['.ts', '.tsx'],
    'web': ['.html', '.css', '.scss', '.sass', '.less'],
    'data': ['.json', '.yaml', '.yml', '.xml', '.csv', '.toml'],
    'markdown': ['.md', '.markdown'],
    'config': ['.ini', '.cfg', '.conf', '.env'],
    'docker': ['Dockerfile', '.dockerignore', 'docker-compose.yml', 'docker-compose.yaml'],
}


# Utility function for memoization
T = TypeVar('T')
def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """Memoize the results of a function call to avoid redundant computation.
    
    Args:
        func: The function to memoize
        
    Returns:
        A wrapped function that caches results based on input arguments
    """
    cache: Dict[str, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Create a key from the function arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cast(T, cache[key])
    
    return wrapper


def get_project_root() -> Path:
    """Get the root directory of the project.
    
    Returns:
        Path object representing the project root directory
    """
    # Assuming this file is in src/utils/__init__.py
    return Path(__file__).parent.parent.parent


def get_template_path(template_type: str) -> Path:
    """Get the path to a specific template directory.
    
    Args:
        template_type: The type of template (e.g., 'python', 'react', 'node')
        
    Returns:
        Path object representing the template directory
        
    Raises:
        ValueError: If the template type is not supported
    """
    if template_type.lower() not in SUPPORTED_PROJECT_TYPES:
        raise ValueError(f"Unsupported template type: {template_type}")
    
    template_path = get_project_root() / 'src' / 'templates' / template_type.lower()
    
    if not template_path.exists():
        raise ValueError(f"Template directory not found: {template_path}")
    
    return template_path


def format_exception(exc: Exception) -> str:
    """Format an exception into a readable string.
    
    Args:
        exc: The exception to format
        
    Returns:
        A formatted string representation of the exception
    """
    return f"{type(exc).__name__}: {str(exc)}"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to a maximum length.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the resulting string
        suffix: String to append if truncation occurs
        
    Returns:
        The truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_debug_mode() -> bool:
    """Check if the application is running in debug mode.
    
    Returns:
        True if debug mode is enabled, False otherwise
    """
    return os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on')


def get_environment() -> str:
    """Get the current environment (development, testing, production).
    
    Returns:
        The current environment name
    """
    return os.environ.get('ENVIRONMENT', 'development').lower()


class Timer:
    """Utility class for timing code execution.
    
    This class can be used as a context manager or decorator to measure
    the execution time of code blocks or functions.
    """
    
    def __init__(self, name: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """Initialize the timer.
        
        Args:
            name: Optional name for the timer
            logger: Optional logger to log the timing information
        """
        self.name = name or "Timer"
        self.logger = logger or logging.getLogger(__name__)
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self) -> 'Timer':
        """Start the timer when entering the context.
        
        Returns:
            The Timer instance
        """
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the timer when exiting the context and log the elapsed time.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.end_time = time.time()
        elapsed = self.elapsed()
        self.logger.debug(f"{self.name} completed in {elapsed:.4f} seconds")
    
    def __call__(self, func: Callable) -> Callable:
        """Use the timer as a decorator.
        
        Args:
            func: The function to time
            
        Returns:
            A wrapped function that times execution
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Timer(name=f"{func.__name__}", logger=self.logger):
                return func(*args, **kwargs)
        return wrapper
    
    def elapsed(self) -> float:
        """Get the elapsed time.
        
        Returns:
            The elapsed time in seconds
            
        Raises:
            RuntimeError: If the timer hasn't been started
        """
        if self.start_time is None:
            raise RuntimeError("Timer hasn't been started")
        
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time