"""
AI-powered processing layer for MEMG.
Provides intelligent enhancements on top of memg-core's deterministic foundation.
"""

from .genai import GenAI

__all__: list[str] = [
    "GenAI",
]
