"""
MEMG API Module - Public Interface Layer

This module provides the main public API for MEMG's AI-enhanced search capabilities.
It serves as the primary entry point for external consumers.
"""

from .enhanced_search import analyze_query, search_enhanced

__all__: list[str] = [
    "analyze_query",
    "search_enhanced",
]
