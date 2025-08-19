"""
YAML-to-JSON schema converter for AI consumption.
Converts memg-core YAML schema to JSON schema format for GenAI.
"""

from typing import Any

from memg_core.core.yaml_translator import YamlTranslator


class SchemaConverter:
    """Converts YAML schema to JSON schema for AI consumption."""

    def __init__(self, yaml_schema_path: str):
        """
        Initialize with YAML schema path.

        Args:
            yaml_schema_path: Path to the YAML schema file
        """
        self.translator = YamlTranslator(yaml_schema_path)
        self.schema = self.translator.schema

    def get_memory_types(self) -> list[str]:
        """Get list of available memory types from schema."""
        return [entity["name"] for entity in self.schema["entities"]]

    def get_memory_type_descriptions(self) -> dict[str, str]:
        """Get memory type descriptions for AI prompts."""
        return {
            entity["name"]: entity.get("description", "")
            for entity in self.schema["entities"]
        }

    def create_query_enhancement_schema(self) -> dict[str, Any]:
        """
        Create JSON schema for query enhancement AI processing.

        Returns:
            JSON schema dict for structured query enhancement
        """
        memory_types = self.get_memory_types()

        schema = {
            "type": "object",
            "properties": {
                "original_query": {
                    "type": "string",
                    "description": "The original user query as received",
                },
                "corrected_query": {
                    "type": "string",
                    "description": "Query with typos fixed and clarifications",
                },
                "analysis": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "User's search intent",
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex"],
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                        },
                    },
                    "required": ["intent", "complexity", "confidence"],
                },
                "sub_queries": {
                    "type": "array",
                    "description": "1-3 structured sub-queries for deterministic search",
                    "minItems": 1,
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "properties": {
                            "memory_type": {
                                "type": "string",
                                "enum": memory_types,
                                "description": f"Memory type to search. Available: {', '.join(memory_types)}",
                            },
                            "search_terms": {
                                "type": "string",
                                "description": "Search terms for this memory type",
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Why this memory type and these search terms were chosen",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Search priority for result ranking",
                            },
                        },
                        "required": ["memory_type", "search_terms", "reasoning"],
                    },
                },
            },
            "required": [
                "original_query",
                "corrected_query",
                "analysis",
                "sub_queries",
            ],
        }

        return schema

    def create_query_enhancement_prompt(self) -> str:
        """
        Create system prompt for query enhancement AI.

        Returns:
            System instruction prompt for GenAI
        """
        memory_types = self.get_memory_type_descriptions()

        type_descriptions = "\n".join(
            [f"- **{name}**: {desc}" for name, desc in memory_types.items()]
        )

        prompt = f"""You are an expert at transforming free-form queries into structured memory searches.

Your job is to:
1. Fix any typos or unclear language in the original query
2. Analyze the user's search intent and complexity
3. Break down the query into 1-3 structured sub-queries for deterministic search
4. For each sub-query, determine the appropriate memory type and search terms

**Available Memory Types:**
{type_descriptions}

**Guidelines:**
- Use 1 sub-query for simple, focused searches
- Use 2-3 sub-queries for complex searches that span multiple memory types
- Always provide clear reasoning for your memory type choices
- Search terms should be concise but comprehensive
- Fix typos naturally without being too literal
- Prioritize sub-queries by relevance (high/medium/low)

**Examples:**
- "all tasks related to memg project development" → task + "memg project development"
- "bugs and solutions for authentication" → bug + "authentication", solution + "authentication"
- "document about API design" → document + "API design"

Be precise, helpful, and always explain your reasoning."""

        return prompt


def create_schema_converter(
    yaml_schema_path: str,
) -> SchemaConverter:
    """
    Create a schema converter for the given YAML schema.

    Args:
        yaml_schema_path: Path to YAML schema file

    Returns:
        SchemaConverter instance
    """
    return SchemaConverter(yaml_schema_path)
