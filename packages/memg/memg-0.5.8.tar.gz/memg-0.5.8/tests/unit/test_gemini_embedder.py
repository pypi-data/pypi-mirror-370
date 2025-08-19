#!/usr/bin/env python3
"""
Tests for Google Gemini embedder functionality.

Tests the GeminiEmbedder class and embedder factory with both
unit tests (mocked) and integration tests (requires API key).
"""

import os
import pytest
from unittest.mock import Mock, patch

# Test imports
try:
    from src.memg.ai.gemini_embedder import GeminiEmbedder, create_gemini_embedder_if_available, is_gemini_embedding_available
    from src.memg.ai.embedder_factory import create_embedder, get_embedder_info
    GEMINI_IMPORTS_AVAILABLE = True
except ImportError:
    GEMINI_IMPORTS_AVAILABLE = False


class TestGeminiEmbedder:
    """Test Google Gemini embedder functionality."""

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_gemini_embedder_init_without_api_key(self):
        """Test that GeminiEmbedder raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Google API key required"):
                GeminiEmbedder()

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_gemini_embedder_init_with_api_key(self):
        """Test GeminiEmbedder initialization with API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client"):
                embedder = GeminiEmbedder()
                assert embedder.model == "gemini-embedding-001"
                assert embedder.output_dimensionality == 768
                assert embedder.dimension == 768

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_gemini_embedder_invalid_dimensions(self):
        """Test that invalid dimensions raise error."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client"):
                with pytest.raises(ValueError, match="output_dimensionality must be one of"):
                    GeminiEmbedder(output_dimensionality=512)

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_gemini_embedder_get_embedding(self):
        """Test single embedding generation."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client") as mock_client:
                # Mock the embedding response
                mock_response = Mock()
                mock_response.embeddings = [Mock(values=[0.1] * 768)]
                mock_client.return_value.models.embed_content.return_value = mock_response

                embedder = GeminiEmbedder()
                embedding = embedder.get_embedding("test text")

                assert len(embedding) == 768
                assert embedding == [0.1] * 768

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_gemini_embedder_get_embeddings_batch(self):
        """Test batch embedding generation."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client") as mock_client:
                # Mock the embedding response for batch
                mock_response = Mock()
                mock_response.embeddings = [
                    Mock(values=[0.1] * 768),
                    Mock(values=[0.2] * 768)
                ]
                mock_client.return_value.models.embed_content.return_value = mock_response

                embedder = GeminiEmbedder()
                embeddings = embedder.get_embeddings(["text1", "text2"])

                assert len(embeddings) == 2
                assert len(embeddings[0]) == 768
                assert len(embeddings[1]) == 768
                assert embeddings[0] == [0.1] * 768
                assert embeddings[1] == [0.2] * 768

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_is_gemini_embedding_available(self):
        """Test availability detection."""
        # Test with API key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            assert is_gemini_embedding_available() is True

        # Test without API key
        with patch.dict(os.environ, {}, clear=True):
            assert is_gemini_embedding_available() is False

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_create_gemini_embedder_if_available(self):
        """Test conditional embedder creation."""
        # Test with API key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client"):
                embedder = create_gemini_embedder_if_available()
                assert embedder is not None
                assert isinstance(embedder, GeminiEmbedder)

        # Test without API key
        with patch.dict(os.environ, {}, clear=True):
            embedder = create_gemini_embedder_if_available()
            assert embedder is None


class TestEmbedderFactory:
    """Test embedder factory functionality."""

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_create_embedder_prefers_gemini(self):
        """Test that factory prefers Gemini when available."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client"):
                with patch("builtins.print"):  # Suppress print output
                    embedder = create_embedder(prefer_gemini=True)
                    assert type(embedder).__name__ == "GeminiEmbedder"

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_create_embedder_falls_back_to_fastembed(self):
        """Test fallback to FastEmbed when Gemini fails."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.print"):  # Suppress print output
                embedder = create_embedder(prefer_gemini=True)
                # Should fall back to FastEmbed (memg-core Embedder)
                assert hasattr(embedder, "get_embedding")

    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_get_embedder_info(self):
        """Test embedder info retrieval."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            with patch("google.genai.Client"):
                with patch("builtins.print"):  # Suppress print output
                    info = get_embedder_info()

                    assert "google_api_key_available" in info
                    assert "fastembed_available" in info
                    assert "preferred_embedder" in info
                    assert info["google_api_key_available"] is True
                    assert info["fastembed_available"] is True


class TestIntegration:
    """Integration tests requiring actual API key."""

    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY")
    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_real_gemini_embedding(self):
        """Test real Gemini embedding (requires API key)."""
        embedder = GeminiEmbedder()

        # Test single embedding
        embedding = embedder.get_embedding("Hello, world!")
        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)

        # Test batch embeddings
        embeddings = embedder.get_embeddings(["Hello", "World"])
        assert len(embeddings) == 2
        assert all(len(emb) == 768 for emb in embeddings)

    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY")
    @pytest.mark.skipif(not GEMINI_IMPORTS_AVAILABLE, reason="Gemini embedder not available")
    def test_embedder_factory_with_real_api(self):
        """Test embedder factory with real API."""
        with patch("builtins.print"):  # Suppress print output
            embedder = create_embedder()

            # Should create Gemini embedder with real API key
            assert type(embedder).__name__ == "GeminiEmbedder"

            # Test it works
            embedding = embedder.get_embedding("test")
            assert len(embedding) == 768


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Testing Gemini embedder functionality...")

    if not GEMINI_IMPORTS_AVAILABLE:
        print("❌ Gemini embedder imports not available")
        exit(1)

    # Test availability detection
    has_api_key = is_gemini_embedding_available()
    print(f"📊 Google API key available: {has_api_key}")

    if has_api_key:
        try:
            # Test real embedder creation
            embedder = GeminiEmbedder()
            print(f"✅ Created Gemini embedder: {embedder}")

            # Test embedding
            embedding = embedder.get_embedding("test")
            print(f"✅ Generated embedding: {len(embedding)} dimensions")

        except Exception as e:
            print(f"❌ Gemini embedder test failed: {e}")
    else:
        print("⚠️  No Google API key - testing factory fallback")
        try:
            with patch("builtins.print"):
                embedder = create_embedder()
            print(f"✅ Factory created embedder: {type(embedder).__name__}")
        except Exception as e:
            print(f"❌ Factory test failed: {e}")

    print("🎉 Gemini embedder tests completed!")
