import logging
import json
from typing import Dict, List, Any, Optional, Union

from src.models.architecture_plan import ArchitecturePlan
from src.models.project_structure import ProjectStructure
from src.models.code_file import CodeFile
from src.clients.anthropic_client import AnthropicClient
from src.config.config import Config


class CodeGenerator:
    """
    Generates code files based on project structure and architecture plan.
    
    This class is responsible for generating actual code files based on
    the project structure and architecture plan.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CodeGenerator.
        
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
    
    def generate_code(self, project_structure: ProjectStructure, 
                     architecture_plan: ArchitecturePlan,
                     additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate code for all files in the project structure.
        
        Args:
            project_structure: The project structure
            architecture_plan: The architecture plan
            additional_context: Additional context for code generation
            
        Returns:
            Dictionary mapping file paths to code content
        """
        self.logger.info("Generating code files")
        
        code_files = {}
        
        for file_info in project_structure.files:
            file_path = file_info.get("path", "")
            file_description = file_info.get("description", "")
            file_components = file_info.get("components", [])
            
            # Skip files without paths
            if not file_path:
                continue
            
            self.logger.debug(f"Generating code for {file_path}")
            
            # Generate code for the file
            try:
                code = self._generate_file_code(
                    file_path=file_path,
                    file_description=file_description,
                    file_components=file_components,
                    project_structure=project_structure,
                    architecture_plan=architecture_plan,
                    additional_context=additional_context
                )
                
                code_files[file_path] = code
            except Exception as e:
                self.logger.error(f"Error generating code for {file_path}: {e}")
                # Provide a placeholder for files that couldn't be generated
                code_files[file_path] = f"# Error generating code: {e}\n# File: {file_path}\n# Description: {file_description}"
        
        self.logger.info(f"Generated {len(code_files)} code files")
        return code_files
    
    def _generate_file_code(self, file_path: str, file_description: str, 
                           file_components: List[str], project_structure: ProjectStructure,
                           architecture_plan: ArchitecturePlan,
                           additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate code for a single file.
        
        Args:
            file_path: Path to the file
            file_description: Description of the file
            file_components: Components implemented in the file
            project_structure: The project structure
            architecture_plan: The architecture plan
            additional_context: Additional context for code generation
            
        Returns:
            The generated code as a string
        """
        # Determine the programming language based on file extension
        extension = file_path.split(".")[-1] if "." in file_path else ""
        language = self._get_language_from_extension(extension)
        
        # Extract components that should be implemented in this file
        component_details = []
        for component_name in file_components:
            component = next((c for c in architecture_plan.components if c.name == component_name), None)
            if component:
                component_details.append(component.to_dict())
        
        # Prepare the prompt for Claude
        prompt = f"""
        You are an expert software developer. Generate code for the following file in a project:
        
        Project Type: {project_structure.project_type}
        File Path: {file_path}
        File Description: {file_description}
        Programming Language: {language}
        
        This file implements the following components:
        {json.dumps(component_details, indent=2) if component_details else "No specific components"}
        
        Project Structure:
        Directories: {json.dumps(project_structure.directories, indent=2)}
        
        Provide ONLY the code for the file, no explanations. 
        Write clean, well-documented, high-quality code following best practices for {language}.
        """
        
        if additional_context:
            prompt += f"\n\nAdditional Context:\n{json.dumps(additional_context, indent=2)}"
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Extract the code from the response
        code = self._extract_code_from_response(response, language)
        
        return code
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """
        Extract code from Claude's response.
        
        Args:
            response: Claude's response
            language: The programming language
            
        Returns:
            The extracted code
        """
        # Check for code blocks
        language_markers = {
            "python": ["```python", "```"],
            "javascript": ["```javascript", "```", "```js", "```"],
            "typescript": ["```typescript", "```", "```ts", "```"],
            "html": ["```html", "```"],
            "css": ["```css", "```"],
            "json": ["```json", "```"],
            "sql": ["```sql", "```"],
            "bash": ["```bash", "```", "```sh", "```"],
            "dockerfile": ["```dockerfile", "```"],
            "yaml": ["```yaml", "```", "```yml", "```"],
            "markdown": ["```markdown", "```", "```md", "```"],
        }
        
        # Get markers for the language
        markers = language_markers.get(language.lower(), ["```", "```"])
        
        # Check all possible markers
        for start_marker in markers[:-1]:
            if start_marker in response:
                start_idx = response.find(start_marker) + len(start_marker)
                end_marker = markers[-1]
                end_idx = response.find(end_marker, start_idx)
                
                if end_idx != -1:
                    return response[start_idx:end_idx].strip()
        
        # If no code block found, return the full response
        return response.strip()
    
    def _get_language_from_extension(self, extension: str) -> str:
        """
        Determine the programming language from a file extension.
        
        Args:
            extension: The file extension
            
        Returns:
            The programming language name
        """
        extension_map = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "html": "html",
            "css": "css",
            "scss": "css",
            "sass": "css",
            "json": "json",
            "md": "markdown",
            "yml": "yaml",
            "yaml": "yaml",
            "sql": "sql",
            "sh": "bash",
            "bash": "bash",
            "dockerfile": "dockerfile",
            "Dockerfile": "dockerfile",
            "java": "java",
            "kt": "kotlin",
            "rb": "ruby",
            "php": "php",
            "c": "c",
            "cpp": "cpp",
            "cs": "csharp",
            "go": "go",
            "rs": "rust",
            "swift": "swift",
            "txt": "text",
            "xml": "xml",
            "ini": "ini",
            "cfg": "ini",
            "conf": "ini",
            "env": "env",
        }
        
        return extension_map.get(extension.lower(), "text")
    
    def get_files(self, project_structure: Union[ProjectStructure, Any], 
                 architecture_plan: Union[ArchitecturePlan, Any]) -> Dict[str, str]:
        """
        Get generated files for a project.
        
        This is a stub method for the interface that should be implemented.
        
        Args:
            project_structure: The project structure
            architecture_plan: The architecture plan
            
        Returns:
            Dictionary mapping file paths to code content
        """
        # In a real implementation, this would retrieve stored files
        # Here we just return an empty dictionary
        return {}
