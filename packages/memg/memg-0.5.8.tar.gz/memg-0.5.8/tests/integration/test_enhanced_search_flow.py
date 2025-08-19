"""
Integration tests for the complete enhanced search flow.
Tests the full pipeline: query -> AI analysis -> search -> results
"""

import os
from unittest.mock import Mock, patch

import pytest

from memg import analyze_query, search_enhanced


class TestEnhancedSearchIntegration:
    """Integration tests for enhanced search functionality."""

    @pytest.fixture
    def mock_memg_core_integration(self):
        """Mock memg-core for integration testing with realistic responses."""
        with patch("memg.search.orchestrator.memg_core_search") as mock_search:
            # Setup realistic search results
            mock_results = [
                Mock(
                    memory_id="task-001",
                    memory_type="task",
                    payload={
                        "statement": "Implement user authentication system",
                        "assignee": "developer",
                        "status": "in_progress",
                        "project": "memg",
                    },
                    score=0.92,
                ),
                Mock(
                    memory_id="doc-001",
                    memory_type="document",
                    payload={
                        "statement": "Authentication design patterns documentation",
                        "details": "Comprehensive guide to authentication patterns",
                        "project": "memg",
                        "url": "https://example.com/auth-docs",
                    },
                    score=0.85,
                ),
            ]
            mock_search.return_value = mock_results
            yield mock_search

    @pytest.mark.integration
    @pytest.mark.requires_api
    @pytest.mark.skip(reason="Skipping real API test - requires valid GOOGLE_API_KEY")
    def test_full_search_flow_with_real_ai(
        self, mock_memg_core_integration, mock_env_vars
    ):
        """Test complete search flow with real AI (requires API key)."""
        query = "find tasks related to authentication development"
        user_id = "test_user"

        results = search_enhanced(query, user_id=user_id, yaml_schema_path="config/core.test.yaml", limit_per_subquery=5)

        # Verify we got results
        assert isinstance(results, list)

        # If we have results, verify their structure
        if results:
            for result in results:
                assert hasattr(result, "memory_id")
                assert hasattr(result, "memory_type")
                assert hasattr(result, "payload")
                assert hasattr(result, "score")
                assert hasattr(result, "sub_query_reasoning")
                assert hasattr(result, "search_terms")

    @pytest.mark.integration
    def test_search_flow_with_mock_ai(self, mock_memg_core_integration):
        """Test complete search flow with mocked AI responses."""
        # Mock the AI response for consistent testing
        mock_ai_response = {
            "original_query": "find authentication tasks",
            "corrected_query": "find authentication tasks",
            "analysis": {
                "intent": "Finding tasks related to authentication development",
                "complexity": "moderate",
                "confidence": 0.9,
            },
            "sub_queries": [
                {
                    "memory_type": "task",
                    "search_terms": "authentication development",
                    "reasoning": "Looking for development tasks related to authentication",
                    "priority": "high",
                },
                {
                    "memory_type": "document",
                    "search_terms": "authentication patterns design",
                    "reasoning": "Finding documentation about authentication patterns",
                    "priority": "medium",
                },
            ],
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            results = search_enhanced(
                "find authentication tasks", user_id="test_user", yaml_schema_path="config/core.test.yaml", limit_per_subquery=3
            )

            # Verify AI was called
            mock_genai.generate_json.assert_called()

            # Verify search was called for each sub-query
            assert mock_memg_core_integration.call_count == 2

            # Verify results structure
            assert isinstance(results, list)
            assert len(results) == 4  # 2 results × 2 sub-queries

            # Verify enhanced attributes are added
            for result in results:
                assert hasattr(result, "sub_query_index")
                assert hasattr(result, "sub_query_reasoning")
                assert hasattr(result, "search_terms")
                assert hasattr(result, "priority")

    @pytest.mark.integration
    def test_query_analysis_integration(self):
        """Test query analysis integration with schema converter."""
        mock_ai_response = {
            "original_query": "show me bug reports",
            "corrected_query": "show me bug reports",
            "analysis": {
                "intent": "Retrieving bug reports from memory",
                "complexity": "simple",
                "confidence": 0.95,
            },
            "sub_queries": [
                {
                    "memory_type": "bug",
                    "search_terms": "bug reports issues",
                    "reasoning": "User wants to see bug reports and issues",
                }
            ],
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            result = analyze_query("show me bug reports", yaml_schema_path="config/core.test.yaml")

            assert result == mock_ai_response
            assert result["analysis"]["intent"] == "Retrieving bug reports from memory"
            assert len(result["sub_queries"]) == 1
            assert result["sub_queries"][0]["memory_type"] == "bug"

    @pytest.mark.integration
    def test_multiple_memory_types_search(self, mock_memg_core_integration):
        """Test search across multiple memory types."""
        mock_ai_response = {
            "original_query": "engineering documentation and tasks",
            "corrected_query": "engineering documentation and tasks",
            "analysis": {"intent": "mixed content search", "confidence": 0.8},
            "sub_queries": [
                {
                    "memory_type": "document",
                    "search_terms": "engineering documentation",
                    "reasoning": "Finding engineering documents",
                },
                {
                    "memory_type": "task",
                    "search_terms": "engineering tasks",
                    "reasoning": "Finding engineering tasks",
                },
                {
                    "memory_type": "note",
                    "search_terms": "engineering notes",
                    "reasoning": "Finding engineering notes",
                },
            ],
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            results = search_enhanced("engineering docs and tasks", user_id="test_user", yaml_schema_path="config/core.test.yaml")

            # Should call search for each memory type
            assert mock_memg_core_integration.call_count == 3

            # Verify different memory types were searched
            search_calls = mock_memg_core_integration.call_args_list
            memory_types_searched = [
                call.kwargs.get("memo_type") for call in search_calls
            ]

            assert "document" in memory_types_searched
            assert "task" in memory_types_searched
            assert "note" in memory_types_searched

    @pytest.mark.integration
    def test_empty_search_results(self, mock_memg_core_integration):
        """Test handling of empty search results."""
        # Configure mock to return empty results
        mock_memg_core_integration.return_value = []

        mock_ai_response = {
            "sub_queries": [
                {
                    "memory_type": "task",
                    "search_terms": "nonexistent query",
                    "reasoning": "Testing empty results",
                }
            ]
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            results = search_enhanced("nonexistent query", user_id="test_user", yaml_schema_path="config/core.test.yaml")

            assert results == []

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_query_processing(self, mock_memg_core_integration):
        """Test processing of complex, multi-part queries."""
        complex_query = """
        Find all documentation about authentication systems,
        security implementation patterns, user management tasks,
        and any bug reports related to login functionality.
        Also show me solutions for common authentication issues.
        """

        mock_ai_response = {
            "original_query": complex_query,
            "corrected_query": complex_query.strip(),
            "analysis": {
                "intent": "Comprehensive authentication system research",
                "complexity": "high",
                "confidence": 0.85,
            },
            "sub_queries": [
                {
                    "memory_type": "document",
                    "search_terms": "authentication security documentation",
                    "reasoning": "Finding authentication documentation",
                },
                {
                    "memory_type": "task",
                    "search_terms": "user management authentication tasks",
                    "reasoning": "Finding user management tasks",
                },
                {
                    "memory_type": "bug",
                    "search_terms": "login authentication bug reports",
                    "reasoning": "Finding authentication bugs",
                },
                {
                    "memory_type": "solution",
                    "search_terms": "authentication issues solutions",
                    "reasoning": "Finding authentication solutions",
                },
            ],
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            results = search_enhanced(
                complex_query, user_id="test_user", yaml_schema_path="config/core.test.yaml", limit_per_subquery=2
            )

            # Should search all 4 memory types
            assert mock_memg_core_integration.call_count == 4

            # Should return combined results (2 per sub-query × 4 sub-queries = 8 total)
            assert len(results) == 8

    @pytest.mark.integration
    def test_error_recovery(self, mock_memg_core_integration):
        """Test error recovery in search flow."""

        # Configure one search to fail, others to succeed
        def side_effect(*args, **kwargs):
            if kwargs.get("memo_type") == "task":
                raise Exception("Search service temporarily unavailable")
            return [Mock(memory_id="test", score=0.8)]

        mock_memg_core_integration.side_effect = side_effect

        mock_ai_response = {
            "sub_queries": [
                {
                    "memory_type": "task",
                    "search_terms": "failing search",
                    "reasoning": "This will fail",
                },
                {
                    "memory_type": "document",
                    "search_terms": "working search",
                    "reasoning": "This will work",
                },
            ]
        }

        with patch("memg.ai.genai.GenAI") as mock_genai_class:
            mock_genai = Mock()
            mock_genai_class.return_value = mock_genai
            mock_genai.generate_json.return_value = mock_ai_response

            # The entire search should fail if any sub-query fails
            with pytest.raises(
                Exception, match="Search service temporarily unavailable"
            ):
                search_enhanced("test query", user_id="test_user", yaml_schema_path="config/core.test.yaml")
