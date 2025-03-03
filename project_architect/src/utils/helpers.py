#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper utilities for Project Architect.

This module provides common utility functions used throughout the Project Architect
application, including file operations, string manipulation, dictionary operations,
and other helper functions that simplify common tasks.
"""

import os
import json
import yaml
import time
import hashlib
import random
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, cast, Set, Tuple
import functools
import logging
from contextlib import contextmanager

# Get logger for this module
from src.utils.logger import get_logger
logger = get_logger(__name__)

# Type variable for generic functions
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Constants
DEFAULT_ENCODING = 'utf-8'
MAX_RETRY_ATTEMPTS = 5
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 60.0
RETRY_BACKOFF_FACTOR = 2.0
RETRY_JITTER = 0.1


def load_json_file(file_path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load JSON data from a file.

    Args:
        file_path: Path to the JSON file
        default: Default value to return if the file doesn't exist or is invalid

    Returns:
        Dictionary containing the JSON data or the default value

    Raises:
        FileNotFoundError: If the file doesn't exist and no default is provided
        json.JSONDecodeError: If the file contains invalid JSON and no default is provided
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding=DEFAULT_ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            logger.warning(f"JSON file not found: {file_path}. Using default value.")
            return default
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        if default is not None:
            logger.warning(f"Invalid JSON in file: {file_path}. Using default value.")
            return default
        logger.error(f"Invalid JSON in file: {file_path}")
        raise


def save_json_file(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_dir: bool = True,
    sort_keys: bool = False,
) -> None:
    """Save data to a JSON file.

    Args:
        data: Dictionary to save as JSON
        file_path: Path where the JSON file will be saved
        indent: Number of spaces for indentation in the JSON file
        ensure_dir: Whether to create the directory if it doesn't exist
        sort_keys: Whether to sort the keys in the JSON output

    Raises:
        IOError: If the file cannot be written
    """
    file_path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(file_path.parent)
    
    try:
        with open(file_path, 'w', encoding=DEFAULT_ENCODING) as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        logger.debug(f"JSON data saved to {file_path}")
    except IOError as e:
        logger.error(f"Failed to save JSON data to {file_path}: {e}")
        raise


def load_yaml_file(file_path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load YAML data from a file.

    Args:
        file_path: Path to the YAML file
        default: Default value to return if the file doesn't exist or is invalid

    Returns:
        Dictionary containing the YAML data or the default value

    Raises:
        FileNotFoundError: If the file doesn't exist and no default is provided
        yaml.YAMLError: If the file contains invalid YAML and no default is provided
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding=DEFAULT_ENCODING) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        if default is not None:
            logger.warning(f"YAML file not found: {file_path}. Using default value.")
            return default
        logger.error(f"YAML file not found: {file_path}")
        raise
    except yaml.YAMLError:
        if default is not None:
            logger.warning(f"Invalid YAML in file: {file_path}. Using default value.")
            return default
        logger.error(f"Invalid YAML in file: {file_path}")
        raise


def save_yaml_file(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    default_flow_style: bool = False,
    ensure_dir: bool = True,
) -> None:
    """Save data to a YAML file.

    Args:
        data: Dictionary to save as YAML
        file_path: Path where the YAML file will be saved
        default_flow_style: YAML flow style (False for block style)
        ensure_dir: Whether to create the directory if it doesn't exist

    Raises:
        IOError: If the file cannot be written
    """
    file_path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(file_path.parent)
    
    try:
        with open(file_path, 'w', encoding=DEFAULT_ENCODING) as f:
            yaml.dump(data, f, default_flow_style=default_flow_style, sort_keys=False)
        logger.debug(f"YAML data saved to {file_path}")
    except IOError as e:
        logger.error(f"Failed to save YAML data to {file_path}: {e}")
        raise


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory to ensure exists

    Returns:
        Path object for the directory

    Raises:
        OSError: If the directory cannot be created
    """
    directory_path = Path(directory_path)
    
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except OSError as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        raise


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to ensure it's valid across operating systems.

    Args:
        filename: The filename to sanitize

    Returns:
        A sanitized filename with invalid characters replaced
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Replace multiple spaces/underscores with a single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized


def merge_dicts(dict1: Dict[K, V], dict2: Dict[K, V]) -> Dict[K, V]:
    """Merge two dictionaries, with values from dict2 taking precedence.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (values override dict1)

    Returns:
        A new dictionary with merged values
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def deep_update(original: Dict[K, Any], update: Dict[K, Any]) -> Dict[K, Any]:
    """Recursively update a dictionary with values from another dictionary.

    Unlike dict.update(), this function will recursively update nested dictionaries.

    Args:
        original: Original dictionary to update
        update: Dictionary with values to update

    Returns:
        The updated dictionary
    """
    for key, value in update.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            original[key] = deep_update(original[key], value)
        else:
            original[key] = value
    return original


def camel_to_snake(name: str) -> str:
    """Convert a camelCase string to snake_case.

    Args:
        name: The camelCase string to convert

    Returns:
        The string converted to snake_case
    """
    # Insert underscore before uppercase letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert a snake_case string to camelCase.

    Args:
        name: The snake_case string to convert

    Returns:
        The string converted to camelCase
    """
    # Split by underscore and capitalize each word except the first
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def get_file_extension(file_path: Union[str, Path]) -> str:
    """Get the extension of a file.

    Args:
        file_path: Path to the file

    Returns:
        The file extension (including the dot) or empty string if no extension
    """
    file_path = Path(file_path)
    suffix = file_path.suffix
    return suffix.lower()


def is_binary_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is binary (non-text).

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file is binary, False otherwise
    """
    # Common binary file extensions
    binary_extensions = {
        '.pyc', '.pyd', '.so', '.dll', '.exe', '.bin', '.dat',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tif', '.tiff',
        '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wav', '.ogg'
    }
    
    # Check extension first
    extension = get_file_extension(file_path)
    if extension in binary_extensions:
        return True
    
    # If extension check is inconclusive, check file content
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # Check for null bytes which typically indicate binary content
            return b'\x00' in chunk
    except (IOError, OSError):
        # If we can't read the file, assume it's not binary
        return False


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
    """Calculate the hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', etc.)

    Returns:
        Hexadecimal string representation of the file hash

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the algorithm is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with open(file_path, 'rb') as f:
        # Read and update hash in chunks to avoid loading large files into memory
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = MAX_RETRY_ATTEMPTS,
    initial_delay: float = INITIAL_RETRY_DELAY,
    max_delay: float = MAX_RETRY_DELAY,
    backoff_factor: float = RETRY_BACKOFF_FACTOR,
    jitter: float = RETRY_JITTER,
    exceptions: Tuple[Exception, ...] = (Exception,),
) -> Callable[..., T]:
    """Decorator to retry a function with exponential backoff.

    Args:
        func: The function to retry
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases
        jitter: Random jitter factor to add to delay
        exceptions: Tuple of exceptions that trigger a retry

    Returns:
        A wrapped function that will be retried on exception
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        attempt = 0
        delay = initial_delay
        
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                attempt += 1
                if attempt >= max_attempts:
                    logger.error(f"Failed after {max_attempts} attempts: {e}")
                    raise
                
                # Calculate delay with jitter
                jitter_amount = random.uniform(-jitter, jitter) * delay
                sleep_time = min(delay + jitter_amount, max_delay)
                
                logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed: {e}. "
                    f"Retrying in {sleep_time:.2f} seconds..."
                )
                
                time.sleep(sleep_time)
                delay = min(delay * backoff_factor, max_delay)
        
        # This should never be reached due to the raise in the loop
        raise RuntimeError("Unexpected error in retry_with_backoff")
    
    return wrapper


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = '',
    separator: str = '.',
) -> Dict[str, Any]:
    """Flatten a nested dictionary.

    Args:
        d: The dictionary to flatten
        parent_key: The parent key for nested dictionaries
        separator: The separator to use between keys

    Returns:
        A flattened dictionary with keys joined by the separator
    """
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(
    d: Dict[str, Any],
    separator: str = '.',
) -> Dict[str, Any]:
    """Unflatten a dictionary with keys separated by a separator.

    Args:
        d: The flattened dictionary
        separator: The separator used between keys

    Returns:
        A nested dictionary
    """
    result: Dict[str, Any] = {}
    for key, value in d.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def copy_directory(
    src: Union[str, Path],
    dst: Union[str, Path],
    ignore_patterns: Optional[List[str]] = None,
) -> None:
    """Copy a directory recursively.

    Args:
        src: Source directory
        dst: Destination directory
        ignore_patterns: List of glob patterns to ignore

    Raises:
        FileNotFoundError: If the source directory doesn't exist
        OSError: If the copy operation fails
    """
    src = Path(src)
    dst = Path(dst)
    
    if not src.exists():
        raise FileNotFoundError(f"Source directory not found: {src}")
    
    if ignore_patterns:
        ignore = shutil.ignore_patterns(*ignore_patterns)
    else:
        ignore = None
    
    try:
        shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
        logger.debug(f"Copied directory from {src} to {dst}")
    except OSError as e:
        logger.error(f"Failed to copy directory from {src} to {dst}: {e}")
        raise


def read_file_content(file_path: Union[str, Path], encoding: str = DEFAULT_ENCODING) -> str:
    """Read the content of a text file.

    Args:
        file_path: Path to the file
        encoding: File encoding

    Returns:
        The content of the file as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file cannot be decoded with the specified encoding
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except UnicodeDecodeError:
        logger.error(f"Failed to decode file {file_path} with encoding {encoding}")
        raise


def write_file_content(
    file_path: Union[str, Path],
    content: str,
    encoding: str = DEFAULT_ENCODING,
    ensure_dir: bool = True,
) -> None:
    """Write content to a text file.

    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding
        ensure_dir: Whether to create the directory if it doesn't exist

    Raises:
        IOError: If the file cannot be written
    """
    file_path = Path(file_path)
    
    if ensure_dir:
        ensure_directory_exists(file_path.parent)
    
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug(f"Content written to {file_path}")
    except IOError as e:
        logger.error(f"Failed to write content to {file_path}: {e}")
        raise


def find_files(
    directory: Union[str, Path],
    pattern: str = '*',
    recursive: bool = True,
) -> List[Path]:
    """Find files matching a pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match files
        recursive: Whether to search recursively

    Returns:
        List of Path objects for matching files

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if recursive:
        return list(directory.glob(f"**/{pattern}"))
    else:
        return list(directory.glob(pattern))


def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """Get the relative path from a base directory.

    Args:
        path: Path to get relative path for
        base: Base directory

    Returns:
        Relative path from base to path
    """
    return Path(path).relative_to(Path(base))


def is_subpath(path: Union[str, Path], parent: Union[str, Path]) -> bool:
    """Check if a path is a subpath of another path.

    Args:
        path: Path to check
        parent: Potential parent path

    Returns:
        True if path is a subpath of parent, False otherwise
    """
    path = Path(path).resolve()
    parent = Path(parent).resolve()
    
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


@contextmanager
def temp_directory() -> Path:
    """Create a temporary directory that is automatically cleaned up.

    Yields:
        Path object for the temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@contextmanager
def working_directory(path: Union[str, Path]) -> None:
    """Context manager to temporarily change the working directory.

    Args:
        path: Directory to change to

    Yields:
        None

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    
    original_dir = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_unique_filename(
    directory: Union[str, Path],
    base_name: str,
    extension: str = '',
) -> Path:
    """Generate a unique filename in a directory.

    Args:
        directory: Directory for the file
        base_name: Base name for the file
        extension: File extension (with or without dot)

    Returns:
        Path object with a unique filename
    """
    directory = Path(directory)
    
    # Ensure extension starts with a dot if provided
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    # Try the base name first
    filename = f"{base_name}{extension}"
    path = directory / filename
    
    # If the file exists, add a number suffix
    counter = 1
    while path.exists():
        filename = f"{base_name}_{counter}{extension}"
        path = directory / filename
        counter += 1
    
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        Size of the file in bytes

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return file_path.stat().st_size


def format_file_size(size_in_bytes: int, precision: int = 2) -> str:
    """Format a file size in human-readable format.

    Args:
        size_in_bytes: Size in bytes
        precision: Number of decimal places

    Returns:
        Human-readable file size (e.g., "1.23 MB")
    """
    if size_in_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0
    while size_in_bytes >= 1024 and i < len(units) - 1:
        size_in_bytes /= 1024
        i += 1
    
    return f"{size_in_bytes:.{precision}f} {units[i]}"


def get_timestamp() -> str:
    """Get a formatted timestamp for the current time.

    Returns:
        Formatted timestamp string (YYYY-MM-DD_HH-MM-SS)
    """
    return time.strftime("%Y-%m-%d_%H-%M-%S")


def remove_empty_directories(directory: Union[str, Path]) -> None:
    """Recursively remove empty directories.

    Args:
        directory: Directory to clean up

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    for path in sorted(directory.glob('**/*'), key=lambda x: len(str(x)), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            logger.debug(f"Removed empty directory: {path}")


def find_duplicates(items: List[T]) -> Dict[T, List[int]]:
    """Find duplicate items in a list and their positions.

    Args:
        items: List of items to check for duplicates

    Returns:
        Dictionary mapping duplicate items to lists of their positions
    """
    seen: Dict[T, List[int]] = {}
    for i, item in enumerate(items):
        if item in seen:
            seen[item].append(i)
        else:
            seen[item] = [i]
    
    # Filter out items that appear only once
    return {item: positions for item, positions in seen.items() if len(positions) > 1}


def group_by(items: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
    """Group items by a key function.

    Args:
        items: List of items to group
        key_func: Function to extract the key for grouping

    Returns:
        Dictionary mapping keys to lists of items
    """
    result: Dict[K, List[T]] = {}
    for item in items:
        key = key_func(item)
        if key in result:
            result[key].append(item)
        else:
            result[key] = [item]
    return result


def replace_in_file(
    file_path: Union[str, Path],
    pattern: str,
    replacement: str,
    encoding: str = DEFAULT_ENCODING,
) -> int:
    """Replace text in a file using regex.

    Args:
        file_path: Path to the file
        pattern: Regex pattern to search for
        replacement: Replacement text
        encoding: File encoding

    Returns:
        Number of replacements made

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        new_content, count = re.subn(pattern, replacement, content)
        
        if count > 0:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(new_content)
            logger.debug(f"Made {count} replacements in {file_path}")
        
        return count
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: URL to validate

    Returns:
        True if the URL is valid, False otherwise
    """
    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http://, https://, ftp://, ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(pattern.match(url))


def get_project_root() -> Path:
    """Get the root directory of the project.
    
    Returns:
        Path object representing the project root directory
    """
    # Assuming this file is in src/utils/helpers.py
    return Path(__file__).parent.parent.parent


def get_config_directory() -> Path:
    """Get the configuration directory of the project.
    
    Returns:
        Path object representing the config directory
    """
    return get_project_root() / 'config'


def get_templates_directory() -> Path:
    """Get the templates directory of the project.
    
    Returns:
        Path object representing the templates directory
    """
    return get_project_root() / 'src' / 'templates'


def get_examples_directory() -> Path:
    """Get the examples directory of the project.
    
    Returns:
        Path object representing the examples directory
    """
    return get_project_root() / 'examples'


def get_docs_directory() -> Path:
    """Get the documentation directory of the project.
    
    Returns:
        Path object representing the docs directory
    """
    return get_project_root() / 'docs'


def ensure_file_exists(file_path: Union[str, Path], default_content: str = '') -> Path:
    """Ensure that a file exists, creating it with default content if necessary.

    Args:
        file_path: Path to the file
        default_content: Default content for the file if it doesn't exist

    Returns:
        Path object for the file

    Raises:
        IOError: If the file cannot be created
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        ensure_directory_exists(file_path.parent)
        try:
            with open(file_path, 'w', encoding=DEFAULT_ENCODING) as f:
                f.write(default_content)
            logger.debug(f"Created file: {file_path}")
        except IOError as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            raise
    
    return file_path


def safe_delete(path: Union[str, Path]) -> bool:
    """Safely delete a file or directory.

    Args:
        path: Path to the file or directory to delete

    Returns:
        True if the deletion was successful, False otherwise
    """
    path = Path(path)
    
    if not path.exists():
        logger.warning(f"Path does not exist, nothing to delete: {path}")
        return True
    
    try:
        if path.is_dir():
            shutil.rmtree(path)
            logger.debug(f"Deleted directory: {path}")
        else:
            path.unlink()
            logger.debug(f"Deleted file: {path}")
        return True
    except (OSError, shutil.Error) as e:
        logger.error(f"Failed to delete {path}: {e}")
        return False


def get_file_modification_time(file_path: Union[str, Path]) -> float:
    """