"""
Unit tests package for Project Architect.

This package contains unit tests for individual components of the Project Architect application.
Unit tests focus on testing the functionality of specific classes and functions in isolation,
using mocks and stubs to replace external dependencies.

The unit tests are organized to mirror the structure of the main application, with test modules
corresponding to the modules they test.
"""

import pytest
from unittest import mock
import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union, Type

# Add the parent directory to sys.path to allow imports from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test utilities
from requirements.txt import (
    MockResponse,
    load_test_fixture,
    compare_dict_structures,
    assert_file_structure_matches,
    setup_test_logger
)

# Import core components for testing
from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.core.project_structure_generator import ProjectStructureGenerator
from src.core.code_generator import CodeGenerator
from src.core.dependency_manager import DependencyManager

# Import clients for mocking
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient
from src.clients.base_client import BaseClient

# Import models
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.models.project_structure import ProjectStructure, FileNode, DirectoryNode
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec

# Setup test logger
setup_test_logger()

# Define common test fixtures and mocks
@pytest.fixture
def mock_anthropic_client():
    """Create a mock AnthropicClient for testing."""
    with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.generate_response.return_value = "Mock response from Claude"
        yield client_instance

@pytest.fixture
def mock_github_client():
    """Create a mock GithubClient for testing."""
    with mock.patch('src.clients.github_client.GithubClient') as mock_client:
        client_instance = mock_client.return_value
        client_instance.search_repositories.return_value = [
            {"name": "test-repo", "description": "A test repository", "url": "https://github.com/test/test-repo"}
        ]
        yield client_instance

@pytest.fixture
def sample_project_description():
    """Return a sample project description for testing."""
    return "A web application that allows users to track their daily expenses, categorize them, and generate reports."

@pytest.fixture
def sample_project_type():
    """Return a sample ProjectType instance for testing."""
    return ProjectType(
        type=ProjectTypeEnum.WEB_APPLICATION,
        frontend_framework="React",
        backend_framework="FastAPI",
        database="PostgreSQL",
        description="A web application with React frontend and FastAPI backend",
        features=["User authentication", "Data visualization", "REST API"],
        complexity="Medium"
    )

@pytest.fixture
def sample_architecture_plan():
    """Return a sample ArchitecturePlan instance for testing."""
    return ArchitecturePlan(
        components=[
            Component(
                name="Frontend",
                type="UI",
                description="React-based user interface",
                responsibilities=["Display data", "Handle user input"],
                technologies=["React", "TypeScript", "Material-UI"]
            ),
            Component(
                name="Backend API",
                type="Service",
                description="FastAPI-based REST API",
                responsibilities=["Process requests", "Business logic", "Data access"],
                technologies=["FastAPI", "Python", "SQLAlchemy"]
            ),
            Component(
                name="Database",
                type="Storage",
                description="PostgreSQL database",
                responsibilities=["Store application data"],
                technologies=["PostgreSQL"]
            )
        ],
        dependencies=[
            Dependency(
                source="Frontend",
                target="Backend API",
                type="HTTP/REST",
                description="Frontend calls backend API endpoints"
            ),
            Dependency(
                source="Backend API",
                target="Database",
                type="SQL",
                description="Backend queries and updates database"
            )
        ],
        data_flows=[
            DataFlow(
                source="Frontend",
                target="Backend API",
                description="User requests and form submissions",
                data_format="JSON"
            ),
            DataFlow(
                source="Backend API",
                target="Frontend",
                description="API responses with data",
                data_format="JSON"
            ),
            DataFlow(
                source="Backend API",
                target="Database",
                description="Database queries and updates",
                data_format="SQL"
            ),
            DataFlow(
                source="Database",
                target="Backend API",
                description="Query results",
                data_format="Records"
            )
        ]
    )

@pytest.fixture
def sample_project_structure():
    """Return a sample ProjectStructure instance for testing."""
    return ProjectStructure(
        root=DirectoryNode(
            name="expense_tracker",
            children=[
                DirectoryNode(
                    name="frontend",
                    children=[
                        DirectoryNode(
                            name="src",
                            children=[
                                DirectoryNode(
                                    name="components",
                                    children=[
                                        FileNode(name="Dashboard.tsx", path="frontend/src/components/Dashboard.tsx"),
                                        FileNode(name="ExpenseForm.tsx", path="frontend/src/components/ExpenseForm.tsx")
                                    ]
                                ),
                                FileNode(name="App.tsx", path="frontend/src/App.tsx"),
                                FileNode(name="index.tsx", path="frontend/src/index.tsx")
                            ]
                        ),
                        FileNode(name="package.json", path="frontend/package.json")
                    ]
                ),
                DirectoryNode(
                    name="backend",
                    children=[
                        DirectoryNode(
                            name="app",
                            children=[
                                DirectoryNode(
                                    name="api",
                                    children=[
                                        FileNode(name="expenses.py", path="backend/app/api/expenses.py"),
                                        FileNode(name="users.py", path="backend/app/api/users.py")
                                    ]
                                ),
                                DirectoryNode(
                                    name="models",
                                    children=[
                                        FileNode(name="expense.py", path="backend/app/models/expense.py"),
                                        FileNode(name="user.py", path="backend/app/models/user.py")
                                    ]
                                ),
                                FileNode(name="main.py", path="backend/app/main.py"),
                                FileNode(name="database.py", path="backend/app/database.py")
                            ]
                        ),
                        FileNode(name="requirements.txt", path="backend/requirements.txt")
                    ]
                ),
                FileNode(name="README.md", path="README.md"),
                FileNode(name="docker-compose.yml", path="docker-compose.yml")
            ]
        )
    )

@pytest.fixture
def sample_code_file():
    """Return a sample CodeFile instance for testing."""
    return CodeFile(
        path="backend/app/main.py",
        content="""from fastapi import FastAPI
from app.api import expenses, users
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

# Include routers
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Expense Tracker API"}
""",
        language="python",
        dependencies=["fastapi", "sqlalchemy"]
    )

@pytest.fixture
def sample_dependency_specs():
    """Return sample dependency specifications for testing."""
    return [
        DependencySpec(
            name="fastapi",
            version="^0.95.0",
            type="python",
            purpose="Web framework for building APIs"
        ),
        DependencySpec(
            name="sqlalchemy",
            version="^2.0.0",
            type="python",
            purpose="SQL toolkit and ORM"
        ),
        DependencySpec(
            name="react",
            version="^18.2.0",
            type="npm",
            purpose="JavaScript library for building user interfaces"
        ),
        DependencySpec(
            name="typescript",
            version="^5.0.0",
            type="npm",
            purpose="Typed JavaScript"
        )
    ]

# Export commonly used fixtures
__all__ = [
    'mock_anthropic_client',
    'mock_github_client',
    'sample_project_description',
    'sample_project_type',
    'sample_architecture_plan',
    'sample_project_structure',
    'sample_code_file',
    'sample_dependency_specs',
]