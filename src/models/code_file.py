#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code File Model.

This module defines the CodeFile class, which represents a generated
code file in the project.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


class CodeFile:
    """
    Represents a generated code file in the project.
    
    Attributes:
        path: Path to the file within the project
        content: The content of the file
        language: The programming language of the file
        description: Description of the file's purpose
        dependencies: List of other files this file depends on
    """
    
    def __init__(
        self,
        path: str,
        content: str,
        language: str = "",
        description: str = "",
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize a CodeFile instance.
        
        Args:
            path: Path to the file within the project
            content: The content of the file
            language: The programming language of the file
            description: Description of the file's purpose
            dependencies: List of other files this file depends on
        """
        self.path = path
        self.content = content
        self.language = language or self._infer_language(path)
        self.description = description
        self.dependencies = dependencies or []
    
    def __str__(self) -> str:
        """Get string representation of the code file."""
        return f"{self.path} ({self.language})"
    
    def _infer_language(self, path: str) -> str:
        """Infer the programming language from the file extension.
        
        Args:
            path: The file path
            
        Returns:
            The inferred programming language
        """
        extension = Path(path).suffix.lower()
        
        # Map of file extensions to languages
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sass": "sass",
            ".less": "less",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".sh": "shell",
            ".bat": "batch",
            ".ps1": "powershell",
            ".sql": "sql",
        }
        
        return language_map.get(extension, "text")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the code file to a dictionary.
        
        Returns:
            Dictionary representation of the code file
        """
        return {
            "path": self.path,
            "content": self.content,
            "language": self.language,
            "description": self.description,
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeFile':
        """Create a CodeFile instance from a dictionary.
        
        Args:
            data: Dictionary containing code file data
            
        Returns:
            A new CodeFile instance
        """
        return cls(
            path=data.get("path", ""),
            content=data.get("content", ""),
            language=data.get("language", ""),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", [])
        )
    
    @property
    def filename(self) -> str:
        """Get the filename without the path.
        
        Returns:
            The filename
        """
        return Path(self.path).name
    
    @property
    def extension(self) -> str:
        """Get the file extension.
        
        Returns:
            The file extension (including the dot)
        """
        return Path(self.path).suffix
    
    def update_content(self, new_content: str) -> None:
        """Update the content of the file.
        
        Args:
            new_content: The new content
        """
        self.content = new_content
