"""
Unit tests for enhanced search API.
Tests main entry points and error handling.
"""

from unittest.mock import Mock, patch

import pytest

from memg.api.enhanced_search import search_enhanced, analyze_query


class TestEnhancedSearchAPI:
    """Unit tests for enhanced search API functions."""

    @patch("memg.api.enhanced_search.create_search_orchestrator")
    def test_search_enhanced_success(self, mock_orchestrator_factory):
        """Test successful enhanced search execution."""
        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.search_enhanced.return_value = [
            Mock(memory_id="1", memory_type="task", score=0.9, payload={"statement": "test"})
        ]
        mock_orchestrator_factory.return_value = mock_orchestrator

        result = search_enhanced("test query", "user123", "test.yaml", limit_per_subquery=5)

        assert len(result) == 1
        assert result[0].memory_id == "1"
        mock_orchestrator.search_enhanced.assert_called_once_with("test query", "user123", 5)

    @patch("memg.api.enhanced_search.create_search_orchestrator")
    def test_search_enhanced_error(self, mock_orchestrator_factory):
        """Test enhanced search with error."""
        mock_orchestrator_factory.side_effect = Exception("Orchestrator creation failed")

        with pytest.raises(Exception, match="Orchestrator creation failed"):
            search_enhanced("test query", "user123", "test.yaml")

    @patch("memg.api.enhanced_search.create_search_orchestrator")
    def test_analyze_query_success(self, mock_orchestrator_factory):
        """Test successful query analysis."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_search_metadata.return_value = {
            "intent": "search",
            "confidence": 0.95,
            "sub_queries": []
        }
        mock_orchestrator_factory.return_value = mock_orchestrator

        result = analyze_query("test query", "test.yaml")

        assert result["intent"] == "search"
        assert result["confidence"] == 0.95
        mock_orchestrator.get_search_metadata.assert_called_once_with("test query")

    @patch("memg.api.enhanced_search.create_search_orchestrator")
    def test_analyze_query_error(self, mock_orchestrator_factory):
        """Test query analysis with error."""
        mock_orchestrator_factory.side_effect = ValueError("Invalid schema path")

        with pytest.raises(ValueError, match="Invalid schema path"):
            analyze_query("test query", "invalid.yaml")
