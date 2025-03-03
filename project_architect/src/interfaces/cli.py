#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command Line Interface for Project Generator.

This module provides a CLI for interacting with the project generation system.
It handles argument parsing and orchestrates the project generation workflow.
"""

import argparse
import sys
from typing import Dict, Optional, List, Any

from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.models.project_type import ProjectType
from src.models.architecture_plan import ArchitecturePlan


class CLI:
    """Command Line Interface for the Project Generator application.

    This class handles user input via command line arguments and orchestrates
    the project generation workflow.
    """

    def __init__(self) -> None:
        """Initialize the CLI with required components."""
        self.project_analyzer = ProjectAnalyzer()
        self.architecture_generator = ArchitectureGenerator()

    def parse_arguments(self) -> Dict[str, Any]:
        """Parse command line arguments.

        Returns:
            Dict[str, Any]: Dictionary containing parsed arguments
        """
        parser = argparse.ArgumentParser(
            description="Generate project architecture and code based on description"
        )
        parser.add_argument(
            "--description", 
            type=str,
            help="Project description text"
        )
        parser.add_argument(
            "--description-file",
            type=str,
            help="Path to file containing project description"
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default="./generated_project",
            help="Directory to output generated project files"
        )
        parser.add_argument(
            "--api-key",
            type=str,
            help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)"
        )
        
        args = parser.parse_args()
        
        # Validate that either description or description-file is provided
        if not args.description and not args.description_file:
            parser.error("Either --description or --description-file must be provided")
            
        return vars(args)

    def get_project_description(self, args: Dict[str, Any]) -> str:
        """Get project description from arguments or file.
        
        Args:
            args: Dictionary of parsed arguments
            
        Returns:
            str: Project description text
            
        Raises:
            FileNotFoundError: If description file doesn't exist
        """
        if args.get("description"):
            return args["description"]
        
        if args.get("description_file"):
            try:
                with open(args["description_file"], "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                print(f"Error: Description file '{args['description_file']}' not found")
                sys.exit(1)
                
        return ""

    def run_cli(self) -> None:
        """Run the CLI application workflow.
        
        This method orchestrates the entire project generation process:
        1. Parse command line arguments
        2. Analyze project description
        3. Generate architecture plan
        4. Generate project structure and code
        """
        args = self.parse_arguments()
        project_description = self.get_project_description(args)
        
        print("Analyzing project description...")
        project_type = self.project_analyzer.analyze_project_description(project_description)
        requirements = self.project_analyzer.extract_key_requirements(project_description)
        
        print(f"Detected project type: {project_type.name}")
        print(f"Extracted {len(requirements)} key requirements")
        
        print("Generating architecture plan...")
        architecture_plan = self.architecture_generator.generate_architecture(
            project_type, requirements
        )
        
        print("Architecture plan generated successfully!")
        print(f"Components: {len(architecture_plan.components)}")
        
        # Here we would call the project generator to create the actual files
        # project_generator.generate_project(architecture_plan, args["output_dir"])
        
        print(f"Project would be generated at: {args['output_dir']}")


def main() -> None:
    """Entry point for the CLI application."""
    cli = CLI()
    cli.run_cli()


if __name__ == "__main__":
    main()
