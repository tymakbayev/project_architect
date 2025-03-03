# Contributing to Project Architect

Thank you for your interest in contributing to Project Architect! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment Setup](#development-environment-setup)
  - [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Commit Guidelines](#commit-guidelines)
  - [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
  - [Python Style Guide](#python-style-guide)
  - [Documentation](#documentation)
  - [Type Hints](#type-hints)
  - [Testing](#testing)
- [Feature Requests and Bug Reports](#feature-requests-and-bug-reports)
- [Review Process](#review-process)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We expect all contributors to be respectful, inclusive, and considerate of others.

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/project_architect.git
   cd project_architect
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   # or
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Project Structure

Familiarize yourself with the project structure:

```
project_architect/
├── src/                    # Source code
│   ├── core/               # Core functionality
│   ├── clients/            # API clients
│   ├── interfaces/         # User interfaces (CLI, API)
│   ├── output/             # Output generation
│   ├── templates/          # Templates for code generation
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── examples/               # Example usage
└── config/                 # Configuration files
```

## Development Workflow

### Branching Strategy

We follow a simplified Git flow:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features or improvements
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent fixes for production
- `release/*`: Release preparation

### Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or correcting tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(analyzer): add support for React project type detection

- Implements heuristics for React project identification
- Adds relevant tests
- Updates documentation

Closes #123
```

### Pull Request Process

1. **Create a branch** from `develop` for your changes
2. **Make your changes** and commit them following our commit guidelines
3. **Write or update tests** as needed
4. **Update documentation** to reflect your changes
5. **Run tests locally** to ensure they pass
6. **Submit a pull request** to the `develop` branch
7. **Address review feedback** if requested

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- Use 4 spaces for indentation
- Maximum line length is 100 characters
- Use double quotes for strings unless single quotes avoid backslashes
- Use f-strings for string formatting when appropriate

We use the following tools to enforce code quality:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking

You can run all checks with:
```bash
make lint
```

### Documentation

- All modules, classes, and functions should have docstrings following the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Update README.md and other documentation when adding features
- Keep API documentation up-to-date

### Type Hints

- Use type hints for all function parameters and return values
- Use `typing` module for complex types
- Run `mypy` to check type consistency

Example:
```python
from typing import Dict, List, Optional

def process_data(input_data: List[Dict[str, str]], 
                 config: Optional[Dict[str, any]] = None) -> Dict[str, any]:
    """Process the input data according to configuration.
    
    Args:
        input_data: List of data dictionaries to process
        config: Optional configuration dictionary
        
    Returns:
        Processed data as a dictionary
    """
    # Implementation
```

### Testing

- Write unit tests for all new functionality
- Maintain or improve code coverage
- Use pytest fixtures for test setup
- Mock external services in unit tests

Run tests with:
```bash
make test
```

## Feature Requests and Bug Reports

- Use GitHub Issues to report bugs or request features
- For bugs, provide a minimal reproducible example
- For features, describe the use case and expected behavior
- Tag issues appropriately (bug, enhancement, etc.)

## Review Process

Pull requests are reviewed by maintainers based on:
- Code quality and adherence to style guide
- Test coverage and passing tests
- Documentation completeness
- Feature completeness and correctness

Reviewers may request changes before merging.

## Release Process

1. Create a `release/vX.Y.Z` branch from `develop`
2. Update version numbers and CHANGELOG.md
3. Perform final testing and validation
4. Submit a PR to merge into `main`
5. After merging, tag the release in GitHub
6. Publish to PyPI if applicable

## Community

- Join our [Discord server](https://discord.example.com/project-architect) for discussions
- Follow the project on Twitter [@ProjectArchitect](https://twitter.com/example)
- Sign up for our newsletter at [project-architect.example.com](https://example.com)

---

Thank you for contributing to Project Architect! Your efforts help make this project better for everyone.