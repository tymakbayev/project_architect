#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Project Analyzer Module.

This module is responsible for analyzing project descriptions to determine
the project type and extract key requirements using the Anthropic Claude API.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from anthropic import Anthropic

from src.models.project_type import ProjectType, ProjectTypeEnum
from src.clients.anthropic_client import AnthropicClient
from src.config.config import Config


class ProjectAnalyzer:
    """Analyzes project descriptions to determine project type and requirements.
    
    This class uses the Anthropic Claude API to analyze project descriptions
    and extract meaningful information about the project type and requirements.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the ProjectAnalyzer with an Anthropic client.
        
        Args:
            api_key: Optional Anthropic API key. If not provided, will attempt
                    to use the ANTHROPIC_API_KEY environment variable.
        """
        # Create a Config object and set the API key if provided
        config = Config()
        if api_key:
            config.anthropic_api_key = api_key
        
        self.anthropic_client = AnthropicClient(config)
        self.logger = logging.getLogger(__name__)

    def analyze_project_description(self, description: str) -> ProjectType:
        """Analyze the project description to determine its type.
        
        Args:
            description: The project description text
            
        Returns:
            ProjectType: The determined project type
            
        Raises:
            ValueError: If the project type cannot be determined
        """
        self.logger.info("Analyzing project description to determine type")
        
        prompt = f"""
        You are an expert software architect. Based on the following project description, 
        determine the most appropriate project type from these options:
        {', '.join([t.name for t in ProjectTypeEnum])}
        
        Project Description:
        {description}
        
        Respond with only the project type name and a brief explanation why you chose it.
        Format: PROJECT_TYPE: explanation
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Extract project type from response
        try:
            project_type_str = response.split(':', 1)[0].strip().upper()
            project_type = ProjectTypeEnum[project_type_str]
            explanation = response.split(':', 1)[1].strip() if ':' in response else ""
            
            return ProjectType(
                type_enum=project_type,
                description=explanation
            )
        except (KeyError, IndexError) as e:
            self.logger.error(f"Failed to determine project type: {e}")
            self.logger.debug(f"Claude response: {response}")
            raise ValueError(f"Could not determine project type from response: {response}") from e

    def extract_key_requirements(self, description: str) -> List[str]:
        """Extract key requirements from the project description.
        
        Args:
            description: The project description text
            
        Returns:
            List[str]: List of key requirements extracted from the description
        """
        self.logger.info("Extracting key requirements from project description")
        
        prompt = f"""
        You are an expert requirements analyst. Based on the following project description,
        extract a list of key functional and non-functional requirements.
        
        Project Description:
        {description}
        
        Format your response as a numbered list of requirements, with each requirement on a new line.
        Be specific and concise. Include both functional and technical requirements.
        """
        
        response = self.anthropic_client.generate_response(prompt)
        
        # Process the response to extract requirements as a list
        requirements = []
        for line in response.strip().split('\n'):
            # Remove numbering and leading/trailing whitespace
            cleaned_line = line.strip()
            if cleaned_line and any(c.isdigit() for c in cleaned_line[0:2]):
                # Remove the numbering (assumes format like "1. " or "1) ")
                requirement = cleaned_line.split(' ', 1)[1].strip() if ' ' in cleaned_line else cleaned_line
                requirements.append(requirement)
            elif cleaned_line and not cleaned_line.startswith('#') and len(cleaned_line) > 10:
                # Include lines that aren't headers and have substantial content
                requirements.append(cleaned_line)
        
        self.logger.info(f"Extracted {len(requirements)} requirements")
        return requirements
        
    def analyze(self, description: str) -> Tuple[str, List[str]]:
        """Analyze the project description to determine type and requirements.
        
        This is a convenience method that combines analyze_project_description
        and extract_key_requirements.
        
        Args:
            description: The project description text
            
        Returns:
            Tuple containing project type and list of requirements
        """
        project_type = self.analyze_project_description(description)
        requirements = self.extract_key_requirements(description)
        
        return project_type.name, requirements
