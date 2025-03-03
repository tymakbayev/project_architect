#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger module for Project Architect.

This module provides logging functionality for the Project Architect application,
including configuration, setup, and utility functions for logging across the application.
It supports different log levels, formatting options, and output destinations.
"""

import os
import sys
import json
import logging
import logging.config
from typing import Dict, Any, Optional, Union, TextIO
from pathlib import Path
import datetime
import functools
import inspect
from contextlib import contextmanager

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log levels for different environments
LOG_LEVELS = {
    "development": logging.DEBUG,
    "testing": logging.INFO,
    "production": logging.WARNING,
}

# ANSI color codes for colored terminal output
COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[41m",  # Red background
    "RESET": "\033[0m",      # Reset to default
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored console output."""

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        use_colors: bool = True,
    ):
        """Initialize the formatter with specified format strings.

        Args:
            fmt: The format string for the message
            datefmt: The format string for the date/time
            style: The style of the format string (%, {, or $)
            use_colors: Whether to use colors in the output
        """
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with optional color.

        Args:
            record: The log record to format

        Returns:
            The formatted log message with color codes if enabled
        """
        levelname = record.levelname
        message = super().format(record)
        
        if self.use_colors and levelname in COLORS:
            message = f"{COLORS[levelname]}{message}{COLORS['RESET']}"
            
        return message


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the specified name.

    If no name is provided, returns a logger with the name of the calling module.

    Args:
        name: The name of the logger to get

    Returns:
        A logger instance
    """
    if name is None:
        # Get the name of the calling module
        frame = inspect.currentframe()
        if frame is not None and frame.f_back is not None:
            module = inspect.getmodule(frame.f_back)
            if module is not None:
                name = module.__name__
            else:
                name = "__main__"
        else:
            name = "__main__"
    
    return logging.getLogger(name)


def setup_logger(
    level: Optional[Union[int, str]] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    use_colors: bool = True,
    config_file: Optional[str] = None,
) -> None:
    """Set up the logger with the specified configuration.

    Args:
        level: The log level to use (DEBUG, INFO, etc.)
        log_file: Path to a file to log to (in addition to console)
        log_format: The format string for log messages
        date_format: The format string for timestamps
        use_colors: Whether to use colored output in the console
        config_file: Path to a JSON logging configuration file
    """
    # If a config file is provided, use it
    if config_file and os.path.exists(config_file):
        configure_logging(config_file)
        return

    # Determine the log level
    if level is None:
        env = os.environ.get("ENVIRONMENT", "development").lower()
        level = LOG_LEVELS.get(env, logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Set formatter
    log_format = log_format or DEFAULT_LOG_FORMAT
    date_format = date_format or DEFAULT_DATE_FORMAT
    
    if use_colors:
        formatter = ColoredFormatter(log_format, date_format, use_colors=use_colors)
    else:
        formatter = logging.Formatter(log_format, date_format)
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        # Ensure the directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Log the setup
    root_logger.debug(f"Logging configured with level: {logging.getLevelName(level)}")
    if log_file:
        root_logger.debug(f"Log file: {log_file}")


def configure_logging(config_file: str) -> None:
    """Configure logging using a configuration file.

    Args:
        config_file: Path to a JSON logging configuration file
    """
    if not os.path.exists(config_file):
        print(f"Warning: Logging configuration file {config_file} not found.")
        return

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Process any environment variables in the config
        process_config_env_vars(config)
        
        # Apply the configuration
        logging.config.dictConfig(config)
        
        logger = logging.getLogger(__name__)
        logger.debug(f"Logging configured from file: {config_file}")
    except Exception as e:
        print(f"Error configuring logging from {config_file}: {e}")
        # Fall back to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )


def process_config_env_vars(config: Dict[str, Any]) -> None:
    """Process environment variables in the logging configuration.

    Replaces strings like "${ENV_VAR}" with the value of the environment variable.

    Args:
        config: The logging configuration dictionary
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, (dict, list)):
                process_config_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is not None:
                    config[key] = env_value
    elif isinstance(config, list):
        for i, item in enumerate(config):
            if isinstance(item, (dict, list)):
                process_config_env_vars(item)
            elif isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                env_var = item[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is not None:
                    config[i] = env_value


def get_log_file_path(log_dir: Optional[str] = None, prefix: str = "app") -> str:
    """Generate a timestamped log file path.

    Args:
        log_dir: Directory to store log files (defaults to 'logs')
        prefix: Prefix for the log file name

    Returns:
        Path to the log file
    """
    if log_dir is None:
        # Use logs directory in the project root
        project_root = Path(__file__).parent.parent.parent
        log_dir = os.path.join(project_root, "logs")
    
    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate a timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(log_dir, f"{prefix}_{timestamp}.log")


def log_function_call(func):
    """Decorator to log function calls with arguments and return values.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        # Format the arguments for logging
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"Calling {func_name}({signature})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned {repr(result)}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func_name}: {str(e)}")
            raise
    
    return wrapper


@contextmanager
def log_execution_time(logger: Optional[logging.Logger] = None, operation: str = "Operation"):
    """Context manager to log the execution time of a block of code.

    Args:
        logger: The logger to use (if None, a logger will be created)
        operation: Description of the operation being timed

    Yields:
        None
    """
    if logger is None:
        # Get the logger for the calling module
        frame = inspect.currentframe()
        if frame is not None and frame.f_back is not None:
            module = inspect.getmodule(frame.f_back)
            if module is not None:
                logger = logging.getLogger(module.__name__)
            else:
                logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(__name__)
    
    start_time = datetime.datetime.now()
    logger.debug(f"Starting {operation}")
    
    try:
        yield
    finally:
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        logger.debug(f"Completed {operation} in {duration.total_seconds():.3f} seconds")


def set_log_level(level: Union[int, str], logger_name: Optional[str] = None) -> None:
    """Set the log level for a specific logger or the root logger.

    Args:
        level: The log level to set (DEBUG, INFO, etc.)
        logger_name: The name of the logger to configure (None for root logger)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Also update the level of all handlers
    for handler in logger.handlers:
        handler.setLevel(level)


def create_rotating_file_handler(
    log_file: str,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    level: int = logging.DEBUG,
    formatter: Optional[logging.Formatter] = None,
) -> logging.Handler:
    """Create a rotating file handler for logging.

    Args:
        log_file: Path to the log file
        max_bytes: Maximum size of the log file before rotation
        backup_count: Number of backup files to keep
        level: Log level for the handler
        formatter: Formatter for log messages

    Returns:
        A configured rotating file handler
    """
    from logging.handlers import RotatingFileHandler
    
    # Ensure the directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setLevel(level)
    
    if formatter is None:
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
    
    handler.setFormatter(formatter)
    return handler


def add_file_handler(
    logger: logging.Logger,
    log_file: str,
    level: Optional[int] = None,
    formatter: Optional[logging.Formatter] = None,
) -> logging.FileHandler:
    """Add a file handler to a logger.

    Args:
        logger: The logger to add the handler to
        log_file: Path to the log file
        level: Log level for the handler (defaults to logger's level)
        formatter: Formatter for log messages

    Returns:
        The created file handler
    """
    # Ensure the directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    handler = logging.FileHandler(log_file)
    
    if level is None:
        level = logger.level
    
    handler.setLevel(level)
    
    if formatter is None:
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return handler


def get_all_loggers() -> Dict[str, logging.Logger]:
    """Get all loggers that have been created.

    Returns:
        A dictionary mapping logger names to logger instances
    """
    return logging.root.manager.loggerDict


def disable_logging_for_tests() -> None:
    """Disable logging when running tests to reduce noise."""
    if "pytest" in sys.modules or "unittest" in sys.modules:
        logging.getLogger().setLevel(logging.CRITICAL)


def enable_debug_logging() -> None:
    """Enable debug logging for all loggers."""
    logging.getLogger().setLevel(logging.DEBUG)
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.DEBUG)


def get_log_level_name(level: int) -> str:
    """Get the name of a log level.

    Args:
        level: The numeric log level

    Returns:
        The name of the log level (DEBUG, INFO, etc.)
    """
    return logging.getLevelName(level)


def redirect_logs_to_file(log_file: str) -> None:
    """Redirect all logs to a file.

    Args:
        log_file: Path to the log file
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def redirect_logs_to_stream(stream: TextIO) -> None:
    """Redirect all logs to a stream.

    Args:
        stream: The stream to write logs to (e.g., sys.stdout)
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add stream handler
    stream_handler = logging.StreamHandler(stream)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)


# Initialize logging with default settings
setup_logger()

if __name__ == "__main__":
    # Example usage
    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Example with execution time logging
    with log_execution_time(logger, "example operation"):
        # Simulate some work
        import time
        time.sleep(1)
    
    # Example with function call logging
    @log_function_call
    def example_function(a, b, c=None):
        return a + b
    
    result = example_function(1, 2, c="test")
    print(f"Result: {result}")