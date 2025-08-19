"""
Sample data for testing MEMG functionality.
"""

# Sample memory data for different types
SAMPLE_MEMORIES = {
    "memo": [
        {"statement": "MEMG uses dual storage with Qdrant and Kuzu", "project": "memg"},
        {
            "statement": "Enhanced search uses Google Gemini 2.0 Flash for query analysis",
            "project": "memg",
        },
    ],
    "document": [
        {
            "statement": "MEMG Architecture Documentation",
            "details": "Comprehensive documentation of MEMG's dual storage architecture using Qdrant for vectors and Kuzu for graph relationships.",
            "project": "memg",
            "url": "https://github.com/memg/docs/architecture",
        },
        {
            "statement": "Enhanced Search API Reference",
            "details": "Complete API reference for MEMG's enhanced search capabilities including query analysis and result ranking.",
            "project": "memg",
        },
    ],
    "task": [
        {
            "statement": "Implement comprehensive test infrastructure",
            "assignee": "developer",
            "status": "in_progress",
            "priority": "high",
            "project": "memg",
            "story_points": 8,
        },
        {
            "statement": "Add code quality tools (Ruff, MyPy, Bandit)",
            "assignee": "developer",
            "status": "pending",
            "priority": "medium",
            "project": "memg",
            "story_points": 5,
        },
    ],
    "note": [
        {
            "statement": "Testing Strategy for MEMG",
            "details": "Unit tests for individual components, integration tests for AI workflows, and end-to-end tests for complete search flows.",
            "project": "memg",
        },
        {
            "statement": "Performance Optimization Ideas",
            "details": "Consider caching AI analysis results, batch processing for multiple queries, and connection pooling for database operations.",
            "project": "memg",
        },
    ],
    "bug": [
        {
            "statement": "Search results not properly sorted by relevance",
            "details": "Enhanced search returns results in incorrect order, affecting user experience.",
            "severity": "medium",
            "status": "open",
            "project": "memg",
            "file_path": "src/memg/ai/search_orchestrator.py",
        },
        {
            "statement": "Memory type validation fails for edge cases",
            "details": "Schema converter doesn't handle empty or malformed YAML configurations properly.",
            "severity": "low",
            "status": "closed",
            "project": "memg",
        },
    ],
    "solution": [
        {
            "statement": "Fix search result sorting by implementing proper score comparison",
            "details": "Modify SearchOrchestrator to sort results by score in descending order before returning.",
            "approach": "algorithmic",
            "code_snippet": "results.sort(key=lambda x: x.score, reverse=True)",
            "test_status": "passed",
            "project": "memg",
        },
        {
            "statement": "Add YAML validation to schema converter initialization",
            "details": "Implement comprehensive validation of YAML structure and required fields during SchemaConverter initialization.",
            "approach": "defensive_programming",
            "test_status": "pending",
            "project": "memg",
        },
    ],
}

# Sample AI responses for testing
SAMPLE_AI_RESPONSES = {
    "simple_analysis": {
        "original_query": "find tasks",
        "corrected_query": "find tasks",
        "analysis": {
            "intent": "Retrieving development tasks",
            "complexity": "simple",
            "confidence": 0.9,
        },
        "sub_queries": [
            {
                "memory_type": "task",
                "search_terms": "development tasks",
                "reasoning": "User wants to find development tasks",
                "priority": "high",
            }
        ],
    },
    "complex_analysis": {
        "original_query": "bugs and solutions for authentication issues",
        "corrected_query": "bugs and solutions for authentication issues",
        "analysis": {
            "intent": "Finding bugs and their solutions related to authentication",
            "complexity": "moderate",
            "confidence": 0.85,
        },
        "sub_queries": [
            {
                "memory_type": "bug",
                "search_terms": "authentication issues bugs",
                "reasoning": "Looking for bug reports related to authentication",
                "priority": "high",
            },
            {
                "memory_type": "solution",
                "search_terms": "authentication fixes solutions",
                "reasoning": "Finding solutions for authentication problems",
                "priority": "high",
            },
        ],
    },
    "typo_correction": {
        "original_query": "memg proiject documentation",
        "corrected_query": "memg project documentation",
        "analysis": {
            "intent": "Finding MEMG project documentation",
            "complexity": "simple",
            "confidence": 0.95,
        },
        "sub_queries": [
            {
                "memory_type": "document",
                "search_terms": "memg project documentation",
                "reasoning": "User wants to find project documentation",
                "priority": "high",
            }
        ],
    },
}

# Sample search results
SAMPLE_SEARCH_RESULTS = [
    {
        "memory_id": "task-001",
        "memory_type": "task",
        "payload": SAMPLE_MEMORIES["task"][0],
        "score": 0.92,
    },
    {
        "memory_id": "doc-001",
        "memory_type": "document",
        "payload": SAMPLE_MEMORIES["document"][0],
        "score": 0.88,
    },
    {
        "memory_id": "solution-001",
        "memory_type": "solution",
        "payload": SAMPLE_MEMORIES["solution"][0],
        "score": 0.85,
    },
]

# JSON schemas for testing
TEST_SCHEMAS = {
    "simple": {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "required": ["message"],
    },
    "query_enhancement": {
        "type": "object",
        "properties": {
            "original_query": {"type": "string"},
            "corrected_query": {"type": "string"},
            "analysis": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "moderate", "complex"],
                    },
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "required": ["intent", "confidence"],
            },
            "sub_queries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "memory_type": {
                            "type": "string",
                            "enum": [
                                "memo",
                                "document",
                                "task",
                                "note",
                                "bug",
                                "solution",
                            ],
                        },
                        "search_terms": {"type": "string"},
                        "reasoning": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                    },
                    "required": ["memory_type", "search_terms", "reasoning"],
                },
            },
        },
        "required": ["original_query", "corrected_query", "analysis", "sub_queries"],
    },
}
