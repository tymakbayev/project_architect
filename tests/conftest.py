#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pytest configuration file for Project Architect.

This module contains fixtures and configuration for the test suite,
including mock clients, sample data, and temporary directories.
"""

import os
import json
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Generator, Callable
from unittest.mock import MagicMock, patch
import pytest
from pydantic import BaseModel

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from src.clients.anthropic_client import AnthropicClient
from src.clients.github_client import GithubClient
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.models.project_structure import ProjectStructure, FileNode, DirectoryNode
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec
from src.config import Config


# ===== Mock Clients =====

@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Create a mock AnthropicClient for testing.
    
    Returns:
        MagicMock: A mock AnthropicClient instance
    """
    mock_client = MagicMock(spec=AnthropicClient)
    
    # Setup common mock responses
    mock_client.analyze_project_type.return_value = ProjectType(
        type=ProjectTypeEnum.PYTHON,
        confidence=0.95,
        details="This is a Python backend application with API endpoints."
    )
    
    mock_client.generate_architecture_plan.return_value = sample_architecture_plan()
    mock_client.generate_project_structure.return_value = sample_project_structure()
    mock_client.generate_code_file.return_value = "def hello_world():\n    return 'Hello, World!'"
    mock_client.suggest_dependencies.return_value = [
        DependencySpec(name="fastapi", version="^0.95.0", purpose="Web framework"),
        DependencySpec(name="pydantic", version="^1.10.7", purpose="Data validation"),
        DependencySpec(name="pytest", version="^7.3.1", purpose="Testing", dev=True)
    ]
    
    return mock_client


@pytest.fixture
def mock_github_client() -> MagicMock:
    """Create a mock GithubClient for testing.
    
    Returns:
        MagicMock: A mock GithubClient instance
    """
    mock_client = MagicMock(spec=GithubClient)
    
    # Setup common mock responses
    mock_client.search_repositories.return_value = [
        {
            "name": "sample-repo-1",
            "description": "A sample repository for testing",
            "url": "https://github.com/user/sample-repo-1",
            "stars": 100,
            "language": "Python"
        },
        {
            "name": "sample-repo-2",
            "description": "Another sample repository",
            "url": "https://github.com/user/sample-repo-2",
            "stars": 50,
            "language": "Python"
        }
    ]
    
    mock_client.get_repository_structure.return_value = {
        "type": "directory",
        "name": "sample-repo",
        "path": "",
        "children": [
            {
                "type": "directory",
                "name": "src",
                "path": "src",
                "children": [
                    {
                        "type": "file",
                        "name": "main.py",
                        "path": "src/main.py"
                    }
                ]
            },
            {
                "type": "file",
                "name": "README.md",
                "path": "README.md"
            }
        ]
    }
    
    mock_client.get_file_content.return_value = "# Sample content\n\nThis is sample content from a GitHub repository."
    
    return mock_client


# ===== Sample Data =====

@pytest.fixture
def sample_project_description() -> str:
    """Provide a sample project description for testing.
    
    Returns:
        str: A sample project description
    """
    return """
    Create a web application that allows users to upload and analyze CSV data files.
    The application should provide data visualization features, user authentication,
    and the ability to share analysis results with other users. It should be built
    using Python for the backend with FastAPI, and React for the frontend.
    """


@pytest.fixture
def sample_architecture_plan() -> ArchitecturePlan:
    """Provide a sample architecture plan for testing.
    
    Returns:
        ArchitecturePlan: A sample architecture plan
    """
    return ArchitecturePlan(
        name="CSV Analyzer",
        description="Web application for CSV data analysis and visualization",
        components=[
            Component(
                name="Backend API",
                type="FastAPI Application",
                description="RESTful API for data processing and user management",
                responsibilities=[
                    "Handle user authentication",
                    "Process CSV file uploads",
                    "Perform data analysis",
                    "Serve analysis results"
                ]
            ),
            Component(
                name="Frontend",
                type="React Application",
                description="User interface for the application",
                responsibilities=[
                    "Provide user authentication UI",
                    "Display data visualizations",
                    "Allow file uploads",
                    "Share analysis results"
                ]
            ),
            Component(
                name="Database",
                type="PostgreSQL",
                description="Persistent storage for user data and analysis results",
                responsibilities=[
                    "Store user information",
                    "Store uploaded files metadata",
                    "Store analysis results"
                ]
            )
        ],
        dependencies=[
            Dependency(
                source="Frontend",
                target="Backend API",
                type="HTTP/REST",
                description="Frontend communicates with backend via REST API"
            ),
            Dependency(
                source="Backend API",
                target="Database",
                type="SQL",
                description="Backend stores and retrieves data from the database"
            )
        ],
        data_flows=[
            DataFlow(
                source="User",
                target="Frontend",
                description="User interacts with the frontend interface"
            ),
            DataFlow(
                source="Frontend",
                target="Backend API",
                description="Frontend sends API requests to the backend"
            ),
            DataFlow(
                source="Backend API",
                target="Database",
                description="Backend reads from and writes to the database"
            )
        ]
    )


@pytest.fixture
def sample_project_structure() -> ProjectStructure:
    """Provide a sample project structure for testing.
    
    Returns:
        ProjectStructure: A sample project structure
    """
    return ProjectStructure(
        name="csv_analyzer",
        root=DirectoryNode(
            name="csv_analyzer",
            children=[
                DirectoryNode(
                    name="backend",
                    children=[
                        DirectoryNode(
                            name="app",
                            children=[
                                FileNode(name="__init__.py", path="backend/app/__init__.py"),
                                FileNode(name="main.py", path="backend/app/main.py"),
                                DirectoryNode(
                                    name="api",
                                    children=[
                                        FileNode(name="__init__.py", path="backend/app/api/__init__.py"),
                                        FileNode(name="auth.py", path="backend/app/api/auth.py"),
                                        FileNode(name="users.py", path="backend/app/api/users.py"),
                                        FileNode(name="files.py", path="backend/app/api/files.py"),
                                        FileNode(name="analysis.py", path="backend/app/api/analysis.py")
                                    ]
                                ),
                                DirectoryNode(
                                    name="models",
                                    children=[
                                        FileNode(name="__init__.py", path="backend/app/models/__init__.py"),
                                        FileNode(name="user.py", path="backend/app/models/user.py"),
                                        FileNode(name="file.py", path="backend/app/models/file.py"),
                                        FileNode(name="analysis.py", path="backend/app/models/analysis.py")
                                    ]
                                ),
                                DirectoryNode(
                                    name="services",
                                    children=[
                                        FileNode(name="__init__.py", path="backend/app/services/__init__.py"),
                                        FileNode(name="auth.py", path="backend/app/services/auth.py"),
                                        FileNode(name="file_processor.py", path="backend/app/services/file_processor.py"),
                                        FileNode(name="analyzer.py", path="backend/app/services/analyzer.py")
                                    ]
                                )
                            ]
                        ),
                        FileNode(name="requirements.txt", path="backend/requirements.txt"),
                        FileNode(name="Dockerfile", path="backend/Dockerfile"),
                        FileNode(name=".env.example", path="backend/.env.example")
                    ]
                ),
                DirectoryNode(
                    name="frontend",
                    children=[
                        DirectoryNode(
                            name="src",
                            children=[
                                FileNode(name="index.js", path="frontend/src/index.js"),
                                FileNode(name="App.js", path="frontend/src/App.js"),
                                DirectoryNode(
                                    name="components",
                                    children=[
                                        FileNode(name="Login.js", path="frontend/src/components/Login.js"),
                                        FileNode(name="Dashboard.js", path="frontend/src/components/Dashboard.js"),
                                        FileNode(name="FileUpload.js", path="frontend/src/components/FileUpload.js"),
                                        FileNode(name="Visualization.js", path="frontend/src/components/Visualization.js")
                                    ]
                                ),
                                DirectoryNode(
                                    name="services",
                                    children=[
                                        FileNode(name="api.js", path="frontend/src/services/api.js"),
                                        FileNode(name="auth.js", path="frontend/src/services/auth.js")
                                    ]
                                )
                            ]
                        ),
                        FileNode(name="package.json", path="frontend/package.json"),
                        FileNode(name=".env.example", path="frontend/.env.example"),
                        FileNode(name="Dockerfile", path="frontend/Dockerfile")
                    ]
                ),
                FileNode(name="docker-compose.yml", path="docker-compose.yml"),
                FileNode(name="README.md", path="README.md"),
                FileNode(name=".gitignore", path=".gitignore")
            ]
        )
    )


@pytest.fixture
def sample_code_files() -> List[CodeFile]:
    """Provide sample code files for testing.
    
    Returns:
        List[CodeFile]: A list of sample code files
    """
    return [
        CodeFile(
            path="backend/app/main.py",
            content="""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, files, analysis

app = FastAPI(title="CSV Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to CSV Analyzer API"}
"""
        ),
        CodeFile(
            path="backend/app/api/auth.py",
            content="""from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.models.user import User, UserInDB
from app.services.auth import authenticate_user, create_access_token

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}
"""
        ),
        CodeFile(
            path="frontend/src/App.js",
            content="""import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { isAuthenticated } from './services/auth';

function App() {
  const [auth, setAuth] = useState(false);
  
  useEffect(() => {
    setAuth(isAuthenticated());
  }, []);

  return (
    <Router>
      <Switch>
        <Route path="/login" render={() => (
          auth ? <Redirect to="/dashboard" /> : <Login setAuth={setAuth} />
        )} />
        <Route path="/dashboard" render={() => (
          auth ? <Dashboard /> : <Redirect to="/login" />
        )} />
        <Route exact path="/" render={() => (
          <Redirect to={auth ? "/dashboard" : "/login"} />
        )} />
      </Switch>
    </Router>
  );
}

export default App;
"""
        )
    ]


# ===== Configuration =====

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Provide a test configuration.
    
    Returns:
        Dict[str, Any]: A test configuration dictionary
    """
    return {
        "anthropic": {
            "api_key": "test_api_key",
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "temperature": 0.7
        },
        "github": {
            "api_key": "test_github_token",
            "search_limit": 5
        },
        "output": {
            "default_output_dir": "/tmp/project_architect_output",
            "create_zip": True
        },
        "logging": {
            "level": "DEBUG",
            "file": "/tmp/project_architect.log"
        }
    }


@pytest.fixture
def config_instance(test_config) -> Config:
    """Create a Config instance with test configuration.
    
    Args:
        test_config: The test configuration dictionary
        
    Returns:
        Config: A Config instance with test configuration
    """
    with patch('src.config.Config._load_config_file') as mock_load:
        mock_load.return_value = test_config
        config = Config()
        return config


# ===== Temporary Directories =====

@pytest.fixture
def temp_output_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test output.
    
    Yields:
        str: Path to the temporary directory
        
    Cleanup:
        Removes the temporary directory after the test
    """
    temp_dir = tempfile.mkdtemp(prefix="project_architect_test_")
    yield temp_dir
    shutil.rmtree(temp_dir)


# ===== Patchers =====

@pytest.fixture
def patch_anthropic_client() -> Generator[Callable[[], MagicMock], None, None]:
    """Patch the AnthropicClient class for all tests using this fixture.
    
    Yields:
        Callable[[], MagicMock]: A function that returns the mock client
    """
    with patch('src.clients.anthropic_client.AnthropicClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Setup default responses
        mock_client.analyze_project_type.return_value = ProjectType(
            type=ProjectTypeEnum.PYTHON,
            confidence=0.95,
            details="This is a Python backend application with API endpoints."
        )
        
        mock_client.generate_architecture_plan.return_value = sample_architecture_plan()
        mock_client.generate_project_structure.return_value = sample_project_structure()
        mock_client.generate_code_file.return_value = "def hello_world():\n    return 'Hello, World!'"
        
        yield lambda: mock_client


@pytest.fixture
def patch_github_client() -> Generator[Callable[[], MagicMock], None, None]:
    """Patch the GithubClient class for all tests using this fixture.
    
    Yields:
        Callable[[], MagicMock]: A function that returns the mock client
    """
    with patch('src.clients.github_client.GithubClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Setup default responses
        mock_client.search_repositories.return_value = [
            {
                "name": "sample-repo-1",
                "description": "A sample repository for testing",
                "url": "https://github.com/user/sample-repo-1",
                "stars": 100,
                "language": "Python"
            }
        ]
        
        yield lambda: mock_client


@pytest.fixture
def patch_os_environ() -> Generator[Dict[str, str], None, None]:
    """Patch os.environ for testing environment variables.
    
    Yields:
        Dict[str, str]: A dictionary representing the patched environment
    """
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "GITHUB_API_KEY": "test_github_key",
        "PROJECT_ARCHITECT_OUTPUT_DIR": "/tmp/project_architect_test"
    }, clear=True):
        yield os.environ


# ===== Utility Fixtures =====

@pytest.fixture
def load_test_json() -> Callable[[str], Dict[str, Any]]:
    """Create a function to load JSON test data from the tests/data directory.
    
    Returns:
        Callable[[str], Dict[str, Any]]: A function that loads JSON data
    """
    def _load_json(filename: str) -> Dict[str, Any]:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        file_path = os.path.join(data_dir, filename)
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    return _load_json


@pytest.fixture
def assert_files_exist() -> Callable[[str, List[str]], None]:
    """Create a function to assert that files exist in a directory.
    
    Returns:
        Callable[[str, List[str]], None]: A function that asserts files exist
    """
    def _assert_files_exist(directory: str, files: List[str]) -> None:
        for file_path in files:
            full_path = os.path.join(directory, file_path)
            assert os.path.exists(full_path), f"File {full_path} does not exist"
    
    return _assert_files_exist


# ===== Test Database =====

@pytest.fixture
def setup_test_db() -> Generator[None, None, None]:
    """Set up a test database for integration tests.
    
    This fixture would normally set up a test database, but for this project
    we're just simulating the setup and teardown.
    
    Yields:
        None
    """
    # In a real implementation, this would create a test database
    print("Setting up test database")
    
    yield
    
    # In a real implementation, this would tear down the test database
    print("Tearing down test database")