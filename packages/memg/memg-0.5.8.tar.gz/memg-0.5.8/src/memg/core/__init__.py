"""
Core integration layer for memg-core.
Provides clean interfaces to memg-core functionality with enhanced features.
"""

# Re-export key memg-core functions for convenience
from memg_core.api.public import (
    Memory,
    SearchResult,
    add_memory,
    create_memory_from_yaml,
    delete_memory,
    get_config,
    search,
)

__all__ = [
    "Memory",
    "SearchResult",
    "add_memory",
    "create_memory_from_yaml",
    "delete_memory",
    "get_config",
    "search",
]
