# Project Architect - Architecture Documentation

## Overview

Project Architect is an application that leverages Anthropic's Claude API (and GitHub API when available) to analyze project descriptions, determine project types, and generate comprehensive project scaffolding including architecture plans, project structures, source code files, and dependencies. The system ensures consistency across various technology stacks such as Python, React, Node.js, and others.

This document outlines the architectural design of the Project Architect system, including its components, interactions, data flows, and design decisions.

## System Architecture

Project Architect follows a modular, layered architecture with clear separation of concerns. The system is organized into the following main layers:

1. **Interface Layer** - Provides access points to the system (CLI, API)
2. **Core Layer** - Contains the main business logic for project generation
3. **Client Layer** - Handles communication with external services
4. **Output Layer** - Manages the generation of output files and directories
5. **Template Layer** - Provides templates for different technology stacks
6. **Utility Layer** - Offers common functionality used across the system

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INTERFACE LAYER                             │
│                                                                     │
│  ┌──────────────┐                              ┌──────────────┐     │
│  │      CLI     │                              │   REST API   │     │
│  └──────┬───────┘                              └──────┬───────┘     │
│         │                                             │             │
└─────────┼─────────────────────────────────────────────┼─────────────┘
          │                                             │
          ▼                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            CORE LAYER                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │    Project   │  │ Architecture │  │      Project Structure   │   │
│  │   Analyzer   │──▶  Generator   │──▶       Generator          │   │
│  └──────────────┘  └──────────────┘  └────────────┬─────────────┘   │
│                                                    │                 │
│                                                    ▼                 │
│                                      ┌──────────────┐  ┌───────────┐ │
│                                      │     Code     │  │ Dependency│ │
│                                      │   Generator  │◀─┤  Manager  │ │
│                                      └──────┬───────┘  └───────────┘ │
│                                             │                        │
└─────────────────────────────────────────────┼────────────────────────┘
                                              │
          ┌─────────────────────────────────┐ │ ┌─────────────────────┐
          │           CLIENT LAYER          │ │ │    OUTPUT LAYER     │
          │                                 │ │ │                     │
          │  ┌────────────┐ ┌────────────┐ │ │ │  ┌────────────────┐ │
          │  │ Anthropic  │ │   GitHub   │ │ └─┼─▶│ Project Output │ │
          │  │   Client   │ │   Client   │ │   │  │    Manager     │ │
          │  └────────────┘ └────────────┘ │   │  └────────────────┘ │
          └─────────────────────────────────┘   └─────────────────────┘
                                              
          ┌─────────────────────────────────┐   ┌─────────────────────┐
          │        TEMPLATE LAYER           │   │    UTILITY LAYER    │
          │                                 │   │                     │
          │  ┌────────┐ ┌────────┐ ┌─────┐ │   │  ┌───────┐ ┌──────┐ │
          │  │ Python │ │ React  │ │Node │ │   │  │Logger │ │Helpers│ │
          │  │Templates│ │Templates│ │Templ│ │   │  │       │ │      │ │
          │  └────────┘ └────────┘ └─────┘ │   │  └───────┘ └──────┘ │
          └─────────────────────────────────┘   └─────────────────────┘
```

## Component Descriptions

### Interface Layer

#### CLI (`src/interfaces/cli.py`)

The Command Line Interface provides a user-friendly way to interact with Project Architect from the terminal. It uses the Typer library to create a structured CLI with commands for project generation, analysis, and configuration.

Key features:
- Project generation from description
- Interactive mode for guided project creation
- Configuration management
- Output formatting options (JSON, YAML, etc.)

#### REST API (`src/interfaces/api.py`)

The REST API provides programmatic access to Project Architect functionality. Built with FastAPI, it offers endpoints for project analysis, architecture generation, and complete project generation.

Key features:
- RESTful API design
- Authentication and rate limiting
- Swagger/OpenAPI documentation
- Asynchronous request handling

### Core Layer

#### Project Analyzer (`src/core/project_analyzer.py`)

Analyzes project descriptions to determine project type, requirements, and key features. This component uses Claude's AI capabilities to understand natural language descriptions and extract structured information.

Key responsibilities:
- Determine project type and subtype
- Extract functional and non-functional requirements
- Identify key technologies and frameworks
- Assess project complexity and scope

#### Architecture Generator (`src/core/architecture_generator.py`)

Generates high-level architecture plans based on project type and requirements. Creates component diagrams, data flows, and architectural patterns appropriate for the project.

Key responsibilities:
- Design system components and their relationships
- Define data flows between components
- Select appropriate architectural patterns
- Create visual architecture diagrams

#### Project Structure Generator (`src/core/project_structure_generator.py`)

Creates the directory and file structure for the project based on the architecture plan and project type. Ensures the structure follows best practices for the selected technology stack.

Key responsibilities:
- Generate directory hierarchy
- Define file organization
- Apply technology-specific structure patterns
- Ensure consistency with architecture plan

#### Code Generator (`src/core/code_generator.py`)

Generates actual code files based on the project structure, architecture, and requirements. Uses templates and AI-generated code to create functional implementations.

Key responsibilities:
- Generate code for individual files
- Ensure code consistency across files
- Apply coding standards and best practices
- Generate documentation within code

#### Dependency Manager (`src/core/dependency_manager.py`)

Identifies and manages project dependencies based on the project type and requirements. Creates dependency specifications for package managers.

Key responsibilities:
- Identify required libraries and frameworks
- Determine compatible versions
- Generate dependency files (requirements.txt, package.json, etc.)
- Handle dependency conflicts

### Client Layer

#### Anthropic Client (`src/clients/anthropic_client.py`)

Handles communication with Anthropic's Claude API for AI-powered analysis and generation. Manages API requests, response parsing, and error handling.

Key responsibilities:
- Authenticate with Anthropic API
- Format prompts for Claude
- Parse and process Claude responses
- Handle rate limiting and errors

#### GitHub Client (`src/clients/github_client.py`)

Interfaces with GitHub API to gather information about repositories, code patterns, and best practices. Can also be used to create repositories for generated projects.

Key responsibilities:
- Authenticate with GitHub API
- Search repositories for reference
- Analyze code patterns and structures
- Create and populate repositories

### Output Layer

#### Project Output Manager (`src/output/project_output_manager.py`)

Manages the creation of output files and directories based on the generated project structure. Handles file writing, formatting, and packaging.

Key responsibilities:
- Create directory structure
- Write code files
- Generate documentation files
- Package project for distribution

### Template Layer

#### Technology Templates (`src/templates/*.py`)

Provides templates and patterns for different technology stacks. These templates guide the generation of code files and project structures for specific technologies.

Key components:
- Python Templates (`python_templates.py`)
- React Templates (`react_templates.py`)
- Node Templates (`node_templates.py`)

### Utility Layer

#### Logger (`src/utils/logger.py`)

Provides logging functionality throughout the application with configurable levels and outputs.

#### Validators (`src/utils/validators.py`)

Contains validation functions for input data, ensuring that project descriptions, configurations, and other inputs meet expected formats and constraints.

#### Helpers (`src/utils/helpers.py`)

General utility functions used across the application, including string processing, file operations, and data transformations.

## Data Models

Project Architect uses several key data models to represent the state of project generation:

### Project Type (`src/models/project_type.py`)

Represents the type and characteristics of a project:
```python
class ProjectType:
    type: str  # e.g., "web_application", "cli_tool", "library"
    subtype: str  # e.g., "fullstack", "frontend", "backend"
    confidence: float  # Confidence score for the classification
    technologies: List[str]  # Recommended technologies
```

### Architecture Plan (`src/models/architecture_plan.py`)

Represents the high-level architecture of the project:
```python
class Component:
    name: str
    description: str
    responsibilities: List[str]
    technologies: List[str]

class Dependency:
    source: str  # Component name
    target: str  # Component name
    type: str  # e.g., "uses", "extends", "implements"
    description: str

class DataFlow:
    source: str  # Component name
    target: str  # Component name
    data_description: str
    protocol: Optional[str]  # e.g., "HTTP", "WebSocket"

class ArchitecturePlan:
    components: List[Component]
    dependencies: List[Dependency]
    data_flows: List[DataFlow]
    patterns: List[str]  # Architectural patterns used
    diagram: Optional[str]  # Textual representation of architecture diagram
```

### Project Structure (`src/models/project_structure.py`)

Represents the directory and file structure of the project:
```python
class FileNode:
    path: str
    description: str
    content_template: Optional[str]
    dependencies: List[str]  # Other files this file depends on

class DirectoryNode:
    path: str
    description: str
    children: List[Union[FileNode, 'DirectoryNode']]

class ProjectStructure:
    root: DirectoryNode
    technology_stack: List[str]
```

### Code File (`src/models/code_file.py`)

Represents a generated code file:
```python
class CodeFile:
    path: str
    content: str
    language: str
    description: str
    dependencies: List[str]  # Other files this file depends on
```

### Dependency Specification (`src/models/dependency_spec.py`)

Represents project dependencies:
```python
class DependencySpec:
    name: str
    version: str
    type: str  # e.g., "production", "development", "optional"
    purpose: str  # Description of why this dependency is needed
```

## Data Flow

1. **Project Description Input**
   - User provides project description via CLI or API
   - Description is validated and preprocessed

2. **Project Analysis**
   - Project Analyzer sends description to Claude API
   - Claude analyzes description and returns project type and requirements
   - Project Analyzer structures this information into a ProjectType object

3. **Architecture Generation**
   - Architecture Generator takes ProjectType and requirements
   - Generates an ArchitecturePlan with components, dependencies, and data flows
   - May consult GitHub for reference architectures if enabled

4. **Project Structure Generation**
   - Project Structure Generator takes ArchitecturePlan
   - Creates a ProjectStructure with directories and files
   - Applies technology-specific templates from Template Layer

5. **Dependency Management**
   - Dependency Manager analyzes requirements and structure
   - Identifies necessary dependencies
   - Creates dependency specifications

6. **Code Generation**
   - Code Generator takes ProjectStructure and ArchitecturePlan
   - Generates code for each file in the structure
   - Uses templates and Claude API for code generation
   - Ensures consistency between files

7. **Output Generation**
   - Project Output Manager takes generated code and structure
   - Creates directories and writes files to disk
   - Generates additional files like README, license, etc.

## Design Decisions

### AI-First Approach

Project Architect is designed with an AI-first approach, leveraging Claude's capabilities for understanding project requirements and generating appropriate code. This allows for a more natural interface where users can describe projects in plain language rather than through complex configuration.

### Modular Architecture

The system uses a modular architecture with clear separation of concerns. This allows for:
- Easy extension with new technology stacks
- Replacement of individual components
- Testing of components in isolation
- Parallel development of different system parts

### Template-Based Generation

While AI is used for analysis and custom code generation, the system also relies on templates for common patterns and structures. This hybrid approach ensures:
- Consistency with best practices
- Reliability for standard components
- Customization for project-specific needs
- Better performance by reducing AI calls for standard code

### Progressive Enhancement

The system follows a progressive enhancement approach, where basic functionality works with minimal configuration, but additional features are available for more complex needs:
- Basic: Generate from description only
- Enhanced: Add custom templates and configurations
- Advanced: Integrate with GitHub, customize generation process

### Technology Agnosticism

While the system supports specific technology stacks, the core architecture is technology-agnostic, allowing for:
- Support for multiple programming languages and frameworks
- Consistent approach across different technologies
- Easy addition of new technology stacks

## Deployment Architecture

Project Architect can be deployed in multiple ways:

### Local Installation

Users can install Project Architect locally as a Python package and use it via CLI or as a library in their own Python code.

### API Service

Project Architect can be deployed as a REST API service, either:
- Self-hosted on premises
- Cloud-hosted (AWS, GCP, Azure)
- Containerized with Docker

### Containerized Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Host                            │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │  API Container  │      │   Worker Container(s)       │   │
│  │                 │      │                             │   │
│  │  - FastAPI      │◀────▶│  - Project Generation Logic │   │
│  │  - Uvicorn      │      │  - Claude API Client        │   │
│  │  - Rate Limiting│      │  - GitHub API Client        │   │
│  └────────┬────────┘      └─────────────────────────────┘   │
│           │                                                 │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────┐
│  Load Balancer      │
│  (e.g., Nginx)      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     Clients         │
│  - Web Browsers     │
│  - API Consumers    │
│  - CI/CD Pipelines  │
└─────────────────────┘
```

## Security Considerations

### API Key Management

Project Architect requires API keys for Anthropic and optionally GitHub. These keys are sensitive and must be properly secured:
- Keys are stored in environment variables or secure configuration
- Keys are never logged or exposed in responses
- Different deployment environments use different keys

### Input Validation

All user inputs are validated to prevent:
- Injection attacks
- Resource exhaustion
- Unexpected behavior

### Rate Limiting

The system implements rate limiting to:
- Prevent abuse
- Manage costs for API calls
- Ensure fair usage among users

### Output Sanitization

Generated code is analyzed to ensure it doesn't contain:
- Malicious code patterns
- Sensitive information
- Security vulnerabilities

## Testing Strategy

Project Architect employs a comprehensive testing strategy:

### Unit Tests

Unit tests for individual components, focusing on:
- Core logic validation
- Edge case handling
- Error handling

### Integration Tests

Integration tests for component interactions:
- Core pipeline integration
- API endpoint functionality
- CLI command execution

### Mock Testing

Mock testing for external dependencies:
- Claude API responses
- GitHub API interactions
- File system operations

### Snapshot Testing

Snapshot testing for generated outputs:
- Code file content
- Project structures
- Configuration files

## Performance Considerations

### Caching

The system implements caching for:
- Claude API responses
- GitHub API responses
- Generated templates and patterns

### Parallel Processing

Where possible, the system uses parallel processing for:
- Generating multiple code files
- Processing independent components
- Handling multiple requests

### Resource Management

The system carefully manages resources for:
- API rate limits
- Memory usage during generation
- Disk space for output

## Extension Points

Project Architect is designed to be extensible in several ways:

### New Technology Stacks

Adding support for new technologies involves:
1. Creating new template modules in the Template Layer
2. Adding technology-specific logic to the Project Structure Generator
3. Updating the Project Analyzer to recognize the new technology

### Custom Templates

Users can provide custom templates for:
- Project structures
- Code files
- Documentation

### Plugin System

A plugin system allows for:
- Custom analyzers
- Additional output formats
- Integration with other tools and services

## Future Directions

### Multi-Model Support

Expanding beyond Claude to support:
- Other LLMs (GPT-4, Llama, etc.)
- Specialized code generation models
- Fine-tuned models for specific technologies

### Interactive Refinement

Adding capabilities for:
- Interactive project refinement
- Iterative generation with feedback
- Visual editing of architecture and structure

### Continuous Integration

Deeper integration with development workflows:
- CI/CD pipeline generation
- Testing framework setup
- Deployment configuration

### Learning from Usage

Implementing systems to:
- Learn from user feedback
- Improve templates based on usage patterns
- Adapt to emerging best practices

## Conclusion

Project Architect's architecture is designed to be modular, extensible, and AI-driven, allowing for the generation of high-quality project scaffolding across multiple technology stacks. By separating concerns into distinct layers and components, the system can evolve and improve while maintaining a consistent interface for users.

The combination of AI-powered analysis and generation with template-based approaches provides both flexibility and reliability, enabling users to quickly bootstrap projects that follow best practices and meet their specific requirements.