# Project Architect

A powerful tool that uses Anthropic's Claude API (and optionally GitHub) to analyze project descriptions, determine project types, and generate complete project scaffolding including architecture plans, project structures, source code files, and dependencies - all while ensuring consistency across various technology stacks (Python, React, Node.js, and more).

![Project Architect](https://img.shields.io/badge/Project-Architect-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

- **Project Analysis**: Automatically determines the project type from a text description
- **Architecture Generation**: Creates detailed architecture plans based on project requirements
- **Code Generation**: Produces working starter code for all project files
- **Multi-Technology Support**: Generates projects for Python, React, Node.js, and more
- **Dependency Management**: Identifies and configures appropriate dependencies
- **Consistent Output**: Ensures all generated components work together seamlessly
- **Multiple Interfaces**: Use via CLI, API, or integrate into your own applications

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Web API](#web-api)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
  - [Setting Up Development Environment](#setting-up-development-environment)
  - [Running Tests](#running-tests)
  - [Docker Development](#docker-development)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude access)
- GitHub API token (optional, for GitHub integration)

### Using pip

```bash
pip install project-architect
```

### From source

```bash
git clone https://github.com/yourusername/project_architect.git
cd project_architect
pip install -e .
```

### Using Docker

```bash
docker pull yourusername/project_architect
# or build locally
docker build -t project_architect .
```

## 🚀 Quick Start

1. Set up your API keys:

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export GITHUB_TOKEN="your_github_token"  # Optional

# Or create a .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" > .env
echo "GITHUB_TOKEN=your_github_token" >> .env  # Optional
```

2. Generate a project from a description:

```bash
# Using the CLI
project-architect --description "Create a FastAPI backend with SQLAlchemy ORM, user authentication, and PostgreSQL database" --output-dir ./my_fastapi_project
```

## 📝 Usage Examples

### Command Line Interface

Generate a project using a text description:

```bash
project-architect --description "A React frontend with Redux state management and Material UI components that connects to a REST API"
```

Generate a project using a description file:

```bash
project-architect --description-file project_description.txt --output-dir ./generated_project
```

Get help on available commands:

```bash
project-architect --help
```

### Python API

```python
from src.project_generator import ProjectGenerator

# Initialize the generator
generator = ProjectGenerator()

# Generate a project from a description
project_description = """
A Django web application with user authentication, 
PostgreSQL database, and REST API endpoints for a 
task management system.
"""

# Generate the project
generator.generate_project(
    description=project_description,
    output_dir="./my_django_project"
)
```

### Web API

Start the API server:

```bash
uvicorn src.interfaces.api:app --reload
```

Make a request to generate a project:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A Flask web application with SQLAlchemy, user authentication, and a React frontend",
    "output_format": "zip"
  }' \
  --output generated_project.zip
```

## ⚙️ Configuration

Project Architect can be configured using environment variables, a `.env` file, or through the configuration files in the `config/` directory.

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude access
- `GITHUB_TOKEN`: GitHub API token (optional)
- `LOG_LEVEL`: Logging level (default: INFO)
- `OUTPUT_DIR`: Default output directory for generated projects

### Configuration Files

- `config/default_config.json`: Default configuration settings
- `config/logging_config.json`: Logging configuration

Example custom configuration:

```json
{
  "api": {
    "anthropic": {
      "model": "claude-3-opus-20240229",
      "max_tokens": 4000,
      "temperature": 0.2
    },
    "github": {
      "use_github": true,
      "search_repositories": true
    }
  },
  "generation": {
    "include_tests": true,
    "include_documentation": true,
    "code_style": "pep8"
  },
  "output": {
    "create_zip": true,
    "cleanup_after_zip": false
  }
}
```

## 📂 Project Structure

```
project_architect/
├── src/                     # Source code
│   ├── core/                # Core functionality
│   │   ├── project_analyzer.py
│   │   ├── architecture_generator.py
│   │   ├── project_structure_generator.py
│   │   ├── code_generator.py
│   │   └── dependency_manager.py
│   ├── clients/             # API clients
│   │   ├── anthropic_client.py
│   │   ├── github_client.py
│   │   └── base_client.py
│   ├── interfaces/          # User interfaces
│   │   ├── cli.py
│   │   └── api.py
│   ├── output/              # Output management
│   │   └── project_output_manager.py
│   ├── templates/           # Code templates
│   │   ├── python_templates.py
│   │   ├── react_templates.py
│   │   └── node_templates.py
│   ├── utils/               # Utility functions
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── helpers.py
│   ├── config.py            # Configuration handling
│   ├── main.py              # Application entry point
│   └── project_generator.py # Main generator class
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Test configuration
├── config/                  # Configuration files
│   ├── default_config.json
│   └── logging_config.json
├── docs/                    # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── README.md
├── examples/                # Example usage
│   ├── example_usage.py
│   └── example_config.json
├── .env.example             # Example environment variables
├── setup.py                 # Package setup
├── pyproject.toml           # Project metadata
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── Makefile                 # Development commands
├── LICENSE                  # License information
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

## 📚 API Documentation

### ProjectGenerator

The main class for generating projects.

```python
from src.project_generator import ProjectGenerator

generator = ProjectGenerator()
generator.generate_project(
    description="Project description",
    output_dir="./output",
    config_path=None  # Optional custom config
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `generate_project(description, output_dir, config_path=None)` | Generate a complete project |
| `analyze_project(description)` | Only analyze the project type and requirements |
| `generate_architecture(description, project_type)` | Generate architecture plan only |

### ProjectAnalyzer

Analyzes project descriptions to determine project type and requirements.

```python
from src.core.project_analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer()
project_type = analyzer.analyze_project_description("A Flask web app with SQLAlchemy")
requirements = analyzer.extract_key_requirements("A Flask web app with SQLAlchemy")
```

### ArchitectureGenerator

Generates architecture plans based on project type and requirements.

```python
from src.core.architecture_generator import ArchitectureGenerator

generator = ArchitectureGenerator()
architecture = generator.generate_architecture(project_type, requirements)
```

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Generate a complete project |
| `/analyze` | POST | Analyze a project description |
| `/architecture` | POST | Generate architecture plan only |

For complete API documentation, see [docs/API.md](docs/API.md).

## 🛠️ Development

### Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/project_architect.git
cd project_architect
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks:

```bash
pre-commit install
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

Run specific test categories:

```bash
pytest tests/unit/  # Unit tests only
pytest tests/integration/  # Integration tests only
```

### Docker Development

Build the Docker image:

```bash
docker build -t project_architect .
```

Run the container:

```bash
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key project_architect
```

Using Docker Compose:

```bash
docker-compose up
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Anthropic](https://www.anthropic.com/) for the Claude API
- All contributors who have helped shape this project

---

Built with ❤️ by [Your Name/Organization]

For questions or support, please open an issue or contact [your-email@example.com].