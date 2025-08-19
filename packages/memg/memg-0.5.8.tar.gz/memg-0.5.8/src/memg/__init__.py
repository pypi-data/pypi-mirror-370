"""
MEMG - Memory Management for AI Agents
Built on memg-core with AI-enhanced features and rich developer experience.

Architecture:
- memg-core: Deterministic foundation (storage, search, schemas)
- MEMG: Enhanced APIs, search orchestration, and utilities
"""

# Version is automatically managed by setuptools_scm from git tags
try:
    from importlib.metadata import version

    __version__ = version("memg")
except ImportError:
    __version__ = "0.0.0+unknown"
__title__ = "MEMG"
__description__ = "True memory for AI - lightweight, generalist, AI-made, AI-focused"

# Core integration layer
# AI enhancement layer
from .ai import GenAI
from .api import analyze_query, search_enhanced
from .core import (
    Memory,
    SearchResult,
    add_memory,
    create_memory_from_yaml,
    delete_memory,
    get_config,
    search,
)

__all__ = [
    "GenAI",
    "Memory",
    "SearchResult",
    "add_memory",
    "analyze_query",
    "create_memory_from_yaml",
    "delete_memory",
    "get_config",
    "search",
    "search_enhanced",
]
