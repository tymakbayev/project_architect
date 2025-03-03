import logging
import json
from typing import Dict, List, Any, Optional

from src.models.architecture_plan import ArchitecturePlan
from src.models.project_structure import ProjectStructure
from src.clients.anthropic_client import AnthropicClient
from src.config.config import Config


class ProjectStructureGenerator:
    """
    Generates project structure based on architecture plan.
    
    This class is responsible for generating a detailed project structure
    based on an architecture plan, including directories and files.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ProjectStructureGenerator.
        
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
    
    def generate_structure(self, architecture_plan: ArchitecturePlan, 
                          additional_context: Optional[Dict[str, Any]] = None) -> ProjectStructure:
        """
        Generate a project structure based on an architecture plan.
        
        Args:
            architecture_plan: The architecture plan for the project
            additional_context: Additional context for structure generation
            
        Returns:
            ProjectStructure: The generated project structure
        """
        self.logger.info("Generating project structure")
        
        # Prepare the prompt for Claude
        components_str = json.dumps([comp.to_dict() for comp in architecture_plan.components], indent=2)
        dependencies_str = json.dumps([dep.to_dict() for dep in architecture_plan.dependencies], indent=2)
        data_flows_str = json.dumps([flow.to_dict() for flow in architecture_plan.data_flows], indent=2)
        
        additional_context_str = ""
        if additional_context:
            additional_context_str = "Additional context:\n" + json.dumps(additional_context, indent=2)
        
        prompt = f"""
        You are an expert software architect. Based on the following architecture plan,
        generate a detailed project structure including directories and files.
        
        Project Type: {architecture_plan.project_type.name}
        
        Components:
        {components_str}
        
        Dependencies:
        {dependencies_str}
        
        Data Flows:
        {data_flows_str}
        
        {additional_context_str}
        
        Provide your response as a JSON object with the following structure:
        {{
            "directories": ["list", "of", "directory", "paths"],
            "files": [
                {{
                    "path": "path/to/file",
                    "description": "description of the file's purpose",
                    "components": ["list", "of", "components", "implemented", "in", "this", "file"]
                }}
            ]
        }}
        
        Consider standard project layouts for {architecture_plan.project_type.name} projects.
        Include all necessary files for a complete and working project.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response to extract the structure
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
                        result = {"directories": [], "files": []}
                else:
                    self.logger.error("Could not parse JSON from Claude's response")
                    result = {"directories": [], "files": []}
        
        # Create the project structure
        return ProjectStructure(
            project_type=architecture_plan.project_type.name,
            description=architecture_plan.description,
            directories=result.get("directories", []),
            files=result.get("files", [])
        )
    
    def generate_structure_from_description(self, project_name: str, 
                                           description: str) -> ProjectStructure:
        """
        Generate a project structure directly from a description.
        
        This is a convenience method that doesn't require an architecture plan.
        
        Args:
            project_name: Name of the project
            description: Description of the project
            
        Returns:
            ProjectStructure: The generated project structure
        """
        self.logger.info(f"Generating project structure for '{project_name}' from description")
        
        prompt = f"""
        You are an expert software architect. Based on the following project description,
        generate a detailed project structure including directories and files.
        
        Project Name: {project_name}
        
        Project Description:
        {description}
        
        Provide your response as a JSON object with the following structure:
        {{
            "project_type": "determined project type (e.g., python, react, node)",
            "directories": ["list", "of", "directory", "paths"],
            "files": [
                {{
                    "path": "path/to/file",
                    "description": "description of the file's purpose",
                    "components": ["list", "of", "components", "implemented", "in", "this", "file"]
                }}
            ]
        }}
        
        Consider standard project layouts for the determined project type.
        Include all necessary files for a complete and working project.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Parse the response
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            try:
                json_match = response.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_match)
            except (IndexError, json.JSONDecodeError):
                import re
                json_pattern = re.compile(r'\{.*\}', re.DOTALL)
                match = json_pattern.search(response)
                if match:
                    try:
                        result = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        self.logger.error("Could not parse JSON from Claude's response")
                        result = {"project_type": "unknown", "directories": [], "files": []}
                else:
                    self.logger.error("Could not parse JSON from Claude's response")
                    result = {"project_type": "unknown", "directories": [], "files": []}
        
        # Create the project structure
        return ProjectStructure(
            project_type=result.get("project_type", "unknown"),
            description=description,
            directories=result.get("directories", []),
            files=result.get("files", [])
        )
