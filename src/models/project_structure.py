#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Structure Model.

This module defines classes related to the structure of a project,
including file and directory nodes.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path


class FileNode:
    """
    Represents a file in the project structure.
    
    Attributes:
        path: Path to the file within the project
        description: Description of the file's purpose
        content: The content of the file (if available)
        components: List of components implemented in the file
    """
    
    def __init__(
        self,
        path: str,
        description: str = "",
        content: Optional[str] = None,
        components: Optional[List[str]] = None
    ):
        """
        Initialize a FileNode instance.
        
        Args:
            path: Path to the file within the project
            description: Description of the file's purpose
            content: The content of the file (if available)
            components: List of components implemented in the file
        """
        self.path = path
        self.description = description
        self.content = content
        self.components = components or []
    
    def __str__(self) -> str:
        """Get string representation of the file node."""
        return self.path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the file node to a dictionary.
        
        Returns:
            Dictionary representation of the file node
        """
        result = {
            "path": self.path,
            "description": self.description,
            "components": self.components
        }
        if self.content is not None:
            result["content"] = self.content
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileNode':
        """Create a FileNode instance from a dictionary.
        
        Args:
            data: Dictionary containing file node data
            
        Returns:
            A new FileNode instance
        """
        return cls(
            path=data.get("path", ""),
            description=data.get("description", ""),
            content=data.get("content"),
            components=data.get("components", [])
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


class DirectoryNode:
    """
    Represents a directory in the project structure.
    
    Attributes:
        path: Path to the directory within the project
        description: Description of the directory's purpose
        children: List of child nodes (files and directories)
    """
    
    def __init__(
        self,
        path: str,
        description: str = "",
        children: Optional[List[Union['DirectoryNode', FileNode]]] = None
    ):
        """
        Initialize a DirectoryNode instance.
        
        Args:
            path: Path to the directory within the project
            description: Description of the directory's purpose
            children: List of child nodes (files and directories)
        """
        self.path = path
        self.description = description
        self.children = children or []
    
    def __str__(self) -> str:
        """Get string representation of the directory node."""
        return self.path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the directory node to a dictionary.
        
        Returns:
            Dictionary representation of the directory node
        """
        return {
            "path": self.path,
            "description": self.description,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DirectoryNode':
        """Create a DirectoryNode instance from a dictionary.
        
        Args:
            data: Dictionary containing directory node data
            
        Returns:
            A new DirectoryNode instance
        """
        children_data = data.get("children", [])
        children = []
        
        for child_data in children_data:
            if child_data.get("children") is not None:
                # This is a directory node
                children.append(DirectoryNode.from_dict(child_data))
            else:
                # This is a file node
                children.append(FileNode.from_dict(child_data))
        
        return cls(
            path=data.get("path", ""),
            description=data.get("description", ""),
            children=children
        )
    
    def add_file(self, file_node: FileNode) -> None:
        """Add a file node to the directory.
        
        Args:
            file_node: The file node to add
        """
        self.children.append(file_node)
    
    def add_directory(self, directory_node: 'DirectoryNode') -> None:
        """Add a directory node to the directory.
        
        Args:
            directory_node: The directory node to add
        """
        self.children.append(directory_node)
    
    def get_files(self) -> List[FileNode]:
        """Get all file nodes in the directory.
        
        Returns:
            List of file nodes
        """
        return [child for child in self.children if isinstance(child, FileNode)]
    
    def get_directories(self) -> List['DirectoryNode']:
        """Get all directory nodes in the directory.
        
        Returns:
            List of directory nodes
        """
        return [child for child in self.children if isinstance(child, DirectoryNode)]
    
    def find_file(self, path: str) -> Optional[FileNode]:
        """Find a file node by path.
        
        Args:
            path: The path to find
            
        Returns:
            The file node with the specified path, or None if not found
        """
        for child in self.children:
            if isinstance(child, FileNode) and child.path == path:
                return child
            elif isinstance(child, DirectoryNode):
                # Check if the path starts with this directory's path
                if path.startswith(child.path + "/"):
                    result = child.find_file(path)
                    if result:
                        return result
        return None


class ProjectStructure:
    """
    Represents the complete structure of a project.
    
    Attributes:
        project_type: The type of project
        description: Description of the project
        directories: List of directories in the project
        files: List of files in the project
    """
    
    def __init__(
        self,
        project_type: str,
        description: str = "",
        directories: Optional[List[str]] = None,
        files: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a ProjectStructure instance.
        
        Args:
            project_type: The type of project
            description: Description of the project
            directories: List of directories in the project
            files: List of file descriptors in the project
        """
        self.project_type = project_type
        self.description = description
        self.directories = directories or []
        self.files = files or []
        self._root = self._build_tree()
    
    def _build_tree(self) -> DirectoryNode:
        """Build a directory tree from the flat structure.
        
        Returns:
            The root directory node
        """
        root = DirectoryNode(".", "Project root")
        
        # Create directory nodes
        dir_nodes = {}
        for dir_path in self.directories:
            parts = dir_path.split("/")
            current_path = ""
            
            for i, part in enumerate(parts):
                parent_path = current_path
                current_path = current_path + ("/" if current_path else "") + part
                
                if current_path not in dir_nodes:
                    dir_node = DirectoryNode(current_path)
                    dir_nodes[current_path] = dir_node
                    
                    if i > 0 and parent_path in dir_nodes:
                        dir_nodes[parent_path].add_directory(dir_node)
                    elif i == 0:
                        root.add_directory(dir_node)
        
        # Create file nodes
        for file_info in self.files:
            file_path = file_info.get("path", "")
            file_node = FileNode(
                path=file_path,
                description=file_info.get("description", ""),
                components=file_info.get("components", [])
            )
            
            # Find the parent directory
            parent_path = str(Path(file_path).parent)
            if parent_path == ".":
                # File is in the root directory
                root.add_file(file_node)
            elif parent_path in dir_nodes:
                dir_nodes[parent_path].add_file(file_node)
            else:
                # Parent directory doesn't exist, add to root
                root.add_file(file_node)
        
        return root
    
    @property
    def root(self) -> DirectoryNode:
        """Get the root directory node.
        
        Returns:
            The root directory node
        """
        return self._root
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project structure to a dictionary.
        
        Returns:
            Dictionary representation of the project structure
        """
        return {
            "project_type": self.project_type,
            "description": self.description,
            "directories": self.directories,
            "files": self.files
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectStructure':
        """Create a ProjectStructure instance from a dictionary.
        
        Args:
            data: Dictionary containing project structure data
            
        Returns:
            A new ProjectStructure instance
        """
        return cls(
            project_type=data.get("project_type", ""),
            description=data.get("description", ""),
            directories=data.get("directories", []),
            files=data.get("files", [])
        )
    
    def find_file(self, path: str) -> Optional[FileNode]:
        """Find a file node by path.
        
        Args:
            path: The path to find
            
        Returns:
            The file node with the specified path, or None if not found
        """
        return self._root.find_file(path)
    
    def get_all_files(self) -> List[FileNode]:
        """Get all file nodes in the project.
        
        Returns:
            List of all file nodes
        """
        result = []
        
        def collect_files(node: Union[DirectoryNode, FileNode]) -> None:
            if isinstance(node, FileNode):
                result.append(node)
            elif isinstance(node, DirectoryNode):
                for child in node.children:
                    collect_files(child)
        
        collect_files(self._root)
        return result
    
    def get_all_nodes(self) -> List[Union[DirectoryNode, FileNode]]:
        """Get all nodes (files and directories) in the project.
        
        Returns:
            List of all nodes
        """
        result = []
        
        def collect_nodes(node: Union[DirectoryNode, FileNode]) -> None:
            result.append(node)
            if isinstance(node, DirectoryNode):
                for child in node.children:
                    collect_nodes(child)
        
        collect_nodes(self._root)
        return result
