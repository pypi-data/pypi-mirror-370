"""Conversation management for natural language interface."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from litai.config import Config


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""

    role: str  # "system", "user", "assistant", or "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: list[dict[str, Any]] | None = None
    tool_results: list[dict[str, Any]] | None = None


class ConversationManager:
    """Manages conversation history and context for natural language interactions."""

    def __init__(self, config: Config | None = None, max_messages: int = 20):
        """Initialize conversation manager.

        Args:
            config: Configuration object for loading user prompt
            max_messages: Maximum number of messages to keep in history
        """
        self.messages: list[ConversationMessage] = []
        self.max_messages = max_messages
        self.config = config
        self._add_system_message()

    def _add_system_message(self) -> None:
        """Add the initial system message that sets up the assistant's behavior."""
        # Load system prompt from text file
        prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
        try:
            system_prompt = prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            # Fallback to hardcoded prompt if file not found
            system_prompt = """You are LitAI, an AI assistant that helps researchers manage and synthesize academic papers. 
        
Your capabilities include:
- Searching for papers on specific topics using Semantic Scholar
- Managing a personal library of papers
- Extracting key points from papers
- Synthesizing information across multiple papers to answer research questions

When users ask questions or make requests:
1. Understand their intent and determine which tools to use
2. Call the appropriate tools to fulfill their request
3. Provide clear, helpful responses based on the results

Be conversational but concise. Focus on helping researchers find, understand, and synthesize academic literature effectively."""

        # Load and append user prompt if available
        if self.config and self.config.user_prompt_path.exists():
            try:
                user_prompt = self.config.user_prompt_path.read_text().strip()
                if user_prompt:
                    system_prompt += f"\n\n## User Research Context\n\n{user_prompt}"
            except Exception:
                # Silently ignore errors loading user prompt
                pass

        self.add_message("system", system_prompt)

    def reset(self) -> None:
        """Reset conversation history, keeping only the system message."""
        self.messages.clear()
        self._add_system_message()

    def add_message(
        self,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add a message to the conversation history.

        Args:
            role: The role of the message sender
            content: The message content
            tool_calls: List of tool calls made (for assistant messages)
            tool_results: List of tool results (for tool response messages)
        """
        message = ConversationMessage(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
        self.messages.append(message)

        # Trim history if needed, keeping system message
        if len(self.messages) > self.max_messages:
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            # Keep system messages and most recent other messages
            self.messages = (
                system_msgs + other_msgs[-(self.max_messages - len(system_msgs)) :]
            )

    def get_messages_for_llm(self, provider: str) -> list[dict[str, Any]]:
        """Get messages formatted for the LLM provider.

        Args:
            provider: "openai" or "anthropic"

        Returns:
            List of messages in the appropriate format
        """
        formatted_messages: list[dict[str, Any]] = []

        for i, msg in enumerate(self.messages):
            formatted_msg: dict[str, Any]

            if provider == "openai":
                # Map system prompt: use "developer" for OpenAI
                openai_role = "developer" if msg.role == "system" else msg.role
                formatted_msg = {
                    "role": openai_role,
                    "content": msg.content,
                }
                if msg.tool_calls:
                    # OpenAI requires tool_calls to have a "type" field and arguments as JSON string
                    formatted_msg["tool_calls"] = [
                        {
                            "type": "function",
                            "id": tc.get("id"),
                            "function": {
                                "name": tc.get("name"),
                                "arguments": json.dumps(tc.get("arguments"))
                                if isinstance(tc.get("arguments"), dict)
                                else tc.get("arguments"),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                if msg.role == "tool" and msg.tool_results:
                    # OpenAI requires strict message ordering: tool messages must immediately follow
                    # an assistant message that contains tool_calls with matching IDs.
                    #
                    # Bug scenario: In natural language mode, failed queries (e.g., "clear") create
                    # assistant messages without tool_calls. When a subsequent query uses tools,
                    # the tool results can end up paired with these non-tool-calling messages,
                    # causing OpenAI to reject with: "messages with role 'tool' must be a response
                    # to a preceding message with 'tool_calls'."
                    #
                    # Fix: Validate that tool messages are properly paired with their calling message.
                    if (
                        i > 0
                        and self.messages[i - 1].role == "assistant"
                        and self.messages[i - 1].tool_calls
                    ):
                        # Get tool call IDs from the previous message
                        prev_tool_calls = self.messages[i - 1].tool_calls
                        prev_tool_call_ids = (
                            {tc.get("id") for tc in prev_tool_calls}
                            if prev_tool_calls
                            else set()
                        )
                        # Only include tool results that match the previous tool calls
                        for result in msg.tool_results:
                            if result.get("tool_call_id") in prev_tool_call_ids:
                                formatted_messages.append(
                                    {
                                        "role": "tool",
                                        "content": result["content"],
                                        "tool_call_id": result["tool_call_id"],
                                    },
                                )
                    # Skip adding the original tool message wrapper
                    continue
                formatted_messages.append(formatted_msg)
            else:  # anthropic
                # Map system prompt: use "system" for Anthropic (handled separately in API call)
                anthropic_role = msg.role
                formatted_msg = {
                    "role": anthropic_role,
                    "content": msg.content,
                }
                if msg.tool_calls:
                    # Anthropic includes tool use in content blocks
                    formatted_msg["content"] = [
                        {"type": "text", "text": msg.content},
                        *[{"type": "tool_use", **tc} for tc in msg.tool_calls],
                    ]
                if msg.role == "tool" and msg.tool_results:
                    # Anthropic expects tool results in content blocks
                    formatted_msg["content"] = [
                        {"type": "tool_result", **result} for result in msg.tool_results
                    ]

                formatted_messages.append(formatted_msg)

        return formatted_messages

    def get_last_user_message(self) -> str | None:
        """Get the content of the last user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def clear_history(self) -> None:
        """Clear conversation history but keep system message."""
        self.messages = [msg for msg in self.messages if msg.role == "system"]
