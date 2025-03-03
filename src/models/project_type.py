#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Type Model.

This module defines the ProjectType class and ProjectTypeEnum enumeration,
which represent the type and characteristics of a project.
"""

from enum import Enum, auto
from typing import List, Dict, Any, Optional


class ProjectTypeEnum(Enum):
    """Enumeration of supported project types."""
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    REACT = auto()
    ANGULAR = auto()
    VUE = auto()
    NODE = auto()
    DJANGO = auto()
    FLASK = auto()
    FASTAPI = auto()
    EXPRESS = auto()
    WEB = auto()
    MOBILE = auto()
    DESKTOP = auto()
    LIBRARY = auto()
    CLI = auto()
    API = auto()
    FULLSTACK = auto()
    GENERIC = auto()


class ProjectType:
    """
    Represents the type and characteristics of a project.
    
    Attributes:
        type_enum: The project type enumeration value
        name: The name of the project type
        subtypes: List of project subtypes
        description: Description of the project type
        technologies: List of technologies associated with the project type
    """
    
    def __init__(
        self,
        type_enum: ProjectTypeEnum,
        name: Optional[str] = None,
        subtypes: Optional[List[str]] = None,
        description: str = "",
        technologies: Optional[List[str]] = None
    ):
        """
        Initialize a ProjectType instance.
        
        Args:
            type_enum: The project type enumeration value
            name: The name of the project type (defaults to enum name)
            subtypes: List of project subtypes
            description: Description of the project type
            technologies: List of technologies associated with the project type
        """
        self.type_enum = type_enum
        self.name = name or type_enum.name.lower()
        self.subtypes = subtypes or []
        self.description = description
        self.technologies = technologies or []
    
    def __str__(self) -> str:
        """Get string representation of the project type."""
        return f"{self.name} project"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project type to a dictionary.
        
        Returns:
            Dictionary representation of the project type
        """
        return {
            "type": self.name,
            "subtypes": self.subtypes,
            "description": self.description,
            "technologies": self.technologies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectType':
        """Create a ProjectType instance from a dictionary.
        
        Args:
            data: Dictionary containing project type data
            
        Returns:
            A new ProjectType instance
        """
        type_name = data.get("type", "").upper()
        try:
            type_enum = ProjectTypeEnum[type_name]
        except KeyError:
            # Default to GENERIC if type is not recognized
            type_enum = ProjectTypeEnum.GENERIC
        
        return cls(
            type_enum=type_enum,
            name=data.get("type", type_enum.name.lower()),
            subtypes=data.get("subtypes", []),
            description=data.get("description", ""),
            technologies=data.get("technologies", [])
        )
