#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of Project Architect.

This script demonstrates how to use the Project Architect to analyze a project description
and generate a complete project structure with code files.

Usage:
    python example_usage.py

This example shows:
1. Basic usage with a simple project description
2. Advanced usage with custom configuration
3. Using the API programmatically
4. Saving and loading generated projects
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import Project Architect components
from src.project_generator import ProjectGenerator
from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.core.project_structure_generator import ProjectStructureGenerator
from src.core.code_generator import CodeGenerator
from src.core.dependency_manager import DependencyManager
from src.clients.anthropic_client import AnthropicClient
from src.output.project_output_manager import ProjectOutputManager
from src.utils.logger import setup_logger
from src.config import Config

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


def load_config(config_path: str = "examples/example_config.json") -> Dict[str, Any]:
    """Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        raise


def basic_usage_example() -> None:
    """Demonstrate basic usage of Project Architect with minimal configuration."""
    logger.info("Running basic usage example...")
    
    # Load API key from environment variable or .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set. Please set it in .env file or environment.")
        return
    
    # Create a project generator with default settings
    generator = ProjectGenerator(anthropic_api_key=api_key)
    
    # Define a simple project
    project_name = "simple_todo_app"
    project_description = """
    A simple todo application with a command-line interface.
    Users should be able to add, remove, list, and mark tasks as complete.
    The application should store tasks in a JSON file.
    """
    
    # Generate the project
    output_dir = Path("./generated_projects/simple_todo_app")
    result = generator.generate_project(
        project_name=project_name,
        project_description=project_description,
        output_dir=output_dir
    )
    
    logger.info(f"Project generated at: {output_dir}")
    logger.info(f"Project type: {result['project_type']}")
    logger.info(f"Generated {len(result['files'])} files")


def advanced_usage_example() -> None:
    """Demonstrate advanced usage with custom configuration."""
    logger.info("Running advanced usage example...")
    
    # Load configuration from file
    config_data = load_config()
    config = Config(config_data)
    
    # Create a project generator with custom configuration
    generator = ProjectGenerator(config=config)
    
    # Define a more complex project
    project_name = "e_commerce_platform"
    project_description = """
    A full-stack e-commerce platform with the following features:
    - User authentication and authorization
    - Product catalog with categories and search
    - Shopping cart and checkout process
    - Order management and history
    - Admin panel for product and order management
    - Payment integration with Stripe
    - Responsive design for mobile and desktop
    
    The application should use React for the frontend, Node.js with Express for the backend,
    and MongoDB for the database. It should follow best practices for security, performance,
    and code organization.
    """
    
    # Additional context to guide generation
    additional_context = {
        "target_audience": "small to medium businesses",
        "deployment_target": "AWS",
        "security_requirements": "GDPR compliance, secure payment processing",
        "performance_goals": "Page load under 2 seconds, mobile-optimized",
        "design_preferences": "Material Design, dark mode support"
    }
    
    # Generate the project with custom options
    output_dir = Path("./generated_projects/e_commerce_platform")
    result = generator.generate_project(
        project_name=project_name,
        project_description=project_description,
        output_dir=output_dir,
        additional_context=additional_context,
        create_zip=True,
        include_tests=True,
        include_documentation=True
    )
    
    logger.info(f"Project generated at: {output_dir}")
    logger.info(f"Project type: {result['project_type']}")
    logger.info(f"Architecture components: {len(result['architecture'].components)}")
    logger.info(f"Generated {len(result['files'])} files")
    logger.info(f"Zip archive created: {output_dir}.zip")


def component_level_usage_example() -> None:
    """Demonstrate usage of individual components for more control."""
    logger.info("Running component-level usage example...")
    
    # Load API key from environment variable or .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set. Please set it in .env file or environment.")
        return
    
    # Create individual components
    anthropic_client = AnthropicClient(api_key)
    project_analyzer = ProjectAnalyzer(anthropic_client=anthropic_client)
    architecture_generator = ArchitectureGenerator(anthropic_client=anthropic_client)
    structure_generator = ProjectStructureGenerator(anthropic_client=anthropic_client)
    code_generator = CodeGenerator(anthropic_client=anthropic_client)
    dependency_manager = DependencyManager(anthropic_client=anthropic_client)
    output_manager = ProjectOutputManager()
    
    # Project details
    project_name = "data_analysis_toolkit"
    project_description = """
    A Python library for data analysis and visualization.
    The library should provide tools for loading data from various sources (CSV, Excel, SQL),
    cleaning and transforming data, performing statistical analysis, and creating visualizations.
    It should be easy to use, well-documented, and have good test coverage.
    """
    
    # Step 1: Analyze project to determine type and requirements
    project_type, requirements = project_analyzer.analyze_project(
        project_name=project_name,
        project_description=project_description
    )
    logger.info(f"Project type: {project_type}")
    logger.info(f"Requirements: {requirements}")
    
    # Step 2: Generate architecture plan
    architecture_plan = architecture_generator.generate_architecture(
        project_type=project_type,
        project_name=project_name,
        project_description=project_description,
        requirements=requirements
    )
    logger.info(f"Architecture components: {len(architecture_plan.components)}")
    
    # Step 3: Generate project structure
    project_structure = structure_generator.generate_structure(
        project_type=project_type,
        project_name=project_name,
        architecture_plan=architecture_plan
    )
    logger.info(f"Structure nodes: {len(project_structure.get_all_nodes())}")
    
    # Step 4: Generate dependencies
    dependencies = dependency_manager.generate_dependencies(
        project_type=project_type,
        architecture_plan=architecture_plan
    )
    logger.info(f"Dependencies: {dependencies}")
    
    # Step 5: Generate code files
    code_files = code_generator.generate_code(
        project_type=project_type,
        project_name=project_name,
        project_description=project_description,
        architecture_plan=architecture_plan,
        project_structure=project_structure,
        dependencies=dependencies
    )
    logger.info(f"Generated {len(code_files)} code files")
    
    # Step 6: Output the project
    output_dir = Path("./generated_projects/data_analysis_toolkit")
    output_manager.output_project(
        project_name=project_name,
        project_structure=project_structure,
        code_files=code_files,
        output_dir=output_dir,
        create_zip=True
    )
    logger.info(f"Project output to: {output_dir}")


def interactive_example() -> None:
    """Demonstrate interactive usage with the CLI."""
    logger.info("Running interactive example...")
    logger.info("This example would normally use the CLI interactively.")
    logger.info("To use the CLI interactively, run: python -m src.interfaces.cli")
    
    # For demonstration purposes, we'll show how to programmatically use the CLI
    from src.interfaces.cli import CLI
    
    # Load API key from environment variable or .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set. Please set it in .env file or environment.")
        return
    
    # Create CLI instance
    cli = CLI(anthropic_api_key=api_key)
    
    # This would normally be interactive, but we'll simulate it
    project_info = {
        "name": "blog_platform",
        "description": "A simple blogging platform where users can create, edit, and publish articles.",
        "output_dir": "./generated_projects/blog_platform"
    }
    
    # Generate the project (in a real interactive session, this would be done through CLI prompts)
    cli.generate_project(
        project_name=project_info["name"],
        project_description=project_info["description"],
        output_dir=project_info["output_dir"]
    )
    
    logger.info(f"Project generated at: {project_info['output_dir']}")


def api_example() -> None:
    """Demonstrate usage of the REST API."""
    logger.info("Running API example...")
    logger.info("This example shows how to use the REST API programmatically.")
    logger.info("To start the API server, run: python -m src.interfaces.api")
    
    import requests
    
    # API server should be running at this address
    api_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code != 200:
            logger.error(f"API server is not responding correctly. Status code: {response.status_code}")
            logger.info("Please start the API server with: python -m src.interfaces.api")
            return
    except requests.ConnectionError:
        logger.error("Could not connect to API server")
        logger.info("Please start the API server with: python -m src.interfaces.api")
        return
    
    # Create a project through the API
    project_data = {
        "project_name": "weather_app",
        "project_description": "A web application that shows weather forecasts for different locations. Users can search for cities and save favorite locations.",
        "additional_context": {
            "target_platforms": ["web", "mobile"],
            "preferred_technologies": ["React", "Node.js"]
        }
    }
    
    # Send request to generate project
    response = requests.post(f"{api_url}/projects/generate", json=project_data)
    
    if response.status_code == 202:
        # Asynchronous generation started
        task_id = response.json().get("task_id")
        logger.info(f"Project generation started. Task ID: {task_id}")
        
        # Poll for results
        logger.info("Polling for results (in a real application, you might use websockets or callbacks)...")
        
        # Simulate polling (in a real application, this would be more robust)
        import time
        for _ in range(10):
            time.sleep(5)
            status_response = requests.get(f"{api_url}/tasks/{task_id}")
            
            if status_response.status_code == 200:
                task_status = status_response.json()
                
                if task_status["status"] == "completed":
                    logger.info("Project generation completed!")
                    logger.info(f"Download URL: {task_status['result']['download_url']}")
                    break
                elif task_status["status"] == "failed":
                    logger.error(f"Project generation failed: {task_status.get('error')}")
                    break
                else:
                    logger.info(f"Current status: {task_status['status']}")
            else:
                logger.error(f"Failed to get task status: {status_response.status_code}")
    else:
        logger.error(f"Failed to start project generation: {response.status_code}")
        logger.error(response.text)


def main() -> None:
    """Run all examples."""
    logger.info("Project Architect Example Usage")
    logger.info("==============================")
    
    # Check if API key is available
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY environment variable not set.")
        logger.warning("Please set it in .env file or environment to run the examples.")
        logger.warning("Example: ANTHROPIC_API_KEY=sk-ant-api03-...")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs("./generated_projects", exist_ok=True)
    
    try:
        # Run examples
        basic_usage_example()
        print("\n" + "-" * 50 + "\n")
        
        advanced_usage_example()
        print("\n" + "-" * 50 + "\n")
        
        component_level_usage_example()
        print("\n" + "-" * 50 + "\n")
        
        interactive_example()
        print("\n" + "-" * 50 + "\n")
        
        # API example requires the API server to be running
        # Uncomment to run this example if the API server is running
        # api_example()
        
        logger.info("All examples completed successfully!")
        logger.info("Check the ./generated_projects directory for the generated projects.")
    
    except Exception as e:
        logger.exception(f"An error occurred while running examples: {e}")


if __name__ == "__main__":
    main()