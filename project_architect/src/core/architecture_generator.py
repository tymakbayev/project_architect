#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Architecture Generator Module.

This module is responsible for generating architecture plans for projects
based on their type and requirements using the Anthropic Claude API.
"""

import logging
from typing import List, Dict, Any, Optional

from src.models.project_type import ProjectType
from src.models.architecture_plan import (
    ArchitecturePlan, 
    Component, 
    Dependency,
    DataFlow
)
from src.clients.anthropic_client import AnthropicClient


class ArchitectureGenerator:
    """Generates architecture plans for projects based on their type and requirements.
    
    This class uses the Anthropic Claude API to generate detailed architecture plans
    for software projects, including components, dependencies, and data flows.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the ArchitectureGenerator with an Anthropic client.
        
        Args:
            api_key: Optional Anthropic API key. If not provided, will attempt
                    to use the ANTHROPIC_API_KEY environment variable.
        """
        self.anthropic_client = AnthropicClient(api_key)
        self.logger = logging.getLogger(__name__)

    def generate_architecture(self, project_type: ProjectType, requirements: List[str]) -> ArchitecturePlan:
        """Generate an architecture plan based on project type and requirements.
        
        Args:
            project_type: The determined project type
            requirements: List of key project requirements
            
        Returns:
            ArchitecturePlan: A complete architecture plan for the project
        """
        self.logger.info(f"Generating architecture for {project_type.type_enum.name} project")
        
        # First, generate the high-level components
        components = self._generate_components(project_type, requirements)
        
        # Then, generate dependencies between components
        dependencies = self._generate_dependencies(components, project_type)
        
        # Finally, generate data flows between components
        data_flows = self._generate_data_flows(components, dependencies, project_type)
        
        # Create and return the complete architecture plan
        architecture_plan = ArchitecturePlan(
            project_type=project_type,
            components=components,
            dependencies=dependencies,
            data_flows=data_flows
        )
        
        self.logger.info(f"Generated architecture plan with {len(components)} components")
        return architecture_plan

    def _generate_components(self, project_type: ProjectType, requirements: List[str]) -> List[Component]:
        """Generate the components for the architecture plan.
        
        Args:
            project_type: The determined project type
            requirements: List of key project requirements
            
        Returns:
            List[Component]: List of components for the architecture
        """
        self.logger.info("Generating components for architecture plan")
        
        requirements_text = "\n".join([f"- {req}" for req in requirements])
        
        prompt = f"""
        You are an expert software architect. Design the main components for a {project_type.type_enum.name} project 
        with the following requirements:
        
        {requirements_text}
        
        For each component, provide:
        1. Name: A clear, descriptive name
        2. Purpose: What the component does
        3. Responsibilities: Key functions/methods it should have
        4. Technologies: Specific libraries or frameworks it should use
        
        Format your response as a structured list of components with these attributes clearly labeled.
        Include at least 4-7 components that together would form a complete architecture.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response to extract components
        components = []
        current_component = None
        current_attribute = None
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a new component
            if line.startswith("#") or (line.lower().startswith("component") and ":" in line):
                # Save previous component if it exists
                if current_component and current_component.get("name"):
                    components.append(Component(
                        name=current_component.get("name", ""),
                        purpose=current_component.get("purpose", ""),
                        responsibilities=current_component.get("responsibilities", ""),
                        technologies=current_component.get("technologies", "")
                    ))
                
                # Start a new component
                current_component = {"name": "", "purpose": "", "responsibilities": "", "technologies": ""}
                if ":" in line:
                    current_component["name"] = line.split(":", 1)[1].strip()
                else:
                    current_component["name"] = line.lstrip("# ").strip()
                current_attribute = None
            
            # Check if this is a component attribute
            elif any(attr in line.lower() for attr in ["name:", "purpose:", "responsibilities:", "technologies:"]):
                for attr in ["name", "purpose", "responsibilities", "technologies"]:
                    if f"{attr}:" in line.lower():
                        current_attribute = attr
                        value = line.split(":", 1)[1].strip() if ":" in line else ""
                        if current_component:
                            current_component[current_attribute] = value
                        break
            
            # Otherwise, this is content for the current attribute
            elif current_component and current_attribute:
                current_component[current_attribute] += " " + line
        
        # Add the last component if it exists
        if current_component and current_component.get("name"):
            components.append(Component(
                name=current_component.get("name", ""),
                purpose=current_component.get("purpose", ""),
                responsibilities=current_component.get("responsibilities", ""),
                technologies=current_component.get("technologies", "")
            ))
        
        self.logger.info(f"Generated {len(components)} components")
        return components

    def _generate_dependencies(self, components: List[Component], project_type: ProjectType) -> List[Dependency]:
        """Generate dependencies between components.
        
        Args:
            components: List of components in the architecture
            project_type: The determined project type
            
        Returns:
            List[Dependency]: List of dependencies between components
        """
        self.logger.info("Generating dependencies between components")
        
        component_names = [comp.name for comp in components]
        component_text = "\n".join([f"- {comp.name}: {comp.purpose}" for comp in components])
        
        prompt = f"""
        You are an expert software architect. Based on the following components for a {project_type.type_enum.name} project,
        determine the dependencies between them.
        
        Components:
        {component_text}
        
        For each component, list which other components it depends on directly.
        Format your response as:
        
        Component: [component name]
        Dependencies: [comma-separated list of components it depends on]
        
        Only include actual dependencies, not every component needs to depend on others.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response to extract dependencies
        dependencies = []
        current_component = None
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith("component:") or line.lower().startswith("component "):
                component_name = line.split(":", 1)[1].strip() if ":" in line else ""
                current_component = next((c for c in components if c.name.lower() == component_name.lower()), None)
                
            elif current_component and (line.lower().startswith("dependencies:") or line.lower().startswith("depends on:")):
                deps_text = line.split(":", 1)[1].strip() if ":" in line else ""
                if deps_text.lower() in ["none", "n/a", "-"]:
                    continue
                    
                # Split by commas and clean up
                dep_names = [d.strip() for d in deps_text.split(",")]
                
                # Create dependency objects
                for dep_name in dep_names:
                    # Find the actual component object
                    dep_component = next((c for c in components if c.name.lower() == dep_name.lower()), None)
                    if dep_component:
                        dependencies.append(Dependency(
                            source=current_component.name,
                            target=dep_component.name,
                            type="uses"
                        ))
        
        self.logger.info(f"Generated {len(dependencies)} dependencies")
        return dependencies

    def _generate_data_flows(self, components: List[Component], dependencies: List[Dependency], 
                           project_type: ProjectType) -> List[DataFlow]:
        """Generate data flows between components.
        
        Args:
            components: List of components in the architecture
            dependencies: List of dependencies between components
            project_type: The determined project type
            
        Returns:
            List[DataFlow]: List of data flows between components
        """
        self.logger.info("Generating data flows between components")
        
        component_text = "\n".join([f"- {comp.name}: {comp.purpose}" for comp in components])
        dependency_text = "\n".join([f"- {dep.source} depends on {dep.target}" for dep in dependencies])
        
        prompt = f"""
        You are an expert software architect. Based on the following components and dependencies for a 
        {project_type.type_enum.name} project, determine the data flows between them.
        
        Components:
        {component_text}
        
        Dependencies:
        {dependency_text}
        
        For each dependency, describe what data flows from one component to another.
        Format your response as:
        
        From: [source component]
        To: [target component]
        Data: [description of data being passed]
        
        Be specific about the actual data being passed between components.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response to extract data flows
        data_flows = []
        current_flow = {"from": "", "to": "", "data": ""}
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if not line:
                # Save the current flow if it's complete
                if current_flow["from"] and current_flow["to"] and current_flow["data"]:
                    data_flows.append(DataFlow(
                        source=current_flow["from"],
                        target=current_flow["to"],
                        data_description=current_flow["data"]
                    ))
                    current_flow = {"from": "", "to": "", "data": ""}
                continue
                
            if line.lower().startswith("from:"):
                current_flow["from"] = line.split(":", 1)[1].strip() if ":" in line else ""
                
            elif line.lower().startswith("to:"):
                current_flow["to"] = line.split(":", 1)[1].strip() if ":" in line else ""
                
            elif line.lower().startswith("data:"):
                current_flow["data"] = line.split(":", 1)[1].strip() if ":" in line else ""
        
        # Add the last flow if it's complete
        if current_flow["from"] and current_flow["to"] and current_flow["data"]:
            data_flows.append(DataFlow(
                source=current_flow["from"],
                target=current_flow["to"],
                data_description=current_flow["data"]
            ))
        
        self.logger.info(f"Generated {len(data_flows)} data flows")
        return data_flows
