import logging
from typing import Dict, List, Any, Optional
import json

from src.clients.anthropic_client import AnthropicClient
from src.models.project_type import ProjectType
from src.models.architecture_plan import ArchitecturePlan

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages project dependencies based on project type and architecture.
    
    This class is responsible for determining and managing the dependencies
    required for a project based on its type and architecture plan.
    """
    
    def __init__(self, anthropic_client: AnthropicClient):
        """Initialize the DependencyManager.
        
        Args:
            anthropic_client: Client for interacting with Anthropic's Claude API
        """
        self.anthropic_client = anthropic_client
        self.dependency_templates = self._load_dependency_templates()
    
    def _load_dependency_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load predefined dependency templates for common project types.
        
        Returns:
            Dictionary mapping project types to their common dependencies
        """
        # This could be loaded from a JSON file in a real implementation
        return {
            "python": {
                "web": ["flask", "requests", "sqlalchemy", "pytest"],
                "data_science": ["numpy", "pandas", "scikit-learn", "matplotlib"],
                "cli": ["click", "rich", "pyyaml"]
            },
            "javascript": {
                "react": ["react", "react-dom", "react-router-dom", "axios"],
                "node": ["express", "mongoose", "dotenv", "jest"]
            },
            "java": {
                "spring": ["spring-boot-starter-web", "spring-boot-starter-data-jpa", "h2"],
                "android": ["androidx.appcompat:appcompat", "com.google.android.material:material"]
            }
        }
    
    def generate_dependencies(self, project_type: ProjectType, architecture_plan: ArchitecturePlan) -> Dict[str, List[str]]:
        """Generate dependencies for a project based on its type and architecture.
        
        Args:
            project_type: The type of the project
            architecture_plan: The architecture plan of the project
            
        Returns:
            Dictionary mapping dependency types to lists of dependencies
        """
        logger.info(f"Generating dependencies for {project_type.name} project")
        
        # Start with base dependencies from templates if available
        base_dependencies = self._get_base_dependencies(project_type)
        
        # Get additional dependencies based on architecture analysis
        additional_dependencies = self._analyze_architecture_for_dependencies(project_type, architecture_plan)
        
        # Merge dependencies
        dependencies = self._merge_dependencies(base_dependencies, additional_dependencies)
        
        # Format dependencies according to project type
        formatted_dependencies = self._format_dependencies(project_type, dependencies)
        
        return formatted_dependencies
    
    def _get_base_dependencies(self, project_type: ProjectType) -> Dict[str, List[str]]:
        """Get base dependencies for a project type from templates.
        
        Args:
            project_type: The type of the project
            
        Returns:
            Dictionary of base dependencies
        """
        result = {"main": [], "dev": []}
        
        # Get dependencies from templates if available
        templates = self.dependency_templates.get(project_type.name.lower(), {})
        if templates:
            for category, deps in templates.items():
                if category in project_type.subtypes:
                    result["main"].extend(deps)
        
        return result
    
    def _analyze_architecture_for_dependencies(self, project_type: ProjectType, architecture_plan: ArchitecturePlan) -> Dict[str, List[str]]:
        """Analyze the architecture plan to determine additional dependencies.
        
        Args:
            project_type: The type of the project
            architecture_plan: The architecture plan of the project
            
        Returns:
            Dictionary of additional dependencies based on architecture
        """
        # Prepare the prompt for Claude
        components_str = json.dumps(architecture_plan.components, indent=2)
        data_flows_str = json.dumps(architecture_plan.data_flows, indent=2)
        
        prompt = f"""Based on the following project type and architecture plan, determine the necessary dependencies:
        
        Project Type: {project_type.name}
        Subtypes: {', '.join(project_type.subtypes)}
        
        Architecture Components:
        {components_str}
        
        Data Flows:
        {data_flows_str}
        
        Please analyze this architecture and provide:
        1. Main dependencies needed for production
        2. Development dependencies needed for testing, development, etc.
        
        Return your response as a JSON object with 'main' and 'dev' lists.
        """
        
        try:
            # Get dependencies from Claude
            dependencies_data = self.anthropic_client.analyze_with_claude(prompt, "dependencies")
            
            # Extract main and dev dependencies
            main_deps = dependencies_data.get("main", [])
            dev_deps = dependencies_data.get("dev", [])
            
            return {"main": main_deps, "dev": dev_deps}
        except Exception as e:
            logger.error(f"Error analyzing architecture for dependencies: {str(e)}")
            return {"main": [], "dev": []}
    
    def _merge_dependencies(self, base_deps: Dict[str, List[str]], additional_deps: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Merge base and additional dependencies, removing duplicates.
        
        Args:
            base_deps: Base dependencies from templates
            additional_deps: Additional dependencies from architecture analysis
            
        Returns:
            Merged dictionary of dependencies
        """
        result = {"main": [], "dev": []}
        
        # Add base dependencies
        for dep_type, deps in base_deps.items():
            result[dep_type].extend(deps)
        
        # Add additional dependencies, avoiding duplicates
        for dep_type, deps in additional_deps.items():
            for dep in deps:
                # Extract package name without version
                package_name = dep.split("==")[0].split(">=")[0].split("<=")[0].strip()
                
                # Check if package is already in the list
                existing_deps = [d.split("==")[0].split(">=")[0].split("<=")[0].strip() for d in result[dep_type]]
                if package_name not in existing_deps:
                    result[dep_type].append(dep)
        
        return result
    
    def _format_dependencies(self, project_type: ProjectType, dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Format dependencies according to project type conventions.
        
        Args:
            project_type: The type of the project
            dependencies: Dictionary of dependencies to format
            
        Returns:
            Formatted dictionary of dependencies
        """
        formatted = {}
        
        if project_type.name.lower() == "python":
            formatted["requirements.txt"] = dependencies["main"]
            formatted["dev-requirements.txt"] = dependencies["dev"]
        
        elif project_type.name.lower() in ["javascript", "typescript", "node"]:
            formatted["dependencies"] = dependencies["main"]
            formatted["devDependencies"] = dependencies["dev"]
        
        elif project_type.name.lower() == "java":
            # For Maven or Gradle projects
            formatted["dependencies"] = dependencies["main"]
            formatted["testDependencies"] = dependencies["dev"]
        
        else:
            # Default format
            formatted["main"] = dependencies["main"]
            formatted["dev"] = dependencies["dev"]
        
        return formatted