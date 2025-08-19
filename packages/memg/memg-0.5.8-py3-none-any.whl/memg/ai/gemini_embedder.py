"""
Google Gemini Embedder for MEMG

Provides embedding functionality using Google's Gemini embedding models
as an alternative to FastEmbed for users who have Google API keys.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class GeminiEmbedder:
    """
    Google Gemini embedder using gemini-embedding-001 model.

    Compatible with memg-core's Embedder interface but uses Google's
    embedding API instead of local FastEmbed models.

    Features:
    - Uses gemini-embedding-001 model by default (configurable via GEMINI_EMBEDDING_MODEL)
    - 768-dimensional vectors by default (configurable via GEMINI_EMBEDDER_DIMENSION)
    - Batch processing support
    - Automatic API key detection (GOOGLE_API_KEY)
    - Compatible with existing memg-core interfaces
    - Controlled by USE_AI environment variable
    """

    def __init__(
        self,
        model: str | None = None,
        output_dimensionality: int | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize Google Gemini embedder.

        Args:
            model: Gemini embedding model to use (auto-detected from GEMINI_EMBEDDING_MODEL, defaults to gemini-embedding-001)
            output_dimensionality: Vector dimensions (auto-detected from GEMINI_EMBEDDER_DIMENSION, defaults to 768)
            api_key: Google API key (auto-detected from GOOGLE_API_KEY if not provided)
        """
        self.model = model or os.getenv(
            "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
        )
        self.output_dimensionality = output_dimensionality or int(
            os.getenv("GEMINI_EMBEDDER_DIMENSION", "768")
        )

        # Get API key
        final_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not final_api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Create client
        self.client = genai.Client(api_key=final_api_key, vertexai=False)

        # Validate output dimensionality
        valid_dimensions = [768, 1536, 3072]
        if self.output_dimensionality not in valid_dimensions:
            raise ValueError(
                f"output_dimensionality must be one of {valid_dimensions}, "
                f"got {self.output_dimensionality}"
            )

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0]

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors, one per input text
        """
        if not texts:
            return []

        # Create embedding config
        config = types.EmbedContentConfig(
            output_dimensionality=self.output_dimensionality
        )

        # Call Google Gemini embedding API
        response = self.client.models.embed_content(
            model=self.model,  # type: ignore
            contents=texts,  # type: ignore
            config=config,
        )

        # Extract embeddings from response
        embeddings = []
        if response.embeddings:
            for embedding_data in response.embeddings:
                if embedding_data.values:
                    embeddings.append(embedding_data.values)
                else:
                    embeddings.append([0.0] * self.output_dimensionality)

        return embeddings

    @property
    def model_name(self) -> str:
        """Get the model name for compatibility with memg-core interface."""
        return f"{self.model} ({self.output_dimensionality}d)"

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.output_dimensionality

    def __repr__(self) -> str:
        return f"GeminiEmbedder(model={self.model}, dimensions={self.output_dimensionality})"


def create_gemini_embedder_if_available() -> GeminiEmbedder | None:
    """
    Create a Gemini embedder if Google API key is available.

    Returns:
        GeminiEmbedder instance if API key is available, None otherwise
    """
    if os.getenv("GOOGLE_API_KEY"):
        try:
            return GeminiEmbedder()
        except Exception:
            # API key might be invalid or API might be down
            return None
    return None


def is_gemini_embedding_available() -> bool:
    """
    Check if Google Gemini embedding is available.

    Returns:
        True if GOOGLE_API_KEY is set, False otherwise
    """
    return bool(os.getenv("GOOGLE_API_KEY"))
