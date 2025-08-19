"""
Search orchestrator that executes multiple deterministic searches and aggregates results.
"""

import os
from dataclasses import dataclass
from typing import Any

from memg_core.api.public import SearchResult
from memg_core.api.public import search as memg_core_search

from ..utils.schema import create_schema_converter


@dataclass
class EnhancedSearchResult:
    """Enhanced search result with metadata."""

    # Original SearchResult data
    memory_id: str
    hrid: str
    memory_type: str
    payload: dict[str, Any]
    score: float
    source: str

    # Enhancement metadata
    sub_query_index: int
    sub_query_reasoning: str
    search_terms: str
    priority: str = "medium"

    @classmethod
    def from_search_result(
        cls,
        search_result: SearchResult,
        sub_query_index: int,
        reasoning: str,
        search_terms: str,
        priority: str = "medium",
    ) -> "EnhancedSearchResult":
        """Create from memg-core SearchResult."""
        return cls(
            memory_id=search_result.memory.id,
            hrid=search_result.memory.hrid,
            memory_type=search_result.memory.memory_type,
            payload=search_result.memory.payload,
            score=search_result.score,
            source=search_result.source,
            sub_query_index=sub_query_index,
            sub_query_reasoning=reasoning,
            search_terms=search_terms,
            priority=priority,
        )


class SearchOrchestrator:
    """Orchestrates AI-enhanced query processing and deterministic search execution."""

    def __init__(self, yaml_schema_path: str):
        """
        Initialize the search orchestrator.

        Args:
            yaml_schema_path: Path to YAML schema file
        """
        self.schema_converter = create_schema_converter(yaml_schema_path)

        # Check if AI is enabled
        self.use_ai = os.getenv("USE_AI", "true").lower() not in (
            "false",
            "0",
            "no",
            "off",
        )

        if self.use_ai:
            # Import GenAI only when needed
            from ..ai.genai import GenAI

            # Create AI instance for query enhancement
            prompt = self.schema_converter.create_query_enhancement_prompt()
            self.ai = GenAI(system_instruction=prompt)

            # Get JSON schema for structured responses
            self.enhancement_schema = (
                self.schema_converter.create_query_enhancement_schema()
            )

    def enhance_query(self, user_query: str) -> dict[str, Any]:
        """
        Enhance a free-form query using AI.

        Args:
            user_query: Free-form user query

        Returns:
            Enhanced query structure with sub-queries
        """
        if not self.use_ai:
            raise RuntimeError("AI features are disabled. Set USE_AI=true to enable.")

        return self.ai.generate_json(user_query, self.enhancement_schema)

    def execute_deterministic_search(
        self, memory_type: str, search_terms: str, user_id: str, limit: int = 10
    ) -> list[SearchResult]:
        """
        Execute deterministic search using memg-core.

        Args:
            memory_type: Memory type to search
            search_terms: Search terms
            user_id: User ID for filtering
            limit: Maximum results

        Returns:
            List of search results
        """
        # Use memg-core's deterministic search
        # Use the memo_type parameter instead of filters for memory type filtering
        results = memg_core_search(
            query=search_terms, user_id=user_id, limit=limit, memo_type=memory_type
        )
        return list(results)

    def search_enhanced(
        self, user_query: str, user_id: str, limit_per_subquery: int = 10
    ) -> list[EnhancedSearchResult]:
        """
        Execute enhanced search: AI processing + deterministic search.

        Args:
            user_query: Free-form user query
            user_id: User ID for filtering
            limit_per_subquery: Max results per sub-query

        Returns:
            List of enhanced search results
        """
        if not self.use_ai:
            raise RuntimeError(
                "AI features are disabled. Set USE_AI=true to enable enhanced search."
            )

        # Step 1: AI Enhancement
        enhanced = self.enhance_query(user_query)

        # Step 2: Execute deterministic searches
        all_results = []

        for i, sub_query in enumerate(enhanced["sub_queries"]):
            memory_type = sub_query["memory_type"]
            search_terms = sub_query["search_terms"]
            reasoning = sub_query["reasoning"]
            priority = sub_query.get("priority", "medium")

            # Execute search
            search_results = self.execute_deterministic_search(
                memory_type=memory_type,
                search_terms=search_terms,
                user_id=user_id,
                limit=limit_per_subquery,
            )

            # Convert to enhanced results
            for result in search_results:
                enhanced_result = EnhancedSearchResult.from_search_result(
                    search_result=result,
                    sub_query_index=i,
                    reasoning=reasoning,
                    search_terms=search_terms,
                    priority=priority,
                )
                all_results.append(enhanced_result)

        # Step 3: Sort by priority and score
        priority_order = {"high": 3, "medium": 2, "low": 1}
        all_results.sort(
            key=lambda r: (priority_order.get(r.priority, 2), r.score), reverse=True
        )

        return all_results

    def get_search_metadata(self, user_query: str) -> dict[str, Any]:
        """
        Get search metadata without executing actual searches.
        Useful for debugging and understanding AI analysis.

        Args:
            user_query: Free-form user query

        Returns:
            Enhanced query analysis
        """
        if not self.use_ai:
            raise RuntimeError(
                "AI features are disabled. Set USE_AI=true to enable search metadata."
            )

        return self.enhance_query(user_query)


def create_search_orchestrator(
    yaml_schema_path: str,
) -> SearchOrchestrator:
    """
    Create a search orchestrator instance.

    Args:
        yaml_schema_path: Path to YAML schema file

    Returns:
        SearchOrchestrator instance
    """
    return SearchOrchestrator(yaml_schema_path)
