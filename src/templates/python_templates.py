#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python Templates Module.

This module provides templates for generating Python project structures, files, and code.
It includes templates for different Python project types (standard packages, web applications,
data science projects, etc.) and common patterns used in Python development.

The templates are designed to be flexible and customizable, allowing for generation of
idiomatic Python code that follows best practices and conventions (PEP 8, etc.).
"""

import os
import re
import textwrap
from typing import Dict, Any, List, Optional, Union, Callable, Set
import logging
from pathlib import Path
from datetime import datetime
import inspect
import importlib
import pkgutil
import jinja2

from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()


class PythonTemplates:
    """
    Provides templates for Python projects.
    
    This class contains static methods that generate code and configuration files
    for Python projects, following best practices and conventions.
    """

    @staticmethod
    def setup_py(context: Dict[str, Any]) -> str:
        """
        Generate a setup.py file for a Python package.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Short description of the project
                - author: Author's name
                - author_email: Author's email
                - version: Project version
                - dependencies: List of dependencies
                - python_requires: Python version requirement
                - classifiers: List of PyPI classifiers
                - entry_points: Dictionary of entry points
        
        Returns:
            String containing the setup.py content
        """
        project_name = context.get('project_name', 'python_project')
        description = context.get('description', 'A Python project')
        author = context.get('author', 'Author')
        author_email = context.get('author_email', 'author@example.com')
        version = context.get('version', '0.1.0')
        dependencies = context.get('dependencies', [])
        python_requires = context.get('python_requires', '>=3.7')
        classifiers = context.get('classifiers', [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ])
        entry_points = context.get('entry_points', {})
        
        # Format dependencies list
        deps_str = ',\n        '.join([f"'{dep}'" for dep in dependencies])
        
        # Format classifiers list
        classifiers_str = ',\n        '.join([f"'{c}'" for c in classifiers])
        
        # Format entry points
        entry_points_str = ''
        if entry_points:
            entry_points_str = 'entry_points={\n'
            for group, points in entry_points.items():
                entry_points_str += f"        '{group}': [\n"
                for name, path in points.items():
                    entry_points_str += f"            '{name}={path}',\n"
                entry_points_str += "        ],\n"
            entry_points_str += '    },'
        
        return f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='{project_name}',
    version='{version}',
    description='{description}',
    author='{author}',
    author_email='{author_email}',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='{python_requires}',
    install_requires=[
        {deps_str}
    ],
    classifiers=[
        {classifiers_str}
    ],
    {entry_points_str}
)
"""

    @staticmethod
    def pyproject_toml(context: Dict[str, Any]) -> str:
        """
        Generate a pyproject.toml file for a Python package.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Short description of the project
                - author: Author's name
                - author_email: Author's email
                - version: Project version
                - dependencies: List of dependencies
                - python_requires: Python version requirement
                - dev_dependencies: List of development dependencies
                - build_system: Build system configuration
        
        Returns:
            String containing the pyproject.toml content
        """
        project_name = context.get('project_name', 'python_project')
        description = context.get('description', 'A Python project')
        author = context.get('author', 'Author')
        author_email = context.get('author_email', 'author@example.com')
        version = context.get('version', '0.1.0')
        dependencies = context.get('dependencies', [])
        python_requires = context.get('python_requires', '>=3.7')
        dev_dependencies = context.get('dev_dependencies', [
            'pytest',
            'pytest-cov',
            'black',
            'isort',
            'mypy',
            'flake8'
        ])
        
        # Format dependencies
        deps_str = '\n'.join([f'    "{dep}",' for dep in dependencies])
        dev_deps_str = '\n'.join([f'    "{dep}",' for dep in dev_dependencies])
        
        return f"""[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[tool.poetry]
name = "{project_name}"
version = "{version}"
description = "{description}"
authors = ["{author} <{author_email}>"]
readme = "README.md"
repository = "https://github.com/username/{project_name}"
license = "MIT"

[tool.poetry.dependencies]
python = "{python_requires}"
{deps_str}

[tool.poetry.dev-dependencies]
{dev_deps_str}

[tool.black]
line-length = 88
target-version = ["py37", "py38", "py39", "py310"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3

[tool.mypy]
python_version = "3.7"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
"""

    @staticmethod
    def init_py(context: Dict[str, Any]) -> str:
        """
        Generate an __init__.py file for a Python package.
        
        Args:
            context: Dictionary containing package information:
                - package_name: Name of the package
                - description: Short description of the package
                - version: Package version
                - imports: List of modules to import and expose
                - all_list: List of names to include in __all__
        
        Returns:
            String containing the __init__.py content
        """
        package_name = context.get('package_name', 'package')
        description = context.get('description', 'A Python package')
        version = context.get('version', '0.1.0')
        imports = context.get('imports', [])
        all_list = context.get('all_list', [])
        
        # Format imports
        imports_str = '\n'.join(imports)
        
        # Format __all__ list
        if all_list:
            all_str = '__all__ = [\n    ' + ',\n    '.join([f"'{name}'" for name in all_list]) + '\n]'
        else:
            all_str = '__all__ = []'
        
        return f'''"""
{package_name}

{description}
"""

__version__ = "{version}"

{imports_str}

{all_str}
'''

    @staticmethod
    def readme_md(context: Dict[str, Any]) -> str:
        """
        Generate a README.md file for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Description of the project
                - installation: Installation instructions
                - usage: Usage examples
                - features: List of features
                - license: License information
        
        Returns:
            String containing the README.md content
        """
        project_name = context.get('project_name', 'Python Project')
        description = context.get('description', 'A Python project')
        installation = context.get('installation', 
                                  'pip install project_name')
        usage = context.get('usage', 'import project_name')
        features = context.get('features', [])
        license_info = context.get('license', 'MIT')
        
        # Format features list
        features_str = ''
        if features:
            features_str = '## Features\n\n'
            for feature in features:
                features_str += f'- {feature}\n'
        
        return f"""# {project_name}

{description}

## Installation

```bash
{installation}
```

## Usage

```python
{usage}
```

{features_str}

## License

{license_info}
"""

    @staticmethod
    def gitignore(context: Dict[str, Any]) -> str:
        """
        Generate a .gitignore file for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - additional_patterns: Additional patterns to ignore
        
        Returns:
            String containing the .gitignore content
        """
        additional_patterns = context.get('additional_patterns', [])
        
        patterns = [
            # Python
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "MANIFEST",
            
            # Unit test / coverage reports
            "htmlcov/",
            ".tox/",
            ".nox/",
            ".coverage",
            ".coverage.*",
            ".cache",
            "nosetests.xml",
            "coverage.xml",
            "*.cover",
            ".hypothesis/",
            ".pytest_cache/",
            
            # Environments
            ".env",
            ".venv",
            "env/",
            "venv/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
            
            # IDE
            ".idea/",
            ".vscode/",
            "*.swp",
            "*.swo",
            
            # OS specific
            ".DS_Store",
            "Thumbs.db"
        ]
        
        # Add additional patterns
        patterns.extend(additional_patterns)
        
        return '\n'.join(patterns)

    @staticmethod
    def license_mit(context: Dict[str, Any]) -> str:
        """
        Generate an MIT license file.
        
        Args:
            context: Dictionary containing license information:
                - year: Copyright year
                - author: Copyright holder name
        
        Returns:
            String containing the MIT license content
        """
        year = context.get('year', datetime.now().year)
        author = context.get('author', 'Author')
        
        return f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    @staticmethod
    def dockerfile(context: Dict[str, Any]) -> str:
        """
        Generate a Dockerfile for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - python_version: Python version to use
                - dependencies: List of system dependencies
                - port: Port to expose
                - cmd: Command to run
        
        Returns:
            String containing the Dockerfile content
        """
        project_name = context.get('project_name', 'python_project')
        python_version = context.get('python_version', '3.9')
        dependencies = context.get('dependencies', [])
        port = context.get('port', '8000')
        cmd = context.get('cmd', 'python -m project_name')
        
        # Format dependencies
        deps_str = ''
        if dependencies:
            deps_str = 'RUN apt-get update && apt-get install -y \\\n    '
            deps_str += ' \\\n    '.join(dependencies)
            deps_str += ' \\\n    && rm -rf /var/lib/apt/lists/*\n'
        
        return f"""FROM python:{python_version}-slim

WORKDIR /app

{deps_str}
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE {port}

CMD {cmd}
"""

    @staticmethod
    def docker_compose_yml(context: Dict[str, Any]) -> str:
        """
        Generate a docker-compose.yml file for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - services: Dictionary of services to include
                - volumes: List of volumes to mount
                - networks: List of networks to create
        
        Returns:
            String containing the docker-compose.yml content
        """
        project_name = context.get('project_name', 'python_project')
        services = context.get('services', {
            'app': {
                'build': '.',
                'ports': ['8000:8000'],
                'volumes': ['.:/app'],
                'environment': ['DEBUG=True'],
                'depends_on': ['db']
            },
            'db': {
                'image': 'postgres:13',
                'volumes': ['postgres_data:/var/lib/postgresql/data'],
                'environment': [
                    'POSTGRES_PASSWORD=postgres',
                    'POSTGRES_USER=postgres',
                    'POSTGRES_DB=postgres'
                ]
            }
        })
        
        # Format services
        services_str = ''
        for name, config in services.items():
            services_str += f'  {name}:\n'
            
            for key, value in config.items():
                if isinstance(value, list):
                    services_str += f'    {key}:\n'
                    for item in value:
                        services_str += f'      - {item}\n'
                elif isinstance(value, dict):
                    services_str += f'    {key}:\n'
                    for k, v in value.items():
                        services_str += f'      {k}: {v}\n'
                else:
                    services_str += f'    {key}: {value}\n'
        
        # Format volumes
        volumes = context.get('volumes', ['postgres_data:'])
        volumes_str = ''
        if volumes:
            volumes_str = 'volumes:\n'
            for volume in volumes:
                if ':' in volume:
                    name, config = volume.split(':', 1)
                    volumes_str += f'  {name}:{config}\n'
                else:
                    volumes_str += f'  {volume}:\n'
        
        # Format networks
        networks = context.get('networks', [])
        networks_str = ''
        if networks:
            networks_str = 'networks:\n'
            for network in networks:
                if isinstance(network, dict):
                    for name, config in network.items():
                        networks_str += f'  {name}:\n'
                        for k, v in config.items():
                            networks_str += f'    {k}: {v}\n'
                else:
                    networks_str += f'  {network}:\n'
        
        return f"""version: '3.8'

services:
{services_str}
{volumes_str}
{networks_str}
"""

    @staticmethod
    def requirements_txt(context: Dict[str, Any]) -> str:
        """
        Generate a requirements.txt file for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - dependencies: List of dependencies with versions
        
        Returns:
            String containing the requirements.txt content
        """
        dependencies = context.get('dependencies', [])
        
        # Add comments for sections if dependencies are categorized
        sections = {
            'core': [],
            'dev': [],
            'test': [],
            'docs': [],
            'optional': []
        }
        
        categorized = False
        for dep in dependencies:
            if isinstance(dep, dict):
                categorized = True
                for section, deps in dep.items():
                    if section in sections:
                        sections[section].extend(deps)
            else:
                sections['core'].append(dep)
        
        if categorized:
            result = ''
            for section, deps in sections.items():
                if deps:
                    result += f"# {section.upper()} dependencies\n"
                    result += '\n'.join(deps)
                    result += '\n\n'
            return result.strip()
        else:
            return '\n'.join(dependencies)

    @staticmethod
    def makefile(context: Dict[str, Any]) -> str:
        """
        Generate a Makefile for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - test_command: Command to run tests
                - lint_commands: Commands for linting
                - clean_paths: Paths to clean
        
        Returns:
            String containing the Makefile content
        """
        project_name = context.get('project_name', 'python_project')
        test_command = context.get('test_command', 'pytest')
        lint_commands = context.get('lint_commands', [
            'black .',
            'isort .',
            'flake8 .',
            'mypy .'
        ])
        clean_paths = context.get('clean_paths', [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            'dist',
            'build',
            '*.egg-info'
        ])
        
        # Format lint commands
        lint_str = '\n\t'.join(lint_commands)
        
        # Format clean paths
        clean_str = ' '.join([f'find . -name "{path}" -exec rm -rf {{}} +' for path in clean_paths])
        
        return f"""# Makefile for {project_name}

.PHONY: help clean lint test coverage install dev-install

help:
	@echo "Available commands:"
	@echo "  make install      - Install the package"
	@echo "  make dev-install  - Install the package in development mode"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage"
	@echo "  make lint         - Run linting tools"
	@echo "  make clean        - Clean build artifacts"

install:
	pip install .

dev-install:
	pip install -e ".[dev]"

test:
	{test_command}

coverage:
	pytest --cov={project_name} --cov-report=html

lint:
	{lint_str}

clean:
	{clean_str}
"""

    @staticmethod
    def pytest_ini(context: Dict[str, Any]) -> str:
        """
        Generate a pytest.ini file for a Python project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - test_paths: Paths to test
                - markers: Test markers to register
        
        Returns:
            String containing the pytest.ini content
        """
        project_name = context.get('project_name', 'python_project')
        test_paths = context.get('test_paths', ['tests'])
        markers = context.get('markers', [
            'unit: Unit tests',
            'integration: Integration tests',
            'slow: Slow running tests'
        ])
        
        # Format test paths
        test_paths_str = ' '.join(test_paths)
        
        # Format markers
        markers_str = '\n    '.join(markers)
        
        return f"""[pytest]
testpaths = {test_paths_str}
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = --verbose
markers =
    {markers_str}
"""

    @staticmethod
    def conftest_py(context: Dict[str, Any]) -> str:
        """
        Generate a conftest.py file for pytest.
        
        Args:
            context: Dictionary containing project information:
                - fixtures: List of fixtures to include
                - imports: List of imports
        
        Returns:
            String containing the conftest.py content
        """
        fixtures = context.get('fixtures', [
            {
                'name': 'sample_data',
                'params': None,
                'docstring': 'A fixture that provides sample data for tests.',
                'body': 'return {"key": "value"}'
            }
        ])
        imports = context.get('imports', ['pytest'])
        
        # Format imports
        imports_str = '\n'.join([f'import {imp}' for imp in imports])
        
        # Format fixtures
        fixtures_str = ''
        for fixture in fixtures:
            name = fixture.get('name', 'fixture')
            params = fixture.get('params')
            docstring = fixture.get('docstring', '')
            body = fixture.get('body', 'pass')
            
            fixtures_str += '\n\n@pytest.fixture'
            if params:
                fixtures_str += f'(params={params})'
            fixtures_str += f'\ndef {name}():'
            if docstring:
                fixtures_str += f'\n    """{docstring}"""\n'
            fixtures_str += f'    {body}'
        
        return f"""{imports_str}{fixtures_str}
"""

    @staticmethod
    def test_file(context: Dict[str, Any]) -> str:
        """
        Generate a test file for a Python module.
        
        Args:
            context: Dictionary containing test information:
                - module_name: Name of the module being tested
                - class_name: Name of the class being tested (if any)
                - imports: List of imports
                - fixtures: List of fixtures to use
                - test_cases: List of test cases to include
        
        Returns:
            String containing the test file content
        """
        module_name = context.get('module_name', 'module')
        class_name = context.get('class_name')
        imports = context.get('imports', ['pytest'])
        fixtures = context.get('fixtures', [])
        test_cases = context.get('test_cases', [
            {
                'name': 'test_function',
                'description': 'Test that the function works correctly.',
                'fixtures': [],
                'body': 'assert True'
            }
        ])
        
        # Add module import if not already included
        if module_name and not any(module_name in imp for imp in imports):
            if class_name:
                imports.append(f'from {module_name} import {class_name}')
            else:
                imports.append(f'import {module_name}')
        
        # Format imports
        imports_str = '\n'.join([f'import {imp}' if ' ' not in imp else imp for imp in imports])
        
        # Format test cases
        test_cases_str = ''
        for test in test_cases:
            name = test.get('name', 'test_function')
            description = test.get('description', '')
            test_fixtures = test.get('fixtures', [])
            body = test.get('body', 'assert True')
            
            test_cases_str += f'\n\ndef {name}('
            if test_fixtures:
                test_cases_str += ', '.join(test_fixtures)
            test_cases_str += '):'
            if description:
                test_cases_str += f'\n    """{description}"""\n'
            test_cases_str += f'    {body}'
        
        # If testing a class, wrap tests in a class
        if class_name:
            test_class_name = f'Test{class_name}'
            test_cases_str = f'\n\nclass {test_class_name}:{test_cases_str}'
        
        return f"""{imports_str}{test_cases_str}
"""

    @staticmethod
    def config_py(context: Dict[str, Any]) -> str:
        """
        Generate a configuration module for a Python project.
        
        Args:
            context: Dictionary containing configuration information:
                - project_name: Name of the project
                - config_vars: Dictionary of configuration variables
                - env_vars: List of environment variables to load
                - config_file_paths: List of paths to look for config files
        
        Returns:
            String containing the config.py content
        """
        project_name = context.get('project_name', 'python_project')
        config_vars = context.get('config_vars', {
            'DEBUG': True,
            'LOG_LEVEL': 'INFO',
            'API_TIMEOUT': 30,
        })
        env_vars = context.get('env_vars', [
            'API_KEY',
            'DEBUG',
            'LOG_LEVEL',
        ])
        config_file_paths = context.get('config_file_paths', [
            './config.json',
            '~/.config/{project_name}/config.json',
            '/etc/{project_name}/config.json',
        ])
        
        # Format config vars
        config_vars_str = ''
        for name, value in config_vars.items():
            if isinstance(value, str):
                config_vars_str += f'    {name} = "{value}"\n'
            else:
                config_vars_str += f'    {name} = {value}\n'
        
        # Format env vars loading
        env_vars_str = ''
        for var in env_vars:
            env_vars_str += f'        if "{var}" in os.environ:\n'
            env_vars_str += f'            self.{var} = os.environ.get("{var}")\n'
        
        # Format config file paths
        config_file_paths_str = ''
        for path in config_file_paths:
            path = path.replace('{project_name}', project_name)
            config_file_paths_str += f'            "{path}",\n'
        
        return f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Configuration module for {project_name}.

This module handles loading configuration from various sources:
1. Default values
2. Configuration files (JSON, YAML, etc.)
3. Environment variables
4. Command line arguments
\"\"\"

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Set

logger = logging.getLogger(__name__)


class Config:
    \"\"\"Configuration class for {project_name}.\"\"\"
    
    # Default configuration values
{config_vars_str}
    
    def __init__(self, config_file: Optional[str] = None):
        \"\"\"
        Initialize configuration with values from various sources.
        
        Args:
            config_file: Optional path to a configuration file
        \"\"\"
        # Load from config file
        self._load_from_config_file(config_file)
        
        # Override with environment variables
        self._load_from_environment()
        
        logger.debug(f"Configuration initialized: {{vars(self)}}")
    
    def _load_from_config_file(self, config_file: Optional[str] = None) -> None:
        \"\"\"
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration file, or None to search in default locations
        \"\"\"
        paths_to_check = []
        
        if config_file:
            paths_to_check.append(config_file)
        else:
            # Default paths to check
            paths_to_check.extend([
{config_file_paths_str}
            ])
        
        for path in paths_to_check:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Update instance attributes
                    for key, value in config_data.items():
                        setattr(self, key, value)
                    
                    logger.info(f"Loaded configuration from {{path}}")
                    return
                except Exception as e:
                    logger.warning(f"Error loading configuration from {{path}}: {{e}}")
        
        logger.info("No configuration file found or loaded")
    
    def _load_from_environment(self) -> None:
        \"\"\"Load configuration from environment variables.\"\"\"
        # Load specific environment variables
{env_vars_str}
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary containing all configuration values
        \"\"\"
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}
    
    def save_to_file(self, file_path: str) -> None:
        \"\"\"
        Save current configuration to a JSON file.
        
        Args:
            file_path: Path where to save the configuration
        \"\"\"
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Configuration saved to {{file_path}}")
        except Exception as e:
            logger.error(f"Error saving configuration to {{file_path}}: {{e}}")


# Create a global instance with default configuration
config = Config()
"""

    @staticmethod
    def logger_py(context: Dict[str, Any]) -> str:
        """
        Generate a logger module for a Python project.
        
        Args:
            context: Dictionary containing logger information:
                - project_name: Name of the project