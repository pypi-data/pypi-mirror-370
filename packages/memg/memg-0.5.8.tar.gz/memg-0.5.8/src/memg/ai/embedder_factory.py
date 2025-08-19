"""
Embedder Factory for MEMG

Provides a factory function to create the best available embedder,
with automatic fallback from Google Gemini to FastEmbed based on
environment configuration.
"""

import os
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_embedder(prefer_gemini: bool = True) -> Any:
    """
    Create the best available embedder with automatic fallback.

    Priority order:
    1. Google Gemini (if GOOGLE_API_KEY is set, USE_AI is not false, and prefer_gemini=True)
    2. FastEmbed (memg-core default)

    Args:
        prefer_gemini: Whether to prefer Gemini over FastEmbed when both are available

    Returns:
        Embedder instance (either GeminiEmbedder or memg-core Embedder)
    """
    # Check for AI enablement, Google API key, and preference
    use_ai = os.getenv("USE_AI", "true").lower() not in ("false", "0", "no", "off")
    has_google_key = bool(os.getenv("GOOGLE_API_KEY"))

    if use_ai and has_google_key and prefer_gemini:
        try:
            from memg.ai.gemini_embedder import GeminiEmbedder  # type: ignore

            embedder = GeminiEmbedder()
            print(f"🤖 Using Google Gemini embedder: {embedder.model_name}")
            return embedder
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini embedder: {e}")
            print("🔄 Falling back to FastEmbed...")

    # Fallback to FastEmbed (memg-core default)
    try:
        from memg_core.core.interfaces.embedder import Embedder

        embedder = Embedder()
        print(f"🚀 Using FastEmbed embedder: {embedder.model_name}")
        return embedder
    except Exception as e:
        raise RuntimeError(f"Failed to initialize any embedder: {e}") from e


def get_embedder_info() -> dict[str, Any]:
    """
    Get information about available embedders.

    Returns:
        Dictionary with embedder availability and configuration info
    """
    use_ai = os.getenv("USE_AI", "true").lower() not in ("false", "0", "no", "off")
    has_google_key = bool(os.getenv("GOOGLE_API_KEY"))

    info = {
        "use_ai_enabled": use_ai,
        "google_api_key_available": has_google_key,
        "fastembed_available": True,  # Always available via memg-core
        "preferred_embedder": "gemini" if (use_ai and has_google_key) else "fastembed",
    }

    # Try to get current embedder details
    try:
        embedder = create_embedder()
        info.update(
            {
                "current_embedder": type(embedder).__name__,
                "current_model": getattr(embedder, "model_name", "unknown"),
                "current_dimensions": getattr(
                    embedder, "dimension", str(len(embedder.get_embedding("test")))
                ),
            }
        )
    except Exception as e:
        info["error"] = str(e)

    return info


def force_fastembed_embedder() -> Any:
    """
    Force creation of FastEmbed embedder, ignoring Gemini availability.

    Returns:
        FastEmbed Embedder instance
    """
    from memg_core.core.interfaces.embedder import Embedder

    embedder = Embedder()
    print(f"🚀 Using FastEmbed embedder (forced): {embedder.model_name}")
    return embedder


def force_gemini_embedder() -> Any:
    """
    Force creation of Gemini embedder, will fail if not available.

    Returns:
        GeminiEmbedder instance

    Raises:
        ValueError: If Google API key is not available
        RuntimeError: If Gemini embedder initialization fails
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Google API key required for Gemini embedder")

    from memg.ai.gemini_embedder import GeminiEmbedder

    embedder = GeminiEmbedder()
    print(f"🤖 Using Gemini embedder (forced): {embedder.model_name}")
    return embedder
