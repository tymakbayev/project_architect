#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the AnthropicClient module.

This module contains tests for the AnthropicClient class, which is responsible for
interacting with the Anthropic Claude API to generate responses for project analysis
and code generation.
"""

import json
import os
import pytest
from unittest import mock
from typing import Dict, Any, List, Optional

from src.clients.anthropic_client import AnthropicClient
from src.clients.base_client import BaseClient, ClientError


class TestAnthropicClient:
    """Test suite for the AnthropicClient class."""

    @pytest.fixture
    def api_key(self):
        """Return a dummy API key for testing."""
        return "test_api_key"

    @pytest.fixture
    def anthropic_client(self, api_key):
        """Create an AnthropicClient instance for testing."""
        return AnthropicClient(api_key=api_key)

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object for testing."""
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is a test response from Claude."
                }
            ],
            "model": "claude-3-opus-20240229",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50
            }
        }
        return mock_resp

    @pytest.fixture
    def mock_error_response(self):
        """Create a mock error response for testing."""
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {
            "error": {
                "type": "invalid_request_error",
                "message": "API key is invalid"
            }
        }
        return mock_resp

    def test_init(self, api_key):
        """Test the initialization of AnthropicClient."""
        client = AnthropicClient(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://api.anthropic.com/v1/messages"
        assert client.model == "claude-3-opus-20240229"
        assert isinstance(client, BaseClient)

        # Test with custom model
        custom_model = "claude-3-sonnet-20240229"
        client = AnthropicClient(api_key=api_key, model=custom_model)
        assert client.model == custom_model

        # Test with environment variable
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env_api_key"}):
            client = AnthropicClient()
            assert client.api_key == "env_api_key"

        # Test with no API key
        with pytest.raises(ValueError):
            with mock.patch.dict(os.environ, {}, clear=True):
                AnthropicClient()

    def test_build_headers(self, anthropic_client):
        """Test the build_headers method."""
        headers = anthropic_client._build_headers()
        assert headers["x-api-key"] == "test_api_key"
        assert headers["anthropic-version"] == "2023-06-01"
        assert headers["content-type"] == "application/json"

    def test_build_payload(self, anthropic_client):
        """Test the build_payload method."""
        system_prompt = "You are a helpful assistant."
        user_prompt = "Tell me about Python."
        max_tokens = 1000
        temperature = 0.7

        payload = anthropic_client._build_payload(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        assert payload["model"] == anthropic_client.model
        assert payload["system"] == system_prompt
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == user_prompt
        assert payload["max_tokens"] == max_tokens
        assert payload["temperature"] == temperature

        # Test with default values
        payload = anthropic_client._build_payload(
            user_prompt=user_prompt
        )
        assert payload["max_tokens"] == 4000
        assert payload["temperature"] == 0.5

    @mock.patch("requests.post")
    def test_generate_response_success(self, mock_post, anthropic_client, mock_response):
        """Test the generate_response method with a successful response."""
        mock_post.return_value = mock_response
        
        system_prompt = "You are a helpful assistant."
        user_prompt = "Tell me about Python."
        
        response = anthropic_client.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Verify the response
        assert response == "This is a test response from Claude."
        
        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == anthropic_client.base_url
        assert kwargs["headers"]["x-api-key"] == anthropic_client.api_key
        assert json.loads(kwargs["data"])["system"] == system_prompt
        assert json.loads(kwargs["data"])["messages"][0]["content"] == user_prompt

    @mock.patch("requests.post")
    def test_generate_response_error(self, mock_post, anthropic_client, mock_error_response):
        """Test the generate_response method with an error response."""
        mock_post.return_value = mock_error_response
        
        with pytest.raises(ClientError) as excinfo:
            anthropic_client.generate_response(
                user_prompt="Tell me about Python."
            )
        
        assert "API key is invalid" in str(excinfo.value)
        assert mock_post.called

    @mock.patch("requests.post")
    def test_generate_response_exception(self, mock_post, anthropic_client):
        """Test the generate_response method when an exception occurs."""
        mock_post.side_effect = Exception("Connection error")
        
        with pytest.raises(ClientError) as excinfo:
            anthropic_client.generate_response(
                user_prompt="Tell me about Python."
            )
        
        assert "Connection error" in str(excinfo.value)
        assert mock_post.called

    @mock.patch("requests.post")
    def test_generate_response_empty_content(self, mock_post, anthropic_client):
        """Test the generate_response method with empty content in response."""
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [],  # Empty content
            "model": "claude-3-opus-20240229"
        }
        mock_post.return_value = mock_resp
        
        with pytest.raises(ClientError) as excinfo:
            anthropic_client.generate_response(
                user_prompt="Tell me about Python."
            )
        
        assert "Empty response content from Anthropic API" in str(excinfo.value)

    @mock.patch("requests.post")
    def test_generate_json_response(self, mock_post, anthropic_client):
        """Test the generate_json_response method."""
        # Mock response with JSON string
        json_content = {"name": "Project Architect", "type": "CLI Tool"}
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(json_content)
                }
            ],
            "model": "claude-3-opus-20240229"
        }
        mock_post.return_value = mock_resp
        
        result = anthropic_client.generate_json_response(
            user_prompt="Generate a JSON description of the project."
        )
        
        assert result == json_content
        assert isinstance(result, dict)
        assert result["name"] == "Project Architect"
        assert result["type"] == "CLI Tool"

    @mock.patch("requests.post")
    def test_generate_json_response_invalid_json(self, mock_post, anthropic_client):
        """Test the generate_json_response method with invalid JSON."""
        # Mock response with invalid JSON string
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is not a valid JSON string"
                }
            ],
            "model": "claude-3-opus-20240229"
        }
        mock_post.return_value = mock_resp
        
        with pytest.raises(ClientError) as excinfo:
            anthropic_client.generate_json_response(
                user_prompt="Generate a JSON description of the project."
            )
        
        assert "Failed to parse JSON response" in str(excinfo.value)

    @mock.patch("requests.post")
    def test_generate_structured_response(self, mock_post, anthropic_client):
        """Test the generate_structured_response method."""
        # Define a schema for testing
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "features": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["name", "version", "features"]
        }
        
        # Mock response with valid structured data
        structured_content = {
            "name": "Project Architect",
            "version": "1.0.0",
            "features": ["Code generation", "Architecture planning"]
        }
        
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(structured_content)
                }
            ],
            "model": "claude-3-opus-20240229"
        }
        mock_post.return_value = mock_resp
        
        result = anthropic_client.generate_structured_response(
            user_prompt="Generate project details.",
            schema=schema
        )
        
        assert result == structured_content
        assert result["name"] == "Project Architect"
        assert result["version"] == "1.0.0"
        assert "Code generation" in result["features"]

    @mock.patch("requests.post")
    def test_generate_structured_response_invalid_schema(self, mock_post, anthropic_client):
        """Test the generate_structured_response method with invalid schema validation."""
        # Define a schema for testing
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "features": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["name", "version", "features"]
        }
        
        # Mock response with invalid structured data (missing required field)
        invalid_content = {
            "name": "Project Architect",
            # Missing "version" field
            "features": ["Code generation", "Architecture planning"]
        }
        
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "msg_123456",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(invalid_content)
                }
            ],
            "model": "claude-3-opus-20240229"
        }
        mock_post.return_value = mock_resp
        
        with pytest.raises(ClientError) as excinfo:
            anthropic_client.generate_structured_response(
                user_prompt="Generate project details.",
                schema=schema
            )
        
        assert "Response does not match the required schema" in str(excinfo.value)

    def test_extract_text_from_response(self, anthropic_client):
        """Test the _extract_text_from_response method."""
        # Test with valid response
        response_data = {
            "content": [
                {"type": "text", "text": "First part. "},
                {"type": "text", "text": "Second part."}
            ]
        }
        result = anthropic_client._extract_text_from_response(response_data)
        assert result == "First part. Second part."
        
        # Test with empty content
        response_data = {"content": []}
        with pytest.raises(ClientError):
            anthropic_client._extract_text_from_response(response_data)
        
        # Test with non-text content
        response_data = {
            "content": [
                {"type": "image", "source": "url"}
            ]
        }
        with pytest.raises(ClientError):
            anthropic_client._extract_text_from_response(response_data)
        
        # Test with mixed content
        response_data = {
            "content": [
                {"type": "text", "text": "Text content. "},
                {"type": "image", "source": "url"},
                {"type": "text", "text": "More text."}
            ]
        }
        result = anthropic_client._extract_text_from_response(response_data)
        assert result == "Text content. More text."


if __name__ == "__main__":
    pytest.main(["-v", __file__])