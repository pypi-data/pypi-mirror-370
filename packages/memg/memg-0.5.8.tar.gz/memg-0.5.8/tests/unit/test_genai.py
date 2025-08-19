"""
Unit tests for the GenAI module.
Tests AI client initialization, query analysis, and error handling.
"""

import os
from unittest.mock import Mock, patch

import pytest

from memg.ai.genai import GenAI


class TestGenAI:
    """Unit tests for GenAI client functionality."""

    def test_init_with_api_key(self):
        """Test GenAI client initialization with API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}), \
             patch("memg.ai.genai.genai.Client"):
            client = GenAI("test instruction")
            assert client.model == "gemini-2.0-flash"

    def test_init_with_custom_model(self):
        """Test GenAI client initialization with custom model."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}), \
             patch("memg.ai.genai.genai.Client"):
            client = GenAI("test instruction", model="gemini-pro")
            assert client.model == "gemini-pro"

    @patch("memg.ai.genai.genai.Client")
    def test_generate_json_success(self, mock_client_class):
        """Test successful JSON generation."""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.parsed = {"result": "success"}
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            client = GenAI("test instruction")
            result = client.generate_json("test content", {"type": "object"})

            assert result == {"result": "success"}
            mock_client.models.generate_content.assert_called_once()

    @patch("memg.ai.genai.genai.Client")
    def test_generate_text_success(self, mock_client_class):
        """Test successful text generation."""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated text response"
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            client = GenAI("test instruction")
            result = client.generate_text("test content")

            assert result == "Generated text response"
            mock_client.models.generate_content.assert_called_once()
