#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for Project Architect.

This module provides the setup configuration for installing the Project Architect
package using setuptools. It defines package metadata, dependencies, entry points,
and other installation parameters.
"""

import os
import re
from setuptools import setup, find_packages


def get_version():
    """Extract version from src/__init__.py."""
    init_path = os.path.join("src", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def get_long_description():
    """Read long description from README.md."""
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


# Define package dependencies
INSTALL_REQUIRES = [
    "anthropic>=0.5.0",
    "fastapi>=0.95.0",
    "uvicorn>=0.22.0",
    "pydantic>=2.0.0",
    "typer>=0.9.0",
    "rich>=13.4.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "jinja2>=3.1.2",
    "PyGithub>=1.59.0",
    "pyyaml>=6.0",
    "jsonschema>=4.17.3",
]

# Development dependencies
DEV_REQUIRES = [
    "pytest>=7.3.1",
    "pytest-cov>=4.1.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "mypy>=1.3.0",
    "flake8>=6.0.0",
    "pre-commit>=3.3.2",
    "tox>=4.6.0",
]

# Documentation dependencies
DOCS_REQUIRES = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.2.1",
    "sphinx-autodoc-typehints>=1.23.0",
]

setup(
    name="project-architect",
    version=get_version(),
    description="AI-powered project scaffolding and code generation tool",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Project Architect Team",
    author_email="info@projectarchitect.dev",
    url="https://github.com/project-architect/project-architect",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="project, generator, architecture, scaffolding, code generation, AI, Claude",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
        "docs": DOCS_REQUIRES,
        "all": DEV_REQUIRES + DOCS_REQUIRES,
    },
    entry_points={
        "console_scripts": [
            "project-architect=src.interfaces.cli:app",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["templates/*", "config/*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/project-architect/project-architect/issues",
        "Source": "https://github.com/project-architect/project-architect",
        "Documentation": "https://project-architect.readthedocs.io/",
    },
    zip_safe=False,
)