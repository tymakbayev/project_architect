"""
Core package for Project Architect.

This package contains the core functionality for analyzing project descriptions,
generating architecture plans, project structures, code, and managing dependencies.
"""

from typing import List, Dict, Any, Optional

# Import core components
from src.core.project_analyzer import ProjectAnalyzer
from src.core.architecture_generator import ArchitectureGenerator
from src.core.project_structure_generator import ProjectStructureGenerator
from src.core.code_generator import CodeGenerator
from src.core.dependency_manager import DependencyManager

# Import models that are used by core components
from src.models.project_type import ProjectType, ProjectTypeEnum
from src.models.architecture_plan import ArchitecturePlan, Component, Dependency, DataFlow
from src.models.project_structure import ProjectStructure, FileNode, DirectoryNode
from src.models.code_file import CodeFile
from src.models.dependency_spec import DependencySpec

# Setup package-level logger
import logging
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()

__all__ = [
    'ProjectAnalyzer',
    'ArchitectureGenerator',
    'ProjectStructureGenerator',
    'CodeGenerator',
    'DependencyManager',
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


class CorePipeline:
    """Orchestrates the core generation pipeline for project creation.
    
    This class provides a convenient way to run the entire generation pipeline
    from project analysis to code generation in a single workflow.
    """
    
    def __init__(
        self,
        project_analyzer: Optional[ProjectAnalyzer] = None,
        architecture_generator: Optional[ArchitectureGenerator] = None,
        structure_generator: Optional[ProjectStructureGenerator] = None,
        code_generator: Optional[CodeGenerator] = None,
        dependency_manager: Optional[DependencyManager] = None,
        anthropic_api_key: Optional[str] = None
    ) -> None:
        """Initialize the CorePipeline with optional component instances.
        
        If components are not provided, they will be created with the given API key.
        
        Args:
            project_analyzer: Optional ProjectAnalyzer instance
            architecture_generator: Optional ArchitectureGenerator instance
            structure_generator: Optional ProjectStructureGenerator instance
            code_generator: Optional CodeGenerator instance
            dependency_manager: Optional DependencyManager instance
            anthropic_api_key: Optional Anthropic API key to use for all components
        """
        self.project_analyzer = project_analyzer or ProjectAnalyzer(anthropic_api_key)
        self.architecture_generator = architecture_generator or ArchitectureGenerator(anthropic_api_key)
        self.structure_generator = structure_generator or ProjectStructureGenerator(anthropic_api_key)
        self.code_generator = code_generator or CodeGenerator(anthropic_api_key)
        self.dependency_manager = dependency_manager or DependencyManager(anthropic_api_key)
        self.logger = logging.getLogger(__name__)
    
    def generate_project(
        self, 
        project_name: str, 
        project_description: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the complete project generation pipeline.
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
            additional_context: Optional additional context for generation
            
        Returns:
            Dict containing all generated artifacts:
                - project_type: The determined ProjectType
                - requirements: List of extracted requirements
                - architecture: The generated ArchitecturePlan
                - structure: The generated ProjectStructure
                - code_files: List of generated CodeFile objects
                - dependencies: List of generated DependencySpec objects
        """
        self.logger.info(f"Starting project generation pipeline for '{project_name}'")
        
        # Step 1: Analyze project description
        project_type = self.project_analyzer.analyze_project_description(project_description)
        self.logger.info(f"Determined project type: {project_type.type_enum.name}")
        
        # Step 2: Extract requirements
        requirements = self.project_analyzer.extract_key_requirements(project_description)
        self.logger.info(f"Extracted {len(requirements)} requirements")
        
        # Step 3: Generate architecture plan
        architecture = self.architecture_generator.generate_architecture(project_type, requirements)
        self.logger.info(f"Generated architecture with {len(architecture.components)} components")
        
        # Step 4: Generate project structure
        structure = self.structure_generator.generate_structure(
            project_name=project_name,
            architecture=architecture,
            additional_context=additional_context
        )
        self.logger.info(f"Generated project structure")
        
        # Step 5: Generate code files
        code_files = self.code_generator.generate_code_files(
            project_name=project_name,
            architecture=architecture,
            structure=structure,
            additional_context=additional_context
        )
        self.logger.info(f"Generated {len(code_files)} code files")
        
        # Step 6: Generate dependencies
        dependencies = self.dependency_manager.generate_dependencies(
            project_type=project_type,
            architecture=architecture,
            code_files=code_files
        )
        self.logger.info(f"Generated {len(dependencies)} dependencies")
        
        # Return all generated artifacts
        return {
            "project_type": project_type,
            "requirements": requirements,
            "architecture": architecture,
            "structure": structure,
            "code_files": code_files,
            "dependencies": dependencies
        }