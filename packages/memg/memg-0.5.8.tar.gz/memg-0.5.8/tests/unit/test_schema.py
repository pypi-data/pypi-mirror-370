"""
Unit tests for schema utilities.
Tests YAML schema loading, conversion, and validation.
"""

from unittest.mock import Mock, patch

import pytest

from memg.utils.schema import SchemaConverter, create_schema_converter


class TestSchemaUtilities:
    """Unit tests for schema utility functions."""

    @patch("memg.utils.schema.YamlTranslator")
    def test_schema_converter_init(self, mock_translator_class):
        """Test SchemaConverter initialization."""
        mock_translator = Mock()
        mock_translator.schema = {"entities": []}
        mock_translator_class.return_value = mock_translator

        converter = SchemaConverter("test.yaml")
        assert converter.translator == mock_translator

    @patch("memg.utils.schema.YamlTranslator")
    def test_get_memory_types(self, mock_translator_class):
        """Test getting memory types from schema."""
        mock_translator = Mock()
        mock_translator.schema = {
            "entities": [
                {"name": "task"},
                {"name": "note"}
            ]
        }
        mock_translator_class.return_value = mock_translator

        converter = SchemaConverter("test.yaml")
        types = converter.get_memory_types()

        assert types == ["task", "note"]

    @patch("memg.utils.schema.YamlTranslator")
    def test_get_memory_type_descriptions(self, mock_translator_class):
        """Test getting memory type descriptions."""
        mock_translator = Mock()
        mock_translator.schema = {
            "entities": [
                {"name": "task", "description": "A task item"},
                {"name": "note", "description": "A note item"}
            ]
        }
        mock_translator_class.return_value = mock_translator

        converter = SchemaConverter("test.yaml")
        descriptions = converter.get_memory_type_descriptions()

        assert descriptions == {"task": "A task item", "note": "A note item"}

    @patch("memg.utils.schema.YamlTranslator")
    def test_create_query_enhancement_schema(self, mock_translator_class):
        """Test creating query enhancement schema."""
        mock_translator = Mock()
        mock_translator.schema = {
            "entities": [
                {"name": "task"},
                {"name": "note"}
            ]
        }
        mock_translator_class.return_value = mock_translator

        converter = SchemaConverter("test.yaml")
        schema = converter.create_query_enhancement_schema()

        assert "properties" in schema
        assert "sub_queries" in schema["properties"]
        assert schema["properties"]["sub_queries"]["items"]["properties"]["memory_type"]["enum"] == ["task", "note"]

    def test_create_schema_converter(self):
        """Test schema converter factory function."""
        with patch("memg.utils.schema.YamlTranslator"):
            converter = create_schema_converter("test.yaml")
            assert isinstance(converter, SchemaConverter)
