#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validators module for Project Architect.

This module provides validation functions for various inputs and data structures
used throughout the Project Architect application. These validators ensure data
integrity, format correctness, and security by validating user inputs, configuration
parameters, file paths, and other critical data before processing.
"""

import os
import re
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Pattern, Callable, TypeVar, cast
import jsonschema
from jsonschema import validate, ValidationError

# Get module logger
from src.utils.logger import get_logger
logger = get_logger(__name__)

# Regular expressions for validation
PROJECT_NAME_PATTERN: Pattern[str] = re.compile(r'^[a-zA-Z][\w\-]*$')
VERSION_PATTERN: Pattern[str] = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$')
PYTHON_IDENTIFIER_PATTERN: Pattern[str] = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
API_KEY_PATTERN: Pattern[str] = re.compile(r'^[A-Za-z0-9_\-\.]+$')
EMAIL_PATTERN: Pattern[str] = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_PATTERN: Pattern[str] = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$')

# Maximum lengths for string inputs
MAX_PROJECT_NAME_LENGTH: int = 100
MAX_DESCRIPTION_LENGTH: int = 5000
MAX_PATH_LENGTH: int = 260  # Windows max path limit

# Common validation error messages
ERRORS = {
    "project_name_invalid": "Project name must start with a letter and contain only letters, numbers, underscores, and hyphens.",
    "project_name_too_long": f"Project name must be less than {MAX_PROJECT_NAME_LENGTH} characters.",
    "description_too_long": f"Project description must be less than {MAX_DESCRIPTION_LENGTH} characters.",
    "path_too_long": f"Path length must be less than {MAX_PATH_LENGTH} characters.",
    "path_not_exists": "The specified path does not exist.",
    "path_not_directory": "The specified path is not a directory.",
    "path_not_file": "The specified path is not a file.",
    "path_not_writable": "The specified path is not writable.",
    "path_not_readable": "The specified path is not readable.",
    "json_invalid": "Invalid JSON format.",
    "yaml_invalid": "Invalid YAML format.",
    "api_key_invalid": "Invalid API key format.",
    "python_identifier_invalid": "Invalid Python identifier. Must start with a letter or underscore and contain only letters, numbers, and underscores.",
    "version_invalid": "Invalid version string. Must follow semantic versioning (e.g., 1.0.0).",
    "email_invalid": "Invalid email address format.",
    "url_invalid": "Invalid URL format.",
}


class ValidationException(Exception):
    """Exception raised for validation errors in the input."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        """Initialize ValidationException with a message and optional field and value.
        
        Args:
            message: The error message
            field: The field that failed validation
            value: The value that failed validation
        """
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
        
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.field:
            return f"Validation error for '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


def validate_project_name(name: str) -> bool:
    """Validate a project name.
    
    Args:
        name: The project name to validate
        
    Returns:
        True if the project name is valid
        
    Raises:
        ValidationException: If the project name is invalid
    """
    if not name:
        raise ValidationException("Project name cannot be empty.", "project_name", name)
    
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        raise ValidationException(ERRORS["project_name_too_long"], "project_name", name)
    
    if not PROJECT_NAME_PATTERN.match(name):
        raise ValidationException(ERRORS["project_name_invalid"], "project_name", name)
    
    return True


def validate_project_description(description: str) -> bool:
    """Validate a project description.
    
    Args:
        description: The project description to validate
        
    Returns:
        True if the project description is valid
        
    Raises:
        ValidationException: If the project description is invalid
    """
    if not description:
        raise ValidationException("Project description cannot be empty.", "project_description", description)
    
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValidationException(ERRORS["description_too_long"], "project_description", description)
    
    return True


def validate_file_path(path: Union[str, Path], must_exist: bool = True, 
                      check_readable: bool = False, check_writable: bool = False) -> bool:
    """Validate a file path.
    
    Args:
        path: The file path to validate
        must_exist: Whether the file must exist
        check_readable: Whether to check if the file is readable
        check_writable: Whether to check if the file is writable
        
    Returns:
        True if the file path is valid
        
    Raises:
        ValidationException: If the file path is invalid
    """
    path_str = str(path)
    
    if not path_str:
        raise ValidationException("File path cannot be empty.", "file_path", path_str)
    
    if len(path_str) > MAX_PATH_LENGTH:
        raise ValidationException(ERRORS["path_too_long"], "file_path", path_str)
    
    path_obj = Path(path_str)
    
    if must_exist and not path_obj.exists():
        raise ValidationException(ERRORS["path_not_exists"], "file_path", path_str)
    
    if must_exist and not path_obj.is_file():
        raise ValidationException(ERRORS["path_not_file"], "file_path", path_str)
    
    if check_readable and must_exist and not os.access(path_str, os.R_OK):
        raise ValidationException(ERRORS["path_not_readable"], "file_path", path_str)
    
    if check_writable:
        if path_obj.exists() and not os.access(path_str, os.W_OK):
            raise ValidationException(ERRORS["path_not_writable"], "file_path", path_str)
        elif not path_obj.exists():
            # Check if parent directory is writable
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                raise ValidationException(f"Parent directory '{parent_dir}' does not exist.", "file_path", path_str)
            if not os.access(str(parent_dir), os.W_OK):
                raise ValidationException(f"Parent directory '{parent_dir}' is not writable.", "file_path", path_str)
    
    return True


def validate_directory_path(path: Union[str, Path], must_exist: bool = True,
                           check_writable: bool = False) -> bool:
    """Validate a directory path.
    
    Args:
        path: The directory path to validate
        must_exist: Whether the directory must exist
        check_writable: Whether to check if the directory is writable
        
    Returns:
        True if the directory path is valid
        
    Raises:
        ValidationException: If the directory path is invalid
    """
    path_str = str(path)
    
    if not path_str:
        raise ValidationException("Directory path cannot be empty.", "directory_path", path_str)
    
    if len(path_str) > MAX_PATH_LENGTH:
        raise ValidationException(ERRORS["path_too_long"], "directory_path", path_str)
    
    path_obj = Path(path_str)
    
    if must_exist and not path_obj.exists():
        raise ValidationException(ERRORS["path_not_exists"], "directory_path", path_str)
    
    if must_exist and not path_obj.is_dir():
        raise ValidationException(ERRORS["path_not_directory"], "directory_path", path_str)
    
    if check_writable:
        if path_obj.exists() and not os.access(path_str, os.W_OK):
            raise ValidationException(ERRORS["path_not_writable"], "directory_path", path_str)
        elif not path_obj.exists():
            # Check if parent directory is writable
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                raise ValidationException(f"Parent directory '{parent_dir}' does not exist.", "directory_path", path_str)
            if not os.access(str(parent_dir), os.W_OK):
                raise ValidationException(f"Parent directory '{parent_dir}' is not writable.", "directory_path", path_str)
    
    return True


def validate_json(json_str: str) -> bool:
    """Validate a JSON string.
    
    Args:
        json_str: The JSON string to validate
        
    Returns:
        True if the JSON string is valid
        
    Raises:
        ValidationException: If the JSON string is invalid
    """
    if not json_str:
        raise ValidationException("JSON string cannot be empty.", "json", json_str)
    
    try:
        json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationException(f"{ERRORS['json_invalid']} {str(e)}", "json", json_str)
    
    return True


def validate_json_schema(json_data: Union[Dict[str, Any], List[Any], str], schema: Dict[str, Any]) -> bool:
    """Validate JSON data against a JSON schema.
    
    Args:
        json_data: The JSON data to validate (dict, list, or string)
        schema: The JSON schema to validate against
        
    Returns:
        True if the JSON data is valid according to the schema
        
    Raises:
        ValidationException: If the JSON data is invalid according to the schema
    """
    # Convert string to dict if needed
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValidationException(f"{ERRORS['json_invalid']} {str(e)}", "json_data", json_data)
    
    try:
        validate(instance=json_data, schema=schema)
    except ValidationError as e:
        raise ValidationException(f"JSON schema validation error: {str(e)}", "json_data", json_data)
    
    return True


def validate_yaml(yaml_str: str) -> bool:
    """Validate a YAML string.
    
    Args:
        yaml_str: The YAML string to validate
        
    Returns:
        True if the YAML string is valid
        
    Raises:
        ValidationException: If the YAML string is invalid
    """
    if not yaml_str:
        raise ValidationException("YAML string cannot be empty.", "yaml", yaml_str)
    
    try:
        yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise ValidationException(f"{ERRORS['yaml_invalid']} {str(e)}", "yaml", yaml_str)
    
    return True


def validate_api_key(api_key: str) -> bool:
    """Validate an API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the API key is valid
        
    Raises:
        ValidationException: If the API key is invalid
    """
    if not api_key:
        raise ValidationException("API key cannot be empty.", "api_key", api_key)
    
    if not API_KEY_PATTERN.match(api_key):
        raise ValidationException(ERRORS["api_key_invalid"], "api_key", api_key)
    
    return True


def is_valid_python_identifier(identifier: str) -> bool:
    """Check if a string is a valid Python identifier.
    
    Args:
        identifier: The string to check
        
    Returns:
        True if the string is a valid Python identifier, False otherwise
    """
    if not identifier:
        return False
    
    return bool(PYTHON_IDENTIFIER_PATTERN.match(identifier))


def validate_python_identifier(identifier: str) -> bool:
    """Validate a Python identifier.
    
    Args:
        identifier: The identifier to validate
        
    Returns:
        True if the identifier is valid
        
    Raises:
        ValidationException: If the identifier is invalid
    """
    if not identifier:
        raise ValidationException("Python identifier cannot be empty.", "identifier", identifier)
    
    if not is_valid_python_identifier(identifier):
        raise ValidationException(ERRORS["python_identifier_invalid"], "identifier", identifier)
    
    # Check if the identifier is a Python keyword
    import keyword
    if keyword.iskeyword(identifier):
        raise ValidationException(f"'{identifier}' is a Python keyword and cannot be used as an identifier.", "identifier", identifier)
    
    return True


def is_valid_version_string(version: str) -> bool:
    """Check if a string is a valid semantic version.
    
    Args:
        version: The string to check
        
    Returns:
        True if the string is a valid semantic version, False otherwise
    """
    if not version:
        return False
    
    return bool(VERSION_PATTERN.match(version))


def validate_version_string(version: str) -> bool:
    """Validate a semantic version string.
    
    Args:
        version: The version string to validate
        
    Returns:
        True if the version string is valid
        
    Raises:
        ValidationException: If the version string is invalid
    """
    if not version:
        raise ValidationException("Version string cannot be empty.", "version", version)
    
    if not is_valid_version_string(version):
        raise ValidationException(ERRORS["version_invalid"], "version", version)
    
    return True


def validate_email(email: str) -> bool:
    """Validate an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email address is valid
        
    Raises:
        ValidationException: If the email address is invalid
    """
    if not email:
        raise ValidationException("Email address cannot be empty.", "email", email)
    
    if not EMAIL_PATTERN.match(email):
        raise ValidationException(ERRORS["email_invalid"], "email", email)
    
    return True


def validate_url(url: str) -> bool:
    """Validate a URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if the URL is valid
        
    Raises:
        ValidationException: If the URL is invalid
    """
    if not url:
        raise ValidationException("URL cannot be empty.", "url", url)
    
    if not URL_PATTERN.match(url):
        raise ValidationException(ERRORS["url_invalid"], "url", url)
    
    return True


def validate_project_type(project_type: str, supported_types: Optional[List[str]] = None) -> bool:
    """Validate a project type.
    
    Args:
        project_type: The project type to validate
        supported_types: List of supported project types
        
    Returns:
        True if the project type is valid
        
    Raises:
        ValidationException: If the project type is invalid
    """
    if not project_type:
        raise ValidationException("Project type cannot be empty.", "project_type", project_type)
    
    if supported_types is None:
        # Import here to avoid circular imports
        from src.utils import SUPPORTED_PROJECT_TYPES
        supported_types = SUPPORTED_PROJECT_TYPES
    
    if project_type not in supported_types:
        supported_types_str = ", ".join(supported_types)
        raise ValidationException(
            f"Unsupported project type: '{project_type}'. Supported types are: {supported_types_str}",
            "project_type",
            project_type
        )
    
    return True


def validate_dependencies(dependencies: List[str]) -> bool:
    """Validate a list of dependencies.
    
    Args:
        dependencies: The list of dependencies to validate
        
    Returns:
        True if the dependencies are valid
        
    Raises:
        ValidationException: If any dependency is invalid
    """
    if not isinstance(dependencies, list):
        raise ValidationException("Dependencies must be a list.", "dependencies", dependencies)
    
    # Validate each dependency
    for i, dep in enumerate(dependencies):
        if not isinstance(dep, str):
            raise ValidationException(f"Dependency at index {i} must be a string.", "dependencies", dep)
        
        if not dep:
            raise ValidationException(f"Dependency at index {i} cannot be empty.", "dependencies", dep)
        
        # Basic package name validation
        # Package names can contain letters, numbers, underscores, hyphens, and dots
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', dep.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()):
            raise ValidationException(f"Invalid package name in dependency: '{dep}'", "dependencies", dep)
    
    return True


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate a file extension.
    
    Args:
        filename: The filename to validate
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if the file extension is valid
        
    Raises:
        ValidationException: If the file extension is invalid
    """
    if not filename:
        raise ValidationException("Filename cannot be empty.", "filename", filename)
    
    # Get the file extension
    _, ext = os.path.splitext(filename)
    
    if not ext and '.' not in allowed_extensions:
        # If no extension and empty extension is allowed
        return True
    
    if ext not in allowed_extensions:
        allowed_ext_str = ", ".join(allowed_extensions)
        raise ValidationException(
            f"Invalid file extension: '{ext}'. Allowed extensions are: {allowed_ext_str}",
            "filename",
            filename
        )
    
    return True


def validate_dict_keys(data: Dict[str, Any], required_keys: List[str], 
                      optional_keys: Optional[List[str]] = None) -> bool:
    """Validate that a dictionary contains required keys and only allowed keys.
    
    Args:
        data: The dictionary to validate
        required_keys: List of required keys
        optional_keys: List of optional keys
        
    Returns:
        True if the dictionary is valid
        
    Raises:
        ValidationException: If the dictionary is invalid
    """
    if not isinstance(data, dict):
        raise ValidationException("Data must be a dictionary.", "data", data)
    
    # Check for required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        missing_keys_str = ", ".join(missing_keys)
        raise ValidationException(f"Missing required keys: {missing_keys_str}", "data", data)
    
    # Check for unknown keys if optional_keys is provided
    if optional_keys is not None:
        allowed_keys = set(required_keys + optional_keys)
        unknown_keys = [key for key in data.keys() if key not in allowed_keys]
        if unknown_keys:
            unknown_keys_str = ", ".join(unknown_keys)
            raise ValidationException(f"Unknown keys: {unknown_keys_str}", "data", data)
    
    return True


def validate_input_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                        max_value: Optional[Union[int, float]] = None) -> bool:
    """Validate that a numeric value is within a specified range.
    
    Args:
        value: The value to validate
        min_value: The minimum allowed value
        max_value: The maximum allowed value
        
    Returns:
        True if the value is valid
        
    Raises:
        ValidationException: If the value is invalid
    """
    if not isinstance(value, (int, float)):
        raise ValidationException(f"Value must be a number, got {type(value).__name__}", "value", value)
    
    if min_value is not None and value < min_value:
        raise ValidationException(f"Value {value} is less than minimum {min_value}", "value", value)
    
    if max_value is not None and value > max_value:
        raise ValidationException(f"Value {value} is greater than maximum {max_value}", "value", value)
    
    return True


def validate_string_length(value: str, min_length: Optional[int] = None, 
                          max_length: Optional[int] = None) -> bool:
    """Validate that a string's length is within a specified range.
    
    Args:
        value: The string to validate
        min_length: The minimum allowed length
        max_length: The maximum allowed length
        
    Returns:
        True if the string is valid
        
    Raises:
        ValidationException: If the string is invalid
    """
    if not isinstance(value, str):
        raise ValidationException(f"Value must be a string, got {type(value).__name__}", "value", value)
    
    if min_length is not None and len(value) < min_length:
        raise ValidationException(f"String length {len(value)} is less than minimum {min_length}", "value", value)
    
    if max_length is not None and len(value) > max_length:
        raise ValidationException(f"String length {len(value)} is greater than maximum {max_length}", "value", value)
    
    return True


def validate_list_length(value: List[Any], min_length: Optional[int] = None, 
                        max_length: Optional[int] = None) -> bool:
    """Validate that a list's length is within a specified range.
    
    Args:
        value: The list to validate
        min_length: The minimum allowed length
        max_length: The maximum allowed length
        
    Returns:
        True if the list is valid
        
    Raises:
        ValidationException: If the list is invalid
    """
    if not isinstance(value, list):
        raise ValidationException(f"Value must be a list, got {type(value).__name__}", "value", value)
    
    if min_length is not None and len(value) < min_length:
        raise ValidationException(f"List length {len(value)} is less than minimum {min_length}", "value", value)
    
    if max_length is not None and len(value) > max_length:
        raise ValidationException(f"List length {len(value)} is greater than maximum {max_length}", "value", value)
    
    return True


def validate_enum(value: Any, allowed_values: List[Any]) -> bool:
    """Validate that a value is one of a set of allowed values.
    
    Args:
        value: The value to validate
        allowed_values: List of allowed values
        
    Returns:
        True if the value is valid
        
    Raises:
        ValidationException: If the value is invalid
    """
    if value not in allowed_values:
        allowed_values_str = ", ".join(str(v) for v in allowed_values)
        raise ValidationException(
            f"Invalid value: '{value}'. Allowed values are: {allowed_values_str}",
            "value",
            value
        )
    
    return True


# Type variable for generic validation function
T = TypeVar('T')

def validate_with_function(value: T, validation_func: Callable[[T], bool], 
                          error_message: str = "Validation failed") -> bool:
    """Validate a value using a custom validation function.
    
    Args:
        value: The value to validate
        validation_func: A function that takes the value and returns True if valid
        error_message: The error message to use if validation fails
        
    Returns:
        True if the value is valid
        
    Raises:
        ValidationException: If the value is invalid
    """
    if not validation_func(value):
        raise ValidationException(error_message, "value", value)
    
    return True


def validate_all(validations: List[Callable[[], bool]]) -> bool:
    """Run multiple validation functions and collect all errors.
    
    Args:
        validations: List of validation functions to run
        
    Returns:
        True if all validations pass
        
    Raises:
        ValidationException: If any validation fails, with all error messages combined
    """
    errors = []
    
    for validation in validations:
        try:
            validation()
        except ValidationException as e:
            errors.append(str(e))
    
    if errors:
        raise ValidationException("\n".join(errors))
    
    return True