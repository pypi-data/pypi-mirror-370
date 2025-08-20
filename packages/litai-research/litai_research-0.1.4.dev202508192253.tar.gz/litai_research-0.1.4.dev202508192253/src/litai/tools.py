"""Tool definitions for natural language interface."""

from typing import Any, TypedDict

from litai.utils.log_context import operation_context
from litai.utils.logger import get_logger

logger = get_logger(__name__)


class ToolParameter(TypedDict):
    """Parameter definition for a tool."""

    type: str
    description: str
    required: bool
    enum: list[str] | None


class ToolDefinition(TypedDict):
    """Definition of a tool that can be called by the LLM."""

    name: str
    description: str
    parameters: dict[str, ToolParameter]


LITAI_TOOLS: list[ToolDefinition] = [
    {
        "name": "find_papers",
        "description": (
            "Search for academic papers on a specific topic using Semantic Scholar. "
            "By default, replaces previous search results. Use the append parameter to "
            "accumulate results from multiple searches, which is useful for building "
            "comprehensive collections, combining different search angles, or exploring "
            "related topics. The system automatically removes duplicates when appending. "
            "IMPORTANT: When users request 'find x, y, and z' or 'find x and y', interpret "
            "as multiple separate searches (one for each term) and ALWAYS use append=true "
            "for ALL searches in the sequence to build a comprehensive collection."
        ),
        "parameters": {
            "query": {
                "type": "string",
                "description": (
                    "The search query or topic to find papers about "
                    "(omit to show recent results)"
                ),
                "required": False,
                "enum": None,
            },
            "append": {
                "type": "boolean",
                "description": (
                    "If true, append to existing results instead of replacing them. "
                    "Useful for building comprehensive collections from multiple searches. "
                    "(default: False)"
                ),
                "required": False,
                "enum": None,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of papers to return (default: 10)",
                "required": False,
                "enum": None,
            },
            "show_recent": {
                "type": "boolean",
                "description": (
                    "Show cached results from the last search (default: False)"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "add_paper",
        "description": (
            "Add paper(s) from search results to the user's collection. "
            "Can add a single paper, multiple papers (comma-delimited), or all papers. "
            "Optionally add tags to papers at the same time using --tags"
        ),
        "parameters": {
            "paper_numbers": {
                "type": "string",
                "description": (
                    "The paper number(s) to add. Can be: empty string (adds all), "
                    "single number (e.g. '1'), or comma-delimited list (e.g. '1,3,5')"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "papers_command",
        "description": (
            "List papers in collection, show all tags, or filter by tags/notes. "
            "Note: To add or view notes for a specific paper, use the note tool instead"
        ),
        "parameters": {
            "page": {
                "type": "integer",
                "description": "The page number to display (default: 1)",
                "required": False,
                "enum": None,
            },
            "show_tags": {
                "type": "boolean",
                "description": (
                    "Show all tags in the database with paper counts (default: False)"
                ),
                "required": False,
                "enum": None,
            },
            "show_notes": {
                "type": "boolean",
                "description": "Show only papers that have notes (default: False)",
                "required": False,
                "enum": None,
            },
            "tag_filter": {
                "type": "string",
                "description": "Filter papers by specific tag name",
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "remove_paper",
        "description": (
            "Remove paper(s) from the user's collection. Can remove a single "
            "paper, multiple papers (comma-delimited), or all papers"
        ),
        "parameters": {
            "paper_numbers": {
                "type": "string",
                "description": (
                    "The paper number(s) to remove. Can be: empty string "
                    "(removes all), single number (e.g. '1'), or comma-delimited "
                    "list (e.g. '1,3,5')"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "manage_paper_tags",
        "description": (
            "Add, remove, or list tags for papers in the collection. "
            "Supports single papers, multiple papers (comma-delimited), ranges (e.g., 1-5), "
            "or natural language paper references"
        ),
        "parameters": {
            "paper_number": {
                "type": "integer",
                "description": "The paper number to manage tags for",
                "required": True,
                "enum": None,
            },
            "add_tags": {
                "type": "string",
                "description": (
                    "Comma-separated list of tags to add (e.g. 'machine-learning,nlp')"
                ),
                "required": False,
                "enum": None,
            },
            "remove_tags": {
                "type": "string",
                "description": "Comma-separated list of tags to remove",
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "synthesize",
        "description": (
            "Synthesize insights from papers in the current context (NOT collection). "
            "Context is different from collection - papers must first be in your collection, "
            "then explicitly added to context for synthesis. The context is a subset of your collection. "
            "This uses ALL papers currently in context to provide a comprehensive analysis. "
            "Use sharded mode when dealing with many papers or if the user mentions processing papers "
            "individually, separately, one by one, or in shards. "
            "Deals with any queries that are asking you to synthesize or do a synthesis. "
            "IMPORTANT: Before calling this tool, ensure papers are in context (check <context_status>). "
            "If no papers are in context, inform the user to add papers to context first - do NOT attempt to "
            "inject paper information into the query parameter. "
            "When passing the query parameter, use the user's original question with only "
            "minor corrections for grammar and spelling. Do not significantly rephrase or change the "
            "user's question - preserve their original intent and wording as much as possible."
        ),
        "parameters": {
            "query": {
                "type": "string",
                "description": (
                    "The user's question or topic to synthesize insights about from the papers in context. "
                    "Use the user's original wording with only minor grammar/spelling corrections. "
                    "Do not significantly rephrase or alter the question. "
                    "NEVER inject paper titles or lists into this parameter - only pass the user's actual question."
                ),
                "required": True,
                "enum": None,
            },
            "sharded": {
                "type": "boolean",
                "description": (
                    "Use sharded mode to process each paper individually then combine results. "
                    "Useful for large contexts or when user wants individual paper analysis first. "
                    "IMPORTANT: If synthesis fails with 'Request too large' error, retry with sharded=True. "
                    "(default: False)"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "note",
        "description": (
            "View or append to notes for a specific paper in the collection. "
            "Notes are personal annotations stored separately from the paper content."
        ),
        "parameters": {
            "paper_id": {
                "type": "string",
                "description": "The paper ID to manage notes for",
                "required": True,
                "enum": None,
            },
            "operation": {
                "type": "string",
                "description": (
                    "The operation to perform: "
                    "'view' (show existing note) or 'append' (add to existing note)"
                ),
                "required": True,
                "enum": ["view", "append"],
            },
            "content": {
                "type": "string",
                "description": (
                    "The note content to append (only used for 'append' operation)"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "prompt",
        "description": (
            "View or append to your system prompt. "
            "This prompt helps LitAI understand your expertise, interests, and research focus "
            "to provide more tailored synthesis and analysis."
        ),
        "parameters": {
            "operation": {
                "type": "string",
                "description": (
                    "The operation to perform: "
                    "'view' (show current system prompt) or 'append' (add to system prompt)"
                ),
                "required": True,
                "enum": ["view", "append"],
            },
            "content": {
                "type": "string",
                "description": (
                    "The text to append to your system prompt (only used for 'append' operation)"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "context_show",
        "description": (
            "Show the current context - displays which papers are loaded for synthesis. "
            "Shows paper titles and what content types (full_text, abstract, notes) are available for each. "
            "Use this before synthesizing to verify the right papers are in context."
        ),
        "parameters": {},
    },
]


def get_openai_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to OpenAI function calling format."""
    with operation_context(
        "tool_generation", provider="openai", tools_count=len(LITAI_TOOLS),
    ):
        logger.info("generating_openai_tools", tools_count=len(LITAI_TOOLS))
        openai_tools = []

        for tool in LITAI_TOOLS:
            properties: dict[str, Any] = {}
            required = []

            for param_name, param_def in tool["parameters"].items():
                properties[param_name] = {
                    "type": param_def["type"],
                    "description": param_def["description"],
                }
                if param_def.get("enum"):
                    properties[param_name]["enum"] = param_def["enum"]
                if param_def.get("required", False):
                    required.append(param_name)

            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }
            openai_tools.append(openai_tool)

        return openai_tools


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to Anthropic tool use format."""
    with operation_context(
        "tool_generation", provider="anthropic", tools_count=len(LITAI_TOOLS),
    ):
        logger.info("generating_anthropic_tools", tools_count=len(LITAI_TOOLS))
        anthropic_tools = []

        for tool in LITAI_TOOLS:
            properties: dict[str, Any] = {}
            required = []

            for param_name, param_def in tool["parameters"].items():
                properties[param_name] = {
                    "type": param_def["type"],
                    "description": param_def["description"],
                }
                if param_def.get("enum"):
                    properties[param_name]["enum"] = param_def["enum"]
                if param_def.get("required", False):
                    required.append(param_name)

            anthropic_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            anthropic_tools.append(anthropic_tool)

        return anthropic_tools
