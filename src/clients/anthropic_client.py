import os
import json
from typing import Dict, Optional, Any, List, Union
import logging
import anthropic
from anthropic.types import MessageParam

from src.config.config import Config

logger = logging.getLogger(__name__)

class AnthropicClient:
    """Client for interacting with Anthropic's Claude API.
    
    This class provides methods to communicate with Claude for various
    project generation tasks such as analyzing project descriptions,
    generating architecture plans, and creating code.
    """
    
    def __init__(self, config: Config):
        """Initialize the Anthropic client with configuration.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model = config.anthropic_model or "claude-3-opus-20240229"
        self.max_tokens = config.anthropic_max_tokens or 4096
    
    def ask_claude(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send a prompt to Claude and get a response.
        
        Args:
            prompt: The user prompt to send to Claude
            system_prompt: Optional system prompt to guide Claude's behavior
            
        Returns:
            Claude's response as a string
        """
        try:
            system = system_prompt or "You are a helpful AI assistant specializing in software development."
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error communicating with Claude: {str(e)}")
            raise
    
    def analyze_with_claude(self, data: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze data using Claude and return structured results.
        
        Args:
            data: The data to analyze
            analysis_type: Type of analysis to perform (e.g., 'project_type', 'architecture')
            
        Returns:
            Dictionary containing the analysis results
        """
        system_prompts = {
            "project_type": "You are an expert software architect. Analyze the project description and determine the most appropriate project type and technologies.",
            "architecture": "You are an expert software architect. Create a detailed architecture plan based on the project description.",
            "dependencies": "You are an expert in software dependencies. Determine the necessary dependencies for the given project type and architecture."
        }
        
        prompt_templates = {
            "project_type": "Analyze the following project description and determine the project type and main technologies that should be used:\n\n{data}\n\nRespond in JSON format with 'project_type' and 'technologies' keys.",
            "architecture": "Create a detailed architecture plan for the following project description:\n\n{data}\n\nRespond in JSON format with components, their responsibilities, and relationships.",
            "dependencies": "Determine the necessary dependencies for a {project_type} project with the following architecture plan:\n\n{data}\n\nRespond in JSON format with a list of dependencies and their versions."
        }
        
        if analysis_type not in system_prompts:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        system_prompt = system_prompts[analysis_type]
        prompt = prompt_templates[analysis_type].format(data=data)
        
        # Add instruction to format response as JSON
        prompt += "\n\nProvide your response in valid JSON format."
        
        response = self.ask_claude(prompt, system_prompt)
        
        # Extract JSON from the response
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
                # If all parsing attempts fail, return the raw response
                logger.warning(f"Could not parse JSON from Claude's response for {analysis_type}")
                result = {"raw_response": response}
        
        return result