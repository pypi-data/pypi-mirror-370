# Google Gemini Embedding Support for MEMG

## Overview

MEMG now supports optional Google Gemini embeddings with automatic fallback to FastEmbed, providing users with enhanced embedding quality when they have a Google API key.

## Features

### ✅ **Automatic Detection & Fallback**
- **Auto-detects** `GOOGLE_API_KEY` environment variable
- **Prefers Gemini** when API key is available
- **Falls back to FastEmbed** when no API key is present
- **Graceful error handling** if API fails

### ✅ **Google Gemini Integration**
- **Model**: `gemini-embedding-001` (Google's latest embedding model)
- **Dimensions**: 768 (configurable from 768/1536/3072)
- **Quality**: High-quality semantic embeddings
- **Performance**: ~150ms API latency

### ✅ **FastEmbed Fallback**
- **Model**: `Snowflake/snowflake-arctic-embed-xs`
- **Dimensions**: 384
- **Local**: No API keys required
- **Fast**: Local processing

## Usage

### Environment Setup

```bash
# Optional: Set Google API key for enhanced embeddings
export GOOGLE_API_KEY="your_google_api_key_here"

# If not set, will automatically use FastEmbed
```

### Direct Usage

```python
from memg.ai.embedder_factory import create_embedder

# Creates best available embedder (Gemini if API key, else FastEmbed)
embedder = create_embedder()
print(f"Using: {embedder.model_name}")

# Generate embeddings
embedding = embedder.get_embedding("Hello, world!")
print(f"Dimensions: {len(embedding)}")
```

### Forced Selection

```python
from memg.ai.embedder_factory import force_gemini_embedder, force_fastembed_embedder

# Force Gemini (requires API key)
gemini_embedder = force_gemini_embedder()

# Force FastEmbed (always works)
fastembed_embedder = force_fastembed_embedder()
```

### Embedder Information

```python
from memg.ai.embedder_factory import get_embedder_info

info = get_embedder_info()
print(info)
# Output:
# {
#   'google_api_key_available': True,
#   'fastembed_available': True,
#   'preferred_embedder': 'gemini',
#   'current_embedder': 'GeminiEmbedder',
#   'current_model': 'gemini-embedding-001 (768d)',
#   'current_dimensions': 768
# }
```

## MCP Server Integration

The MCP server automatically uses the embedder factory and reports embedding status:

### Health Endpoint
```bash
curl http://localhost:8787/
```

Returns:
```json
{
  "status": "healthy",
  "service": "MEMG Core MCP v0.x.x",
  "features": [
    "deterministic_search",
    "ai_enhanced_search",
    "yaml_schema_driven",
    "optional_gemini_embedding"
  ],
  "embedding": {
    "google_api_key_available": true,
    "current_embedder": "GeminiEmbedder",
    "current_model": "gemini-embedding-001 (768d)",
    "current_dimensions": 768
  }
}
```

### Dynamic Dimension Handling
- **No more hardcoded 384 dimensions** in MCP server
- **Automatically detects** embedder dimensions
- **Adjusts vector operations** based on active embedder

## Architecture

### Class Hierarchy

```
Embedder Interface (memg-core)
├── Embedder (FastEmbed) - 384d
└── GeminiEmbedder - 768d
```

### Factory Pattern

```
EmbedderFactory
├── create_embedder() -> Auto-select best available
├── force_gemini_embedder() -> Force Gemini
├── force_fastembed_embedder() -> Force FastEmbed
└── get_embedder_info() -> Current status
```

## Files

- `src/memg/ai/gemini_embedder.py` - Google Gemini embedder implementation
- `src/memg/ai/embedder_factory.py` - Factory for embedder selection
- `tests/unit/test_gemini_embedder.py` - Comprehensive test suite
- `integrations/mcp/mcp_server.py` - Updated with dynamic dimension handling

## Configuration

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API access | Optional |
| `GEMINI_MODEL` | Override default model | Optional |

### Model Options

| Model | Dimensions | Notes |
|-------|------------|-------|
| `gemini-embedding-001` | 768/1536/3072 | Latest (default) |
| `text-embedding-004` | 768 | Older, more compatible |

## Testing

### Unit Tests
```bash
cd tests/unit
python test_gemini_embedder.py
```

### Integration Test (requires API key)
```bash
GOOGLE_API_KEY=your_key python test_gemini_embedder.py
```

### MCP Server Test
```bash
PYTHONPATH=src python -c "
from integrations.mcp.mcp_server import get_embedder_info
print(get_embedder_info())
"
```

## Benefits

### With Google API Key
- ✅ **Higher quality embeddings** from Google's latest model
- ✅ **768 dimensions** for better semantic understanding
- ✅ **Cloud-based** - no local model loading
- ✅ **Regularly updated** by Google

### Without Google API Key
- ✅ **No API costs** - completely free
- ✅ **Local processing** - no external dependencies
- ✅ **Fast startup** - no API key validation
- ✅ **Privacy** - no data sent to external services

## Migration

Existing MEMG installations automatically benefit from this enhancement:

1. **No breaking changes** - existing code works unchanged
2. **Automatic detection** - just set `GOOGLE_API_KEY` to upgrade
3. **Transparent fallback** - removes API key to downgrade
4. **Dynamic adaptation** - MCP server adjusts automatically

## Performance Comparison

| Metric | FastEmbed | Gemini |
|--------|-----------|--------|
| Dimensions | 384 | 768 |
| Quality | Good | Excellent |
| Latency | ~10ms | ~150ms |
| Cost | Free | API usage |
| Setup | None | API key |
| Privacy | Local | Cloud |

Choose based on your needs:
- **FastEmbed**: Privacy, speed, no costs
- **Gemini**: Quality, latest models, cloud-powered

---

## Summary

MEMG now provides **best-of-both-worlds** embedding support:
- **Automatic upgrade** to Gemini when API key is available
- **Seamless fallback** to FastEmbed when not
- **Zero configuration** required for basic usage
- **Full transparency** about which embedder is active

Set `GOOGLE_API_KEY` to unlock enhanced embedding quality, or use MEMG as-is with the reliable FastEmbed fallback! 🚀
