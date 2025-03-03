#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Architecture Plan Model.

This module defines classes related to the architecture plan of a project,
including components, dependencies, and data flows.
"""

from typing import List, Dict, Any, Optional
from src.models.project_type import ProjectType


class Component:
    """
    Represents a component in the architecture plan.
    
    Attributes:
        name: The name of the component
        purpose: The purpose or description of the component
        responsibilities: The responsibilities of the component
        technologies: The technologies used by the component
    """
    
    def __init__(
        self,
        name: str,
        purpose: str = "",
        responsibilities: str = "",
        technologies: str = ""
    ):
        """
        Initialize a Component instance.
        
        Args:
            name: The name of the component
            purpose: The purpose or description of the component
            responsibilities: The responsibilities of the component
            technologies: The technologies used by the component
        """
        self.name = name
        self.purpose = purpose
        self.responsibilities = responsibilities
        self.technologies = technologies
    
    def __str__(self) -> str:
        """Get string representation of the component."""
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary.
        
        Returns:
            Dictionary representation of the component
        """
        return {
            "name": self.name,
            "purpose": self.purpose,
            "responsibilities": self.responsibilities,
            "technologies": self.technologies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create a Component instance from a dictionary.
        
        Args:
            data: Dictionary containing component data
            
        Returns:
            A new Component instance
        """
        return cls(
            name=data.get("name", ""),
            purpose=data.get("purpose", ""),
            responsibilities=data.get("responsibilities", ""),
            technologies=data.get("technologies", "")
        )


class Dependency:
    """
    Represents a dependency between components in the architecture plan.
    
    Attributes:
        source: The name of the source component
        target: The name of the target component
        type: The type of dependency (e.g., "uses", "extends", "implements")
        description: Description of the dependency
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        type: str = "uses",
        description: str = ""
    ):
        """
        Initialize a Dependency instance.
        
        Args:
            source: The name of the source component
            target: The name of the target component
            type: The type of dependency
            description: Description of the dependency
        """
        self.source = source
        self.target = target
        self.type = type
        self.description = description
    
    def __str__(self) -> str:
        """Get string representation of the dependency."""
        return f"{self.source} {self.type} {self.target}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dependency to a dictionary.
        
        Returns:
            Dictionary representation of the dependency
        """
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dependency':
        """Create a Dependency instance from a dictionary.
        
        Args:
            data: Dictionary containing dependency data
            
        Returns:
            A new Dependency instance
        """
        return cls(
            source=data.get("source", ""),
            target=data.get("target", ""),
            type=data.get("type", "uses"),
            description=data.get("description", "")
        )


class DataFlow:
    """
    Represents a data flow between components in the architecture plan.
    
    Attributes:
        source: The name of the source component
        target: The name of the target component
        data_description: Description of the data being transferred
        protocol: The protocol used for the data transfer
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        data_description: str,
        protocol: Optional[str] = None
    ):
        """
        Initialize a DataFlow instance.
        
        Args:
            source: The name of the source component
            target: The name of the target component
            data_description: Description of the data being transferred
            protocol: The protocol used for the data transfer
        """
        self.source = source
        self.target = target
        self.data_description = data_description
        self.protocol = protocol
    
    def __str__(self) -> str:
        """Get string representation of the data flow."""
        protocol_str = f" via {self.protocol}" if self.protocol else ""
        return f"{self.source} -> {self.target}{protocol_str}: {self.data_description}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data flow to a dictionary.
        
        Returns:
            Dictionary representation of the data flow
        """
        result = {
            "source": self.source,
            "target": self.target,
            "data_description": self.data_description
        }
        if self.protocol:
            result["protocol"] = self.protocol
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataFlow':
        """Create a DataFlow instance from a dictionary.
        
        Args:
            data: Dictionary containing data flow data
            
        Returns:
            A new DataFlow instance
        """
        return cls(
            source=data.get("source", ""),
            target=data.get("target", ""),
            data_description=data.get("data_description", ""),
            protocol=data.get("protocol")
        )


class ArchitecturePlan:
    """
    Represents the complete architecture plan of a project.
    
    Attributes:
        project_type: The project type
        components: List of components in the architecture
        dependencies: List of dependencies between components
        data_flows: List of data flows between components
        description: Description of the architecture plan
    """
    
    def __init__(
        self,
        project_type: ProjectType,
        components: List[Component],
        dependencies: List[Dependency],
        data_flows: List[DataFlow],
        description: str = ""
    ):
        """
        Initialize an ArchitecturePlan instance.
        
        Args:
            project_type: The project type
            components: List of components in the architecture
            dependencies: List of dependencies between components
            data_flows: List of data flows between components
            description: Description of the architecture plan
        """
        self.project_type = project_type
        self.components = components
        self.dependencies = dependencies
        self.data_flows = data_flows
        self.description = description
    
    def __str__(self) -> str:
        """Get string representation of the architecture plan."""
        return f"Architecture plan for {self.project_type} with {len(self.components)} components"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the architecture plan to a dictionary.
        
        Returns:
            Dictionary representation of the architecture plan
        """
        return {
            "project_type": self.project_type.to_dict(),
            "components": [comp.to_dict() for comp in self.components],
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "data_flows": [flow.to_dict() for flow in self.data_flows],
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchitecturePlan':
        """Create an ArchitecturePlan instance from a dictionary.
        
        Args:
            data: Dictionary containing architecture plan data
            
        Returns:
            A new ArchitecturePlan instance
        """
        project_type = ProjectType.from_dict(data.get("project_type", {}))
        
        components = [
            Component.from_dict(comp_data)
            for comp_data in data.get("components", [])
        ]
        
        dependencies = [
            Dependency.from_dict(dep_data)
            for dep_data in data.get("dependencies", [])
        ]
        
        data_flows = [
            DataFlow.from_dict(flow_data)
            for flow_data in data.get("data_flows", [])
        ]
        
        return cls(
            project_type=project_type,
            components=components,
            dependencies=dependencies,
            data_flows=data_flows,
            description=data.get("description", "")
        )
    
    def get_component_by_name(self, name: str) -> Optional[Component]:
        """Get a component by its name.
        
        Args:
            name: The name of the component to find
            
        Returns:
            The component with the specified name, or None if not found
        """
        for component in self.components:
            if component.name == name:
                return component
        return None
    
    def get_dependencies_for_component(self, component_name: str) -> List[Dependency]:
        """Get all dependencies where a component is the source.
        
        Args:
            component_name: The name of the source component
            
        Returns:
            List of dependencies where the component is the source
        """
        return [dep for dep in self.dependencies if dep.source == component_name]
    
    def get_dependent_components(self, component_name: str) -> List[str]:
        """Get the names of components that depend on a specified component.
        
        Args:
            component_name: The name of the target component
            
        Returns:
            List of names of components that depend on the specified component
        """
        return [dep.source for dep in self.dependencies if dep.target == component_name]
