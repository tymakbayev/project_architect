#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the ArchitectureGenerator module.

This module contains tests for the ArchitectureGenerator class, which is responsible for
generating architecture plans based on project descriptions and project types.
"""

import os
import json
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.core.architecture_generator import ArchitectureGenerator
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.clients.anthropic_client import AnthropicClient


class TestArchitectureGenerator:
    """Test suite for the ArchitectureGenerator class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AnthropicClient for testing."""
        with mock.patch('src.clients.anthropic_client.AnthropicClient') as mock_client:
            client_instance = mock_client.return_value
            # Mock response for generate_architecture_plan
            client_instance.generate_response.return_value = json.dumps({
                "components": [
                    {
                        "name": "Frontend",
                        "type": "UI",
                        "description": "React-based user interface",
                        "responsibilities": ["Display data", "Handle user input"],
                        "technologies": ["React", "TypeScript", "Material-UI"]
                    },
                    {
                        "name": "Backend API",
                        "type": "Service",
                        "description": "FastAPI-based REST API",
                        "responsibilities": ["Process requests", "Business logic", "Data validation"],
                        "technologies": ["FastAPI", "Python", "Pydantic"]
                    },
                    {
                        "name": "Database",
                        "type": "Storage",
                        "description": "PostgreSQL database",
                        "responsibilities": ["Data persistence", "Data retrieval"],
                        "technologies": ["PostgreSQL", "SQLAlchemy"]
                    }
                ],
                "dependencies": [
                    {
                        "source": "Frontend",
                        "target": "Backend API",
                        "type": "HTTP/REST",
                        "description": "Frontend makes API calls to backend"
                    },
                    {
                        "source": "Backend API",
                        "target": "Database",
                        "type": "SQL",
                        "description": "Backend queries and updates database"
                    }
                ],
                "data_flows": [
                    {
                        "source": "Frontend",
                        "target": "Backend API",
                        "data_type": "JSON",
                        "description": "User input and API requests"
                    },
                    {
                        "source": "Backend API",
                        "target": "Frontend",
                        "data_type": "JSON",
                        "description": "API responses with data"
                    },
                    {
                        "source": "Backend API",
                        "target": "Database",
                        "data_type": "SQL Queries",
                        "description": "Database queries and commands"
                    },
                    {
                        "source": "Database",
                        "target": "Backend API",
                        "data_type": "Result Sets",
                        "description": "Query results and data"
                    }
                ]
            })
            yield client_instance

    @pytest.fixture
    def architecture_generator(self, mock_anthropic_client):
        """Create an ArchitectureGenerator instance with mocked client."""
        generator = ArchitectureGenerator(api_key="test_api_key")
        generator.anthropic_client = mock_anthropic_client
        return generator

    @pytest.fixture
    def sample_project_type(self):
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
    def sample_project_description(self):
        """Return a sample project description for testing."""
        return "A web application that allows users to track their daily expenses, categorize them, and generate reports."

    def test_init(self):
        """Test the initialization of ArchitectureGenerator."""
        # Test with API key
        generator = ArchitectureGenerator(api_key="test_api_key")
        assert isinstance(generator.anthropic_client, AnthropicClient)
        assert generator.anthropic_client.api_key == "test_api_key"
        
        # Test with existing client
        mock_client = mock.MagicMock()
        generator = ArchitectureGenerator(anthropic_client=mock_client)
        assert generator.anthropic_client == mock_client
        
        # Test with neither API key nor client
        with pytest.raises(ValueError):
            ArchitectureGenerator()

    def test_generate_architecture_plan(self, architecture_generator, sample_project_type, sample_project_description):
        """Test generating an architecture plan from a project type and description."""
        # Call the method
        architecture_plan = architecture_generator.generate_architecture_plan(
            project_type=sample_project_type,
            project_description=sample_project_description
        )
        
        # Verify the result
        assert isinstance(architecture_plan, ArchitecturePlan)
        assert len(architecture_plan.components) == 3
        assert len(architecture_plan.dependencies) == 2
        assert len(architecture_plan.data_flows) == 4
        
        # Check components
        frontend = next((c for c in architecture_plan.components if c.name == "Frontend"), None)
        assert frontend is not None
        assert frontend.type == "UI"
        assert "React" in frontend.technologies
        
        backend = next((c for c in architecture_plan.components if c.name == "Backend API"), None)
        assert backend is not None
        assert backend.type == "Service"
        assert "FastAPI" in backend.technologies
        
        database = next((c for c in architecture_plan.components if c.name == "Database"), None)
        assert database is not None
        assert database.type == "Storage"
        assert "PostgreSQL" in database.technologies
        
        # Check dependencies
        frontend_to_backend = next((d for d in architecture_plan.dependencies 
                                  if d.source == "Frontend" and d.target == "Backend API"), None)
        assert frontend_to_backend is not None
        assert frontend_to_backend.type == "HTTP/REST"
        
        backend_to_db = next((d for d in architecture_plan.dependencies 
                            if d.source == "Backend API" and d.target == "Database"), None)
        assert backend_to_db is not None
        assert backend_to_db.type == "SQL"
        
        # Check data flows
        frontend_to_backend_flow = next((f for f in architecture_plan.data_flows 
                                       if f.source == "Frontend" and f.target == "Backend API"), None)
        assert frontend_to_backend_flow is not None
        assert frontend_to_backend_flow.data_type == "JSON"
        
        # Verify the client was called with the right parameters
        architecture_generator.anthropic_client.generate_response.assert_called_once()
        call_args = architecture_generator.anthropic_client.generate_response.call_args[0][0]
        assert "architecture plan" in call_args.lower()
        assert sample_project_description in call_args
        assert sample_project_type.type.value in call_args

    def test_generate_architecture_plan_with_custom_prompt(self, architecture_generator, sample_project_type, sample_project_description):
        """Test generating an architecture plan with a custom prompt."""
        # Define a custom prompt
        custom_prompt = "Create a microservices architecture for the following project: {project_description}"
        
        # Call the method with custom prompt
        architecture_plan = architecture_generator.generate_architecture_plan(
            project_type=sample_project_type,
            project_description=sample_project_description,
            custom_prompt=custom_prompt
        )
        
        # Verify the result
        assert isinstance(architecture_plan, ArchitecturePlan)
        
        # Verify the client was called with the custom prompt
        architecture_generator.anthropic_client.generate_response.assert_called_once()
        call_args = architecture_generator.anthropic_client.generate_response.call_args[0][0]
        assert custom_prompt.format(project_description=sample_project_description) in call_args

    def test_parse_architecture_plan_response(self, architecture_generator):
        """Test parsing the architecture plan response from the AI model."""
        # Sample response JSON
        response_json = {
            "components": [
                {
                    "name": "Test Component",
                    "type": "Service",
                    "description": "A test component",
                    "responsibilities": ["Test responsibility"],
                    "technologies": ["Test tech"]
                }
            ],
            "dependencies": [
                {
                    "source": "Component A",
                    "target": "Component B",
                    "type": "HTTP",
                    "description": "A test dependency"
                }
            ],
            "data_flows": [
                {
                    "source": "Component A",
                    "target": "Component B",
                    "data_type": "JSON",
                    "description": "A test data flow"
                }
            ]
        }
        
        # Call the method
        architecture_plan = architecture_generator._parse_architecture_plan_response(json.dumps(response_json))
        
        # Verify the result
        assert isinstance(architecture_plan, ArchitecturePlan)
        assert len(architecture_plan.components) == 1
        assert architecture_plan.components[0].name == "Test Component"
        assert len(architecture_plan.dependencies) == 1
        assert architecture_plan.dependencies[0].source == "Component A"
        assert len(architecture_plan.data_flows) == 1
        assert architecture_plan.data_flows[0].data_type == "JSON"

    def test_parse_architecture_plan_response_invalid_json(self, architecture_generator):
        """Test parsing an invalid JSON response."""
        # Invalid JSON
        invalid_json = "This is not valid JSON"
        
        # Call the method and expect an exception
        with pytest.raises(ValueError):
            architecture_generator._parse_architecture_plan_response(invalid_json)

    def test_parse_architecture_plan_response_missing_fields(self, architecture_generator):
        """Test parsing a response with missing required fields."""
        # JSON missing required fields
        incomplete_json = {
            "components": [
                {
                    "name": "Test Component",
                    "type": "Service",
                    "description": "A test component",
                    "responsibilities": ["Test responsibility"],
                    "technologies": ["Test tech"]
                }
            ]
            # Missing dependencies and data_flows
        }
        
        # Call the method
        architecture_plan = architecture_generator._parse_architecture_plan_response(json.dumps(incomplete_json))
        
        # Verify the result has empty lists for missing fields
        assert isinstance(architecture_plan, ArchitecturePlan)
        assert len(architecture_plan.components) == 1
        assert len(architecture_plan.dependencies) == 0
        assert len(architecture_plan.data_flows) == 0

    def test_generate_architecture_plan_client_error(self, architecture_generator, sample_project_type, sample_project_description):
        """Test handling of client errors when generating an architecture plan."""
        # Mock the client to raise an exception
        architecture_generator.anthropic_client.generate_response.side_effect = Exception("API Error")
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            architecture_generator.generate_architecture_plan(
                project_type=sample_project_type,
                project_description=sample_project_description
            )
        
        assert "API Error" in str(excinfo.value)

    def test_generate_architecture_plan_with_additional_requirements(self, architecture_generator, sample_project_type, sample_project_description):
        """Test generating an architecture plan with additional requirements."""
        # Additional requirements
        additional_requirements = [
            "Must support offline mode",
            "Must be scalable to handle 10,000 concurrent users",
            "Must comply with GDPR regulations"
        ]
        
        # Call the method with additional requirements
        architecture_plan = architecture_generator.generate_architecture_plan(
            project_type=sample_project_type,
            project_description=sample_project_description,
            additional_requirements=additional_requirements
        )
        
        # Verify the result
        assert isinstance(architecture_plan, ArchitecturePlan)
        
        # Verify the client was called with the additional requirements
        architecture_generator.anthropic_client.generate_response.assert_called_once()
        call_args = architecture_generator.anthropic_client.generate_response.call_args[0][0]
        for req in additional_requirements:
            assert req in call_args

    @mock.patch('src.core.architecture_generator.logging')
    def test_logging(self, mock_logging, architecture_generator, sample_project_type, sample_project_description):
        """Test that the architecture generator logs appropriate messages."""
        # Call the method
        architecture_generator.generate_architecture_plan(
            project_type=sample_project_type,
            project_description=sample_project_description
        )
        
        # Verify logging calls
        mock_logging.info.assert_any_call(mock.ANY)
        mock_logging.debug.assert_any_call(mock.ANY)

    def test_component_creation(self, architecture_generator):
        """Test the creation of Component objects from dictionary data."""
        component_data = {
            "name": "Test Component",
            "type": "Service",
            "description": "A test component",
            "responsibilities": ["Test responsibility"],
            "technologies": ["Test tech"]
        }
        
        # Create a Component using the data
        component = Component(**component_data)
        
        # Verify the Component properties
        assert component.name == "Test Component"
        assert component.type == "Service"
        assert component.description == "A test component"
        assert component.responsibilities == ["Test responsibility"]
        assert component.technologies == ["Test tech"]

    def test_dependency_creation(self, architecture_generator):
        """Test the creation of Dependency objects from dictionary data."""
        dependency_data = {
            "source": "Component A",
            "target": "Component B",
            "type": "HTTP",
            "description": "A test dependency"
        }
        
        # Create a Dependency using the data
        dependency = Dependency(**dependency_data)
        
        # Verify the Dependency properties
        assert dependency.source == "Component A"
        assert dependency.target == "Component B"
        assert dependency.type == "HTTP"
        assert dependency.description == "A test dependency"

    def test_data_flow_creation(self, architecture_generator):
        """Test the creation of DataFlow objects from dictionary data."""
        data_flow_data = {
            "source": "Component A",
            "target": "Component B",
            "data_type": "JSON",
            "description": "A test data flow"
        }
        
        # Create a DataFlow using the data
        data_flow = DataFlow(**data_flow_data)
        
        # Verify the DataFlow properties
        assert data_flow.source == "Component A"
        assert data_flow.target == "Component B"
        assert data_flow.data_type == "JSON"
        assert data_flow.description == "A test data flow"

    def test_architecture_plan_creation(self, architecture_generator):
        """Test the creation of ArchitecturePlan objects."""
        # Create components, dependencies, and data flows
        components = [
            Component(
                name="Component A",
                type="Service",
                description="A test component",
                responsibilities=["Test responsibility"],
                technologies=["Test tech"]
            ),
            Component(
                name="Component B",
                type="UI",
                description="Another test component",
                responsibilities=["Another test responsibility"],
                technologies=["Another test tech"]
            )
        ]
        
        dependencies = [
            Dependency(
                source="Component A",
                target="Component B",
                type="HTTP",
                description="A test dependency"
            )
        ]
        
        data_flows = [
            DataFlow(
                source="Component A",
                target="Component B",
                data_type="JSON",
                description="A test data flow"
            )
        ]
        
        # Create an ArchitecturePlan
        architecture_plan = ArchitecturePlan(
            components=components,
            dependencies=dependencies,
            data_flows=data_flows
        )
        
        # Verify the ArchitecturePlan properties
        assert len(architecture_plan.components) == 2
        assert architecture_plan.components[0].name == "Component A"
        assert architecture_plan.components[1].name == "Component B"
        assert len(architecture_plan.dependencies) == 1
        assert architecture_plan.dependencies[0].source == "Component A"
        assert len(architecture_plan.data_flows) == 1
        assert architecture_plan.data_flows[0].data_type == "JSON"


if __name__ == "__main__":
    pytest.main(["-v", __file__])