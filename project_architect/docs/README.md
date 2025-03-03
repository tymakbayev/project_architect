# Project Architect Documentation

## Overview

Project Architect is a powerful tool that leverages Anthropic's Claude API and GitHub integration to automatically generate complete project scaffolding based on natural language descriptions. This documentation provides comprehensive information about the system architecture, usage guides, and development resources.

## Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Quick Start Guide](#quick-start-guide)
- [Core Concepts](#core-concepts)
  - [Project Analysis](#project-analysis)
  - [Architecture Generation](#architecture-generation)
  - [Project Structure Generation](#project-structure-generation)
  - [Code Generation](#code-generation)
  - [Dependency Management](#dependency-management)
- [Usage Guides](#usage-guides)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [REST API](#rest-api)
- [Technology Stack Support](#technology-stack-support)
  - [Python Projects](#python-projects)
  - [React Projects](#react-projects)
  - [Node.js Projects](#node-js-projects)
  - [Adding New Technology Support](#adding-new-technology-support)
- [Advanced Features](#advanced-features)
  - [Custom Templates](#custom-templates)
  - [GitHub Integration](#github-integration)
  - [Project Customization](#project-customization)
- [Development](#development)
  - [Architecture Overview](#architecture-overview)
  - [Component Descriptions](#component-descriptions)
  - [Adding New Features](#adding-new-features)
  - [Testing](#testing)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging](#debugging)
  - [Getting Support](#getting-support)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Installation

Project Architect can be installed using pip:

```bash
pip install project-architect
```

For development installation:

```bash
git clone https://github.com/yourusername/project_architect.git
cd project_architect
pip install -e .
```

### Configuration

Before using Project Architect, you need to configure your API keys and other settings:

1. Create a `.env` file in your project root (or copy and modify the provided `.env.example`):

```
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_API_TOKEN=your_github_token  # Optional, for GitHub integration
LOG_LEVEL=INFO
```

2. Alternatively, you can set these environment variables directly in your system.

3. For more advanced configuration, you can modify the JSON files in the `config/` directory:
   - `default_config.json`: General application settings
   - `logging_config.json`: Logging configuration

### Quick Start Guide

Generate a new project using the CLI:

```bash
project-architect generate --name "my_awesome_project" --description "A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality."
```

Or using the Python API:

```python
from project_architect import ProjectGenerator

generator = ProjectGenerator()
project = generator.generate_project(
    name="my_awesome_project",
    description="A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality."
)

# Output the project to a directory
project.output("./output_directory")
```

## Core Concepts

### Project Analysis

Project Architect begins by analyzing your project description using Claude's AI capabilities. The system:

1. Identifies the type of project (web app, CLI tool, library, etc.)
2. Extracts key requirements and features
3. Determines the most appropriate technology stack
4. Identifies architectural patterns that match your needs

The `ProjectAnalyzer` component handles this process, producing a structured representation of your project's requirements that guides the subsequent generation steps.

### Architecture Generation

Based on the analysis, the `ArchitectureGenerator` creates a comprehensive architectural plan that includes:

- System components and their responsibilities
- Component interactions and data flows
- External dependencies and integrations
- Deployment considerations

The architecture is designed to follow best practices for the identified project type and technology stack.

### Project Structure Generation

The `ProjectStructureGenerator` transforms the architectural plan into a concrete directory and file structure. This includes:

- Directory hierarchy
- Empty file placeholders with appropriate extensions
- Configuration files
- Documentation structure

The structure follows conventional patterns for the selected technology stack to ensure familiarity and maintainability.

### Code Generation

The `CodeGenerator` populates the file structure with actual code, including:

- Boilerplate and scaffolding code
- Implementation of core functionality
- Configuration settings
- Documentation comments

The generated code is designed to be functional, following best practices and coding standards for the selected technology.

### Dependency Management

The `DependencyManager` identifies and configures the appropriate dependencies for your project, including:

- Core libraries and frameworks
- Development tools
- Testing frameworks
- Deployment utilities

Dependencies are specified in the appropriate format for your technology stack (requirements.txt, package.json, etc.).

## Usage Guides

### Command Line Interface

The CLI provides a convenient way to use Project Architect from the terminal:

```bash
# Basic usage
project-architect generate --name "project_name" --description "Project description"

# Specify output directory
project-architect generate --name "project_name" --description "Project description" --output "./my_projects"

# Provide additional context
project-architect generate --name "project_name" --description "Project description" --context '{"preferred_technologies": ["python", "react"], "deployment": "aws"}'

# List available project types
project-architect list-types

# Get help
project-architect --help
```

For more details, see the CLI documentation in the `src/interfaces/cli.py` file.

### Python API

You can integrate Project Architect into your Python applications:

```python
from project_architect import ProjectGenerator
from project_architect.core import ProjectAnalyzer, ArchitectureGenerator
from project_architect.models import ProjectType

# Use the high-level generator
generator = ProjectGenerator()
project = generator.generate_project(
    name="my_project",
    description="A data processing pipeline with web dashboard",
    additional_context={
        "preferred_technologies": ["python", "fastapi"],
        "deployment": "kubernetes"
    }
)

# Output the project
project.output("./output_directory")

# Or use individual components
analyzer = ProjectAnalyzer()
project_type = analyzer.analyze_project_description(
    "A data processing pipeline with web dashboard"
)

architecture_generator = ArchitectureGenerator()
architecture = architecture_generator.generate_architecture(
    project_type=project_type,
    project_name="my_project"
)

# Work with the architecture...
```

### REST API

Project Architect provides a REST API for integration with web applications or other services:

1. Start the API server:

```bash
project-architect serve --host 0.0.0.0 --port 8000
```

2. Use the API endpoints:

```bash
# Generate a project
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my_api_project",
    "description": "A RESTful API for managing inventory",
    "additional_context": {
      "preferred_technologies": ["python", "fastapi"]
    }
  }'

# Get project types
curl http://localhost:8000/v1/project-types
```

For complete API documentation, see the [API Reference](../API.md) or access the Swagger UI at `http://localhost:8000/docs` when the server is running.

## Technology Stack Support

### Python Projects

Project Architect supports various Python project types:

- Web applications (Flask, FastAPI, Django)
- CLI tools (Click, Typer)
- Data processing pipelines
- Libraries and packages
- API clients
- Machine learning applications

The generated Python projects include:

- Proper package structure
- Virtual environment setup
- Testing framework (pytest)
- Documentation (Sphinx)
- CI/CD configuration
- Dependency management

### React Projects

For React applications, Project Architect generates:

- Component structure (functional components with hooks)
- State management setup (Context API, Redux)
- Routing configuration
- API integration
- Styling setup (CSS modules, styled-components, or Tailwind)
- Testing framework (Jest, React Testing Library)
- Build configuration

### Node.js Projects

Node.js project support includes:

- Express/Koa/Fastify API servers
- GraphQL APIs
- Serverless functions
- CLI tools
- Libraries and packages
- Full-stack applications

### Adding New Technology Support

To add support for a new technology stack:

1. Create a new template module in `src/templates/`
2. Implement the required template functions and patterns
3. Update the `ProjectAnalyzer` to recognize projects that should use this technology
4. Add appropriate code generation logic in `CodeGenerator`
5. Update dependency management for the new technology

See the developer documentation for detailed instructions.

## Advanced Features

### Custom Templates

You can create custom templates for your projects:

1. Create a templates directory in your project:

```bash
mkdir -p my_templates/python
```

2. Add template files with Jinja2 syntax:

```python
# my_templates/python/main.py.j2
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""{{ project_name }} - {{ project_description }}"""

def main():
    """Main entry point for {{ project_name }}."""
    print("Welcome to {{ project_name }}!")
    
    # TODO: Implement your application logic here
    
if __name__ == "__main__":
    main()
```

3. Use your templates with the CLI:

```bash
project-architect generate --name "my_project" --description "My awesome project" --templates-dir "./my_templates"
```

### GitHub Integration

Project Architect can integrate with GitHub to:

- Create a new repository for your project
- Push the generated code
- Set up GitHub Actions workflows
- Configure branch protection rules

To use GitHub integration:

```bash
project-architect generate --name "my_project" --description "Project description" --github-repo "username/repo-name"
```

Make sure your `GITHUB_API_TOKEN` is configured with appropriate permissions.

### Project Customization

You can customize the generation process:

```python
from project_architect import ProjectGenerator

generator = ProjectGenerator()
project = generator.generate_project(
    name="custom_project",
    description="A customized web application",
    additional_context={
        "preferred_technologies": ["python", "fastapi"],
        "custom_components": [
            {
                "name": "authentication",
                "type": "service",
                "description": "JWT-based authentication service"
            },
            {
                "name": "reporting",
                "type": "module",
                "description": "PDF report generation module"
            }
        ],
        "database": "postgresql",
        "deployment": "docker"
    }
)
```

## Development

### Architecture Overview

Project Architect follows a modular architecture:

- **Core Components**: Handle the main generation logic
  - `ProjectAnalyzer`: Analyzes project descriptions
  - `ArchitectureGenerator`: Creates architectural plans
  - `ProjectStructureGenerator`: Generates directory and file structures
  - `CodeGenerator`: Produces actual code
  - `DependencyManager`: Manages project dependencies

- **Clients**: Handle external service communication
  - `AnthropicClient`: Communicates with Claude API
  - `GithubClient`: Interacts with GitHub API

- **Interfaces**: Provide user interaction methods
  - `CLI`: Command-line interface
  - `API`: REST API server

- **Templates**: Contain patterns for different technologies
  - `python_templates`: Templates for Python projects
  - `react_templates`: Templates for React projects
  - `node_templates`: Templates for Node.js projects

- **Output**: Manages the generation output
  - `ProjectOutputManager`: Handles file and directory creation

- **Utils**: Provide common utilities
  - `logger`: Logging setup
  - `validators`: Input validation
  - `helpers`: Common helper functions

### Component Descriptions

#### ProjectAnalyzer

The `ProjectAnalyzer` uses Claude to analyze project descriptions and determine:

- Project type and subtype
- Core requirements
- Recommended technologies
- Architectural considerations

It transforms natural language descriptions into structured data that guides the generation process.

#### ArchitectureGenerator

The `ArchitectureGenerator` creates a comprehensive architectural plan based on the project analysis. It defines:

- System components
- Component interactions
- Data flows
- External integrations
- Deployment architecture

The generated architecture follows best practices for the identified project type.

#### ProjectStructureGenerator

The `ProjectStructureGenerator` transforms the architectural plan into a concrete file and directory structure, including:

- Directory hierarchy
- File placeholders
- Configuration files
- Documentation structure

#### CodeGenerator

The `CodeGenerator` populates the file structure with actual code, including:

- Implementation of core functionality
- Configuration settings
- Documentation
- Tests

#### DependencyManager

The `DependencyManager` identifies and configures appropriate dependencies for the project, including:

- Core libraries
- Development tools
- Testing frameworks
- Deployment utilities

### Adding New Features

To add new features to Project Architect:

1. Identify the component that should contain the feature
2. Implement the feature following the existing patterns
3. Add appropriate tests
4. Update documentation
5. Submit a pull request

See the [CONTRIBUTING.md](../CONTRIBUTING.md) file for detailed contribution guidelines.

### Testing

Project Architect uses pytest for testing:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

When adding new features, make sure to:

1. Add unit tests for individual components
2. Add integration tests for component interactions
3. Ensure all tests pass before submitting changes

## Troubleshooting

### Common Issues

#### API Key Configuration

If you encounter authentication errors:

1. Verify your API keys are correctly set in the `.env` file or environment variables
2. Check that the API keys have the necessary permissions
3. Ensure the API keys are not expired

#### Generation Quality Issues

If the generated code doesn't meet expectations:

1. Try providing more detailed project descriptions
2. Add specific requirements in the `additional_context` parameter
3. Use custom templates for more control over the output

#### Performance Issues

If generation is slow:

1. Check your network connection to the Anthropic API
2. Consider breaking down large projects into smaller components
3. Use the `--cache` option to enable caching of API responses

### Debugging

Enable debug logging for more detailed information:

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or when running the CLI
project-architect generate --name "project" --description "description" --log-level DEBUG
```

### Getting Support

If you encounter issues not covered in this documentation:

1. Check the [GitHub Issues](https://github.com/yourusername/project_architect/issues) for similar problems
2. Create a new issue with detailed information about your problem
3. Join our community Discord server for real-time support

## API Reference

For detailed API documentation, see the [API Reference](../API.md) document.

## Contributing

We welcome contributions to Project Architect! See the [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines.

## License

Project Architect is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.