import logging
import json
from typing import Dict, List, Any, Optional, Union

from src.models.project_type import ProjectType
from src.models.architecture_plan import ArchitecturePlan
from src.clients.anthropic_client import AnthropicClient
from src.config.config import Config


class DependencyManager:
    """
    Manages project dependencies based on project type and architecture.
    
    This class is responsible for determining and managing the dependencies
    required for a project based on its type and architecture plan.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DependencyManager.
        
        Args:
            api_key: Optional Anthropic API key. If not provided, will use
                    the ANTHROPIC_API_KEY environment variable.
        """
        # Create a Config object and set the API key if provided
        config = Config()
        if api_key:
            config.anthropic_api_key = api_key
            
        self.anthropic_client = AnthropicClient(config)
        self.logger = logging.getLogger(__name__)
        self.dependency_templates = self._load_dependency_templates()
    
    def _load_dependency_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load predefined dependency templates for common project types.
        
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
    
    def determine_dependencies(self, project_type: Union[ProjectType, str], 
                             architecture_plan: ArchitecturePlan) -> List[str]:
        """
        Determine dependencies for a project based on its type and architecture.
        
        Args:
            project_type: The type of the project
            architecture_plan: The architecture plan of the project
            
        Returns:
            List of dependencies
        """
        project_type_name = project_type.name if isinstance(project_type, ProjectType) else project_type
        self.logger.info(f"Determining dependencies for {project_type_name} project")
        
        # Prepare the prompt for Claude
        components_str = json.dumps([comp.to_dict() for comp in architecture_plan.components], indent=2)
        
        prompt = f"""
        You are an expert in software dependencies. Based on the following project type and architecture components,
        determine the necessary dependencies for the project.
        
        Project Type: {project_type_name}
        
        Architecture Components:
        {components_str}
        
        List all required dependencies for this project, including:
        1. Core dependencies for the main functionality
        2. Testing dependencies
        3. Development dependencies
        
        Format your response as a JSON object with 'main', 'test', and 'dev' lists of dependencies.
        Each dependency should be a string in the format appropriate for the project type.
        For example, for Python: 'flask==2.0.1', for Node.js: 'express': '^4.17.1'
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response to extract dependencies
        try:
            # Try to parse the entire response as JSON
            result = json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response
            try:
                # Look for JSON between triple backticks
                json_match = response.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_match)
            except (IndexError, json.JSONDecodeError):
                # Try finding JSON object using regex-like approach
                import re
                json_pattern = re.compile(r'\{.*\}', re.DOTALL)
                match = json_pattern.search(response)
                if match:
                    try:
                        result = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        self.logger.error("Could not parse JSON from Claude's response")
                        result = {"main": [], "test": [], "dev": []}
                else:
                    self.logger.error("Could not parse JSON from Claude's response")
                    result = {"main": [], "test": [], "dev": []}
        
        # Combine all dependencies into a flat list
        all_deps = []
        for category in ["main", "test", "dev"]:
            all_deps.extend(result.get(category, []))
        
        self.logger.info(f"Determined {len(all_deps)} dependencies")
        return all_deps
    
    def generate_dependency_files(self, dependencies: List[str]) -> Dict[str, str]:
        """
        Generate dependency files based on the list of dependencies.
        
        Args:
            dependencies: List of dependencies
            
        Returns:
            Dictionary mapping file paths to file content
        """
        self.logger.info("Generating dependency files")
        
        # This is a simplified implementation
        # In a real implementation, you would generate appropriate files
        # based on the project type (requirements.txt, package.json, etc.)
        
        # Check if we can determine the project type from dependencies
        project_type = self._determine_project_type_from_dependencies(dependencies)
        
        files = {}
        
        if project_type == "python":
            # Generate requirements.txt
            requirements = "\n".join(dependencies)
            files["requirements.txt"] = requirements
        
        elif project_type == "node" or project_type == "javascript":
            # Generate package.json
            package_json = {
                "name": "project",
                "version": "1.0.0",
                "description": "Generated project",
                "main": "index.js",
                "scripts": {
                    "start": "node index.js",
                    "test": "jest"
                },
                "dependencies": {},
                "devDependencies": {}
            }
            
            # Parse dependencies
            for dep in dependencies:
                if ":" in dep:
                    name, version = dep.split(":", 1)
                    name = name.strip().strip('"\'')
                    version = version.strip().strip('"\',')
                    package_json["dependencies"][name] = version
                else:
                    package_json["dependencies"][dep] = "latest"
            
            files["package.json"] = json.dumps(package_json, indent=2)
        
        self.logger.info(f"Generated {len(files)} dependency files")
        return files
    
    def _determine_project_type_from_dependencies(self, dependencies: List[str]) -> str:
        """
        Determine the project type based on dependencies.
        
        Args:
            dependencies: List of dependencies
            
        Returns:
            Project type (python, node, etc.)
        """
        # Check for Python-specific dependencies
        python_keywords = ["flask", "django", "sqlalchemy", "pandas", "pytest", "requests"]
        if any(dep.split("==")[0].lower() in python_keywords for dep in dependencies):
            return "python"
        
        # Check for Node/JavaScript-specific dependencies
        node_keywords = ["express", "react", "vue", "angular", "jest", "webpack"]
        if any(dep.split(":")[0].strip().lower() in node_keywords for dep in dependencies):
            return "node"
        
        # Default to python if we can't determine
        return "python"
