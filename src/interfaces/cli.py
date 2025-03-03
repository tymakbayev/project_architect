#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command Line Interface for Project Generator.

This module provides a CLI for interacting with the project generation system.
It handles argument parsing and orchestrates the project generation workflow.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any

import typer
from rich.console import Console
from rich.logging import RichHandler

from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.project_generator import ProjectGenerator
from src.models.project_type import ProjectType
from src.models.architecture_plan import ArchitecturePlan
from src.config.config import Config


# Create Typer app instance
app = typer.Typer(
    name="project-architect",
    help="Generate project architectures and code from descriptions",
    add_completion=False
)

# Set up rich console for better output
console = Console()


class CLI:
    """Command Line Interface for the Project Generator application.

    This class handles user input via command line arguments and orchestrates
    the project generation workflow.
    """

    def __init__(self, anthropic_api_key: Optional[str] = None) -> None:
        """Initialize the CLI with required components.
        
        Args:
            anthropic_api_key: Optional API key for Anthropic
        """
        # Create a Config object
        config = Config()
        if anthropic_api_key:
            config.anthropic_api_key = anthropic_api_key
            
        self.project_analyzer = ProjectAnalyzer(anthropic_api_key)
        self.architecture_generator = ArchitectureGenerator(anthropic_api_key)
        self.project_generator = ProjectGenerator()
        self.logger = logging.getLogger(__name__)

    def parse_arguments(self) -> Dict[str, Any]:
        """Parse command line arguments.

        Returns:
            Dict[str, Any]: Dictionary containing parsed arguments
        """
        # Note: This method is kept for backward compatibility
        # Actual argument parsing is now handled by Typer
        pass

    def get_project_description(self, description: Optional[str] = None, description_file: Optional[str] = None) -> str:
        """Get project description from arguments or file.
        
        Args:
            description: Project description text
            description_file: Path to file containing description
            
        Returns:
            str: Project description text
            
        Raises:
            FileNotFoundError: If description file doesn't exist
            ValueError: If neither description nor description_file is provided
        """
        if description:
            return description
        
        if description_file:
            try:
                with open(description_file, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                self.logger.error(f"Error: Description file '{description_file}' not found")
                raise
                
        raise ValueError("Either description or description_file must be provided")

    def generate_project(
        self, 
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        description_file: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a project from a description.
        
        Args:
            project_name: Name of the project
            description: Text description of the project
            description_file: Path to file containing description
            output_dir: Directory to output the generated project
            
        Returns:
            Dictionary containing result of project generation
            
        Raises:
            ValueError: If neither description nor description_file is provided
        """
        try:
            # Get project description
            project_desc = self.get_project_description(description, description_file)
            
            # Derive project name from output directory if not provided
            if not project_name and output_dir:
                project_name = Path(output_dir).name
            elif not project_name:
                project_name = "generated_project"
                
            # Generate project
            self.logger.info(f"Generating project '{project_name}' from description")
            result = self.project_generator.generate_project(project_desc, output_dir)
            
            self.logger.info(f"Project generation completed: {result['status']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating project: {str(e)}")
            raise

    def run_cli(self) -> None:
        """Run the CLI application workflow."""
        # This method is kept for backward compatibility
        # The workflow is now handled by the Typer app
        pass


# Typer command handlers
@app.command()
def generate(
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description text"),
    description_file: Optional[Path] = typer.Option(None, "--description-file", "-f", help="Path to file containing project description"),
    output_dir: Path = typer.Option("./generated_project", "--output-dir", "-o", help="Directory to output the generated project"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)"),
    project_name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name (defaults to directory name)")
):
    """Generate a complete project from a text description."""
    cli = CLI(api_key)
    
    # Check for required parameters
    if not description and not description_file:
        console.print("[bold red]Error:[/bold red] Either --description or --description-file must be provided")
        raise typer.Exit(code=1)
    
    try:
        result = cli.generate_project(
            project_name=project_name,
            description=description,
            description_file=description_file,
            output_dir=str(output_dir)
        )
        
        # Display result
        console.print(f"[bold green]Project generation completed![/bold green]")
        console.print(f"  Project type: [cyan]{result.get('project_type', 'unknown')}[/cyan]")
        console.print(f"  Files generated: [cyan]{len(result.get('files', []))}[/cyan]")
        console.print(f"  Output directory: [cyan]{result.get('output_dir', output_dir)}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def analyze(
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description text"),
    description_file: Optional[Path] = typer.Option(None, "--description-file", "-f", help="Path to file containing project description"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)")
):
    """Analyze a project description to determine type and requirements."""
    cli = CLI(api_key)
    
    # Check for required parameters
    if not description and not description_file:
        console.print("[bold red]Error:[/bold red] Either --description or --description-file must be provided")
        raise typer.Exit(code=1)
    
    try:
        # Get project description
        project_desc = cli.get_project_description(description, description_file)
        
        # Analyze project
        project_type = cli.project_analyzer.analyze_project_description(project_desc)
        requirements = cli.project_analyzer.extract_key_requirements(project_desc)
        
        # Display results
        console.print(f"[bold green]Project Analysis:[/bold green]")
        console.print(f"  Project type: [cyan]{project_type.name}[/cyan]")
        console.print(f"  Description: {project_type.description}")
        
        console.print("\n[bold green]Requirements:[/bold green]")
        for i, req in enumerate(requirements, 1):
            console.print(f"  {i}. {req}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def architecture(
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description text"),
    description_file: Optional[Path] = typer.Option(None, "--description-file", "-f", help="Path to file containing project description"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="File to output the generated architecture"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)")
):
    """Generate an architecture plan for a project description."""
    cli = CLI(api_key)
    
    # Check for required parameters
    if not description and not description_file:
        console.print("[bold red]Error:[/bold red] Either --description or --description-file must be provided")
        raise typer.Exit(code=1)
    
    try:
        # Get project description
        project_desc = cli.get_project_description(description, description_file)
        
        # Analyze project
        project_type = cli.project_analyzer.analyze_project_description(project_desc)
        requirements = cli.project_analyzer.extract_key_requirements(project_desc)
        
        # Generate architecture
        architecture_plan = cli.architecture_generator.generate_architecture(project_type, requirements)
        
        # Display results
        console.print(f"[bold green]Architecture Plan:[/bold green]")
        console.print(f"  Project type: [cyan]{project_type.name}[/cyan]")
        
        console.print("\n[bold green]Components:[/bold green]")
        for comp in architecture_plan.components:
            console.print(f"  [cyan]{comp.name}[/cyan]")
            console.print(f"    Purpose: {comp.purpose}")
            console.print(f"    Technologies: {comp.technologies}")
        
        console.print("\n[bold green]Dependencies:[/bold green]")
        for dep in architecture_plan.dependencies:
            console.print(f"  [cyan]{dep.source}[/cyan] → [cyan]{dep.target}[/cyan] ({dep.type})")
            
        # Save to file if requested
        if output_file:
            import json
            with open(output_file, "w") as f:
                json.dump(architecture_plan.to_dict(), f, indent=2)
            console.print(f"\nArchitecture plan saved to [cyan]{output_file}[/cyan]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    # Set up logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    # Run the Typer app
    app()
