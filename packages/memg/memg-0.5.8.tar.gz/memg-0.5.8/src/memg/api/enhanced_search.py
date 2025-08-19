"""
Enhanced search entry point for MEMG.
Provides AI-enhanced query processing on top of memg-core's deterministic foundation.
"""

from typing import Any

from ..search import EnhancedSearchResult, create_search_orchestrator


def search_enhanced(
    user_query: str,
    user_id: str,
    yaml_schema_path: str,
    limit_per_subquery: int = 10,
) -> list[EnhancedSearchResult]:
    """
    Enhanced search that transforms free-form queries into structured deterministic searches.

    This is the main entry point for AI-enhanced search in MEMG.

    Args:
        user_query: Free-form user query (e.g., "all tasks related to memg project development")
        user_id: User ID for filtering results
        limit_per_subquery: Maximum results per sub-query (default: 10)
        yaml_schema_path: Path to YAML schema file

    Returns:
        List of enhanced search results with metadata

    Example:
        >>> results = search_enhanced("bugs and solutions for authentication", "cursor")
        >>> for result in results:
        ...     print(f"{result.memory_type}: {result.payload['statement']}")
        ...     print(f"  Score: {result.score}, Reasoning: {result.sub_query_reasoning}")
    """
    orchestrator = create_search_orchestrator(yaml_schema_path)
    return orchestrator.search_enhanced(user_query, user_id, limit_per_subquery)


def analyze_query(user_query: str, yaml_schema_path: str) -> dict[str, Any]:
    """
    Analyze a query without executing searches.
    Useful for understanding how AI will process the query.

    Args:
        user_query: Free-form user query
        yaml_schema_path: Path to YAML schema file

    Returns:
        Query analysis including corrected query, intent, and planned sub-queries

    Example:
        >>> analysis = analyze_query("all tasks related to memg proiject development")
        >>> print(analysis['corrected_query'])
        "all tasks related to memg project development"
        >>> print(analysis['sub_queries'][0]['memory_type'])
        "task"
    """
    orchestrator = create_search_orchestrator(yaml_schema_path)
    return orchestrator.get_search_metadata(user_query)


# For backward compatibility and convenience
enhanced_search = search_enhanced
