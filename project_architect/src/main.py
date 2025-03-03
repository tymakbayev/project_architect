#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for the Project Architect application.

This module initializes the application, sets up logging, loads configuration,
and provides entry points for both CLI and API interfaces.
"""

import os
import sys
import logging
import argparse
from typing import Optional, Dict, Any, List
import dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from src.utils.logger import setup_logger
from src.config import Config
from src.project_generator import ProjectGenerator
from src.interfaces.cli import CLI

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Project Architect: Generate project architecture, structure, and code from descriptions"
    )
    
    # Main command options
    parser.add_argument(
        "--api", 
        action="store_true", 
        help="Start the REST API server"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port for the API server (default: 8000)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host for the API server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    
    # CLI mode arguments (when not using API)
    parser.add_argument(
        "--description", 
        type=str, 
        help="Project description text"
    )
    parser.add_argument(
        "--description-file", 
        type=str, 
        help="File containing project description"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        help="Directory to output the generated project"
    )
    
    return parser.parse_args()


def init_app() -> Dict[str, Any]:
    """
    Initialize the application components.

    Returns:
        Dict[str, Any]: Dictionary containing initialized components.
    """
    # Load environment variables from .env file if it exists
    dotenv.load_dotenv()
    
    # Setup logging
    logger = setup_logger()
    logger.info("Initializing Project Architect application")
    
    # Load configuration
    config = Config()
    try:
        config_path = os.environ.get('CONFIG_PATH', 'config/default_config.json')
        config.load_config(config_path)
        logger.info(f"Configuration loaded from {config_path}")
    except Exception as e:
        logger.warning(f"Failed to load configuration: {e}. Using default values.")
    
    # Initialize project generator
    project_generator = ProjectGenerator()
    
    # Initialize CLI
    cli = CLI(project_generator)
    
    return {
        "logger": logger,
        "config": config,
        "project_generator": project_generator,
        "cli": cli
    }


def start_api_server(host: str, port: int, debug: bool = False) -> None:
    """
    Start the FastAPI server.

    Args:
        host (str): Host address to bind the server.
        port (int): Port number to bind the server.
        debug (bool, optional): Enable debug mode. Defaults to False.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting API server at {host}:{port}")
    
    try:
        import uvicorn
        from src.interfaces.api import app as api_app
        
        # Start the API server
        uvicorn.run(
            "src.interfaces.api:app",
            host=host,
            port=port,
            reload=debug,
            log_level="debug" if debug else "info"
        )
    except ImportError:
        logger.error("Failed to start API server: uvicorn package is not installed. Please install it with 'pip install uvicorn'")
        sys.exit(1)


def run_cli_mode(
    app_components: Dict[str, Any],
    description: Optional[str] = None,
    description_file: Optional[str] = None,
    output_dir: Optional[str] = None
) -> None:
    """
    Run the application in CLI mode.

    Args:
        app_components (Dict[str, Any]): Dictionary containing initialized app components.
        description (Optional[str], optional): Project description text. Defaults to None.
        description_file (Optional[str], optional): File containing project description. Defaults to None.
        output_dir (Optional[str], optional): Directory to output the generated project. Defaults to None.
    """
    logger = app_components["logger"]
    cli = app_components["cli"]
    
    # Get project description
    if description_file:
        try:
            with open(description_file, 'r') as f:
                description = f.read()
            logger.info(f"Loaded project description from {description_file}")
        except Exception as e:
            logger.error(f"Failed to read description file: {e}")
            sys.exit(1)
    
    if not description:
        logger.error("No project description provided. Use --description or --description-file")
        sys.exit(1)
    
    # Generate project
    try:
        result = cli.generate_project(description, output_dir)
        logger.info(f"Project generation completed. Result: {result}")
    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize application components
    app_components = init_app()
    logger = app_components["logger"]
    
    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Override config path if provided
    if args.config:
        try:
            app_components["config"].load_config(args.config)
            logger.info(f"Configuration loaded from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {args.config}: {e}")
            sys.exit(1)
    
    # Determine run mode
    if args.api:
        # API mode
        start_api_server(args.host, args.port, args.debug)
    else:
        # CLI mode
        run_cli_mode(
            app_components,
            description=args.description,
            description_file=args.description_file,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()