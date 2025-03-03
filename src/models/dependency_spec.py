#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dependency Specification Model.

This module defines the DependencySpec class, which represents a
dependency specification for a project.
"""

from typing import List, Dict, Any, Optional, Literal


class DependencySpec:
    """
    Represents a dependency specification for a project.
    
    Attributes:
        name: The name of the dependency
        version: The version of the dependency
        type: The type of dependency (production, development, etc.)
        purpose: Description of why the dependency is needed
    """
    
    def __init__(
        self,
        name: str,
        version: str = "",
        type: Literal["production", "development", "optional", "peer"] = "production",
        purpose: str = ""
    ):
        """
        Initialize a DependencySpec instance.
        
        Args:
            name: The name of the dependency
            version: The version of the dependency (empty string for latest)
            type: The type of dependency
            purpose: Description of why the dependency is needed
        """
        self.name = name
        self.version = version
        self.type = type
        self.purpose = purpose
    
    def __str__(self) -> str:
        """Get string representation of the dependency specification."""
        if self.version:
            return f"{self.name}=={self.version}"
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dependency specification to a dictionary.
        
        Returns:
            Dictionary representation of the dependency specification
        """
        return {
            "name": self.name,
            "version": self.version,
            "type": self.type,
            "purpose": self.purpose
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencySpec':
        """Create a DependencySpec instance from a dictionary.
        
        Args:
            data: Dictionary containing dependency specification data
            
        Returns:
            A new DependencySpec instance
        """
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            type=data.get("type", "production"),
            purpose=data.get("purpose", "")
        )
    
    @classmethod
    def from_string(cls, dependency_string: str) -> 'DependencySpec':
        """Create a DependencySpec instance from a string.
        
        Args:
            dependency_string: A dependency string (e.g., "package==1.0.0")
            
        Returns:
            A new DependencySpec instance
        """
        if "==" in dependency_string:
            name, version = dependency_string.split("==", 1)
            return cls(name=name.strip(), version=version.strip())
        elif ">=" in dependency_string:
            name, version = dependency_string.split(">=", 1)
            return cls(name=name.strip(), version=f">={version.strip()}")
        elif "<=" in dependency_string:
            name, version = dependency_string.split("<=", 1)
            return cls(name=name.strip(), version=f"<={version.strip()}")
        elif ">" in dependency_string:
            name, version = dependency_string.split(">", 1)
            return cls(name=name.strip(), version=f">{version.strip()}")
        elif "<" in dependency_string:
            name, version = dependency_string.split("<", 1)
            return cls(name=name.strip(), version=f"<{version.strip()}")
        elif "~=" in dependency_string:
            name, version = dependency_string.split("~=", 1)
            return cls(name=name.strip(), version=f"~={version.strip()}")
        else:
            return cls(name=dependency_string.strip())
    
    def to_requirement_string(self) -> str:
        """Convert the dependency specification to a requirements.txt string.
        
        Returns:
            String representation for requirements.txt
        """
        if self.version:
            return f"{self.name}=={self.version}"
        return self.name
    
    def to_package_json_entry(self) -> Dict[str, str]:
        """Convert the dependency specification to a package.json entry.
        
        Returns:
            Dictionary entry for package.json
        """
        if self.version:
            # Handle different version specifiers
            if self.version.startswith(">="):
                version = self.version
            elif self.version.startswith("<="):
                version = self.version
            elif self.version.startswith(">"):
                version = self.version
            elif self.version.startswith("<"):
                version = self.version
            elif self.version.startswith("~="):
                # Convert Python's ~= to npm's ~
                version = "~" + self.version[2:]
            else:
                # Default to exact version
                version = self.version
            
            # If version has no prefix, add ^ for npm
            if not any(version.startswith(p) for p in ["^", "~", ">", "<", "="]):
                version = f"^{version}"
            
            return {self.name: version}
        else:
            # Default to latest
            return {self.name: "latest"}
