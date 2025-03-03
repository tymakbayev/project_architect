"""
Models package for Project Architect.

This package contains data models used throughout the application, defining
the structure and relationships of various components like project types,
architecture plans, project structures, code files, and dependencies.
"""

from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.models.project_structure import ProjectStructure, FileNode, DirectoryNode
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec

__all__ = [
    'ProjectType',
    'ProjectTypeEnum',
    'ArchitecturePlan',
    'Component',
    'Dependency',
    'DataFlow',
    'ProjectStructure',
    'FileNode',
    'DirectoryNode',
    'CodeFile',
    'DependencySpec',
]
