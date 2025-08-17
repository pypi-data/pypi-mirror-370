"""
Pytest configuration and shared fixtures for MEMG test suite.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_config_dir(project_root):
    """Return the test configuration directory."""
    return project_root / "config"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test_api_key",
            "MEMG_TEST_MODE": "true",
        },
    ):
        yield


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "memo": {"statement": "Test memo statement", "project": "memg"},
        "document": {
            "statement": "Test document statement",
            "details": "Detailed documentation content",
            "project": "memg",
            "url": "https://example.com/doc",
        },
        "task": {
            "statement": "Test task statement",
            "assignee": "developer",
            "status": "in_progress",
            "priority": "high",
            "project": "memg",
        },
        "note": {
            "statement": "Test note statement",
            "details": "Note details content",
            "project": "memg",
        },
        "bug": {
            "statement": "Test bug statement",
            "details": "Bug reproduction steps",
            "severity": "medium",
            "status": "open",
            "project": "memg",
        },
        "solution": {
            "statement": "Test solution statement",
            "details": "Solution implementation details",
            "approach": "algorithmic",
            "test_status": "passed",
            "project": "memg",
        },
    }


@pytest.fixture
def mock_genai_response():
    """Mock GenAI response for testing."""
    return {
        "original_query": "test query",
        "corrected_query": "test query",
        "analysis": {
            "intent": "Testing query analysis",
            "complexity": "simple",
            "confidence": 0.95,
        },
        "sub_queries": [
            {
                "memory_type": "task",
                "search_terms": "test query",
                "reasoning": "This is a test query for task retrieval",
                "priority": "high",
            }
        ],
    }


@pytest.fixture
def mock_memg_core():
    """Mock memg-core functionality for isolated testing."""
    with (
        patch("memg.core.search") as mock_search,
        patch("memg.core.add_memory") as mock_add,
        patch("memg.core.delete_memory") as mock_delete,
    ):
        # Configure mock search results
        mock_search.return_value = [
            Mock(
                memory_id="test-id-1",
                memory_type="task",
                payload={"statement": "Test task", "project": "memg"},
                score=0.9,
            )
        ]

        # Configure mock add memory
        mock_add.return_value = Mock(memory_id="new-test-id")

        # Configure mock delete
        mock_delete.return_value = True

        yield {
            "search": mock_search,
            "add_memory": mock_add,
            "delete_memory": mock_delete,
        }


@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration for testing."""
    return """
entity_types:
  memo:
    description: "Basic memory unit for storing simple facts or observations"
    required_fields: ["statement"]
    optional_fields: ["project"]
    anchor_field: "statement"

  task:
    description: "Development tasks, work items, or action items"
    required_fields: ["statement"]
    optional_fields: ["assignee", "status", "priority", "project"]
    anchor_field: "statement"

  solution:
    description: "Solutions, fixes, or implementation approaches"
    required_fields: ["statement", "details"]
    optional_fields: ["approach", "test_status", "project"]
    anchor_field: "statement"
"""


# Pytest markers for test organization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
    config.addinivalue_line(
        "markers", "requires_api: Tests that require external API access"
    )


# Skip tests that require API keys if not available
def pytest_runtest_setup(item):
    """Setup function to skip tests based on markers and environment."""
    if item.get_closest_marker("requires_api"):
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("Test requires GOOGLE_API_KEY environment variable")
