"""LLM client for LitAI."""

import contextlib
import json
import os
from dataclasses import dataclass
from typing import Any, Literal

import openai
import tiktoken
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from litai.utils.logger import get_logger

from .config import Config
from .models import LLMConfig
from .token_tracker import TokenTracker
from .token_tracker import TokenUsage as TokenUsageTracker

logger = get_logger(__name__)

# Reasoning models that don't support max_tokens parameter
# @TODO: Most new openai models don't support max tokens
REASONING_MODELS = {
    "o4-mini-2025-04-16",
    "o3-2025-04-16",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
}


@dataclass
class TokenUsage:
    """Token usage and cost information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


class LLMClient:
    """Unified LLM client with auto-detection for OpenAI and Anthropic."""

    def __init__(
        self, config: Config | None = None, token_tracker: TokenTracker | None = None,
    ):
        """Initialize the LLM client with optional configuration.

        Args:
            config: Optional Config instance to load LLM settings from
            token_tracker: Optional shared TokenTracker instance
        """
        self.provider: str | None = None
        self.client: AsyncOpenAI | AsyncAnthropic | None = None
        self.config: Config | None = config
        self.token_tracker: TokenTracker | None = token_tracker

        # Initialize token tracker if not provided but config is available
        if not token_tracker and config:
            self.token_tracker = TokenTracker(config)

        # Load LLM config from file if config is provided
        llm_config = LLMConfig()  # Default to auto-detection
        if config:
            config_data = config.load_config()
            if "llm" in config_data:
                llm_config = LLMConfig.from_dict(config_data["llm"])

        # Initialize provider and client based on configuration
        if llm_config.is_auto:
            # Auto-detect provider based on environment variables
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
                self.client = AsyncOpenAI()
                logger.info("llm_provider_detected", provider="openai")
            elif os.getenv("ANTHROPIC_API_KEY"):
                self.provider = "anthropic"
                self.client = AsyncAnthropic()
                logger.info("llm_provider_detected", provider="anthropic")
            else:
                raise ValueError(
                    "No API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY "
                    "environment variable, or configure your LLM provider in ~/.litai/config.json",
                )
        else:
            # Use configured provider
            self.provider = llm_config.provider

            # Get API key from specified or default env var
            if llm_config.provider == "openai":
                api_key_env = llm_config.api_key_env or "OPENAI_API_KEY"
                api_key = os.getenv(api_key_env)
                if not api_key:
                    raise ValueError(
                        f"OpenAI provider configured but {api_key_env} not set. "
                        "Please set the API key environment variable.",
                    )
                self.client = AsyncOpenAI(api_key=api_key)
            elif llm_config.provider == "anthropic":
                api_key_env = llm_config.api_key_env or "ANTHROPIC_API_KEY"
                api_key = os.getenv(api_key_env)
                if not api_key:
                    raise ValueError(
                        f"Anthropic provider configured but {api_key_env} not set. "
                        "Please set the API key environment variable.",
                    )
                self.client = AsyncAnthropic(api_key=api_key)
            else:
                raise ValueError(
                    f"Unknown provider: {llm_config.provider}. "
                    "Supported providers: openai, anthropic, auto",
                )

            logger.info("llm_provider_configured", provider=self.provider)

    async def close(self) -> None:
        """Close the client connections properly."""
        if self.client:
            with contextlib.suppress(Exception):
                await self.client.close()

    async def test_connection(self) -> tuple[str, TokenUsage]:
        """Test the LLM connection with a simple prompt.

        Returns:
            tuple of (response text, token usage info)
        """
        test_prompt = "Say 'Hello from LitAI' and nothing else."
        response = await self.complete(
            test_prompt,
            max_tokens=10,
            model_size="small",
            operation_type="connection_test",
        )
        return response["content"], response["usage"]

    async def complete(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        tools: list[dict[str, Any]] | None = None,
        model_size: Literal["small", "large"] = "small",
        operation_type: str = "",
        reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = None,
    ) -> dict[str, Any]:
        """Complete a prompt using the configured LLM with dynamic model selection.

        Args:
            prompt: The prompt to complete (string or list of messages)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            tools: Optional list of tools for function calling
            model_size: Size of model to use ("small" or "large")
            operation_type: Type of operation for tracking purposes
            reasoning_effort: Reasoning effort level for reasoning models (minimal/low/medium/high)

        Returns:
            dict containing:
                - content: The generated text
                - usage: TokenUsage object with token counts and cost
                - tool_calls: Optional list of ToolCall objects
        """
        # Select model based on size
        try:
            if self.config:
                if model_size == "small":
                    selected_model = self.config.get_small_model()
                elif model_size == "large":
                    selected_model = self.config.get_large_model()
                else:
                    raise ValueError(
                        f"Invalid model_size: {model_size}. Must be 'small' or 'large'",
                    )
            else:
                # Fallback to defaults when no config is available
                if model_size == "small":
                    selected_model = (
                        "gpt-5-nano"
                        if self.provider == "openai"
                        else "claude-3-haiku-20240307"
                    )
                elif model_size == "large":
                    selected_model = (
                        "gpt-5"
                        if self.provider == "openai"
                        else "claude-3-sonnet-20240229"
                    )
                else:
                    raise ValueError(
                        f"Invalid model_size: {model_size}. Must be 'small' or 'large'",
                    )

            # Validate that we have a model
            if not selected_model or not selected_model.strip():
                raise ValueError(
                    f"No {model_size} model configured. Please set up your LLM configuration with "
                    f"a {model_size} model using the /config command.",
                )

            await logger.ainfo(
                "llm_model_selected",
                provider=self.provider,
                model=selected_model,
                model_size=model_size,
                operation_type=operation_type,
            )

        except Exception as e:
            await logger.aerror(
                "llm_model_selection_failed",
                error=str(e),
                model_size=model_size,
                provider=self.provider,
            )
            raise ValueError(f"Failed to select {model_size} model: {e}") from e

        try:
            if self.provider == "openai":
                response = await self._complete_openai(
                    prompt,
                    max_tokens,
                    temperature,
                    tools,
                    selected_model,
                    reasoning_effort,
                )
            elif self.provider == "anthropic":
                response = await self._complete_anthropic(
                    prompt, max_tokens, temperature, tools, selected_model,
                )
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            # Track token usage if tracker is available
            if self.token_tracker and "usage" in response:
                usage = TokenUsageTracker(
                    input_tokens=response["usage"].prompt_tokens,
                    output_tokens=response["usage"].completion_tokens,
                    model=selected_model,
                    model_size=model_size,
                    operation_type=operation_type,
                )
                self.token_tracker.track_usage(usage)

            return response

        except openai.RateLimitError:
            # Don't log, just re-raise so it can be caught by callers
            raise
        except Exception as e:
            await logger.aerror(
                "llm_completion_failed",
                error=str(e),
                model=selected_model,
                model_size=model_size,
                provider=self.provider,
            )
            raise

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        model_size: Literal["small", "large"] = "small",
        operation_type: str = "text_generation",
    ) -> str:
        """Simple text generation helper - returns just the content string.

        Args:
            prompt: The prompt to complete
            max_tokens: Maximum tokens to generate
            model_size: Model size to use ("small" or "large")
            operation_type: Type of operation for tracking

        Returns:
            The generated text content
        """
        response = await self.complete(
            prompt,
            max_tokens=max_tokens,
            model_size=model_size,
            operation_type=operation_type,
        )
        return str(response["content"])

    async def _complete_openai(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = None,
    ) -> dict[str, Any]:
        """Complete using OpenAI API."""
        if not self.client:
            raise ValueError("OpenAI client not initialized")

        # Check client type - handle both real client and mocks
        try:
            is_openai_client = isinstance(self.client, AsyncOpenAI)
        except TypeError:
            # Handle mocked clients in tests
            is_openai_client = hasattr(self.client, "chat") and hasattr(
                self.client.chat, "completions",
            )

        if not is_openai_client:
            raise ValueError("OpenAI client not initialized")

        # Handle both string prompts and message lists
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        # Use the passed model or default
        model_name = model or "gpt-5"

        # Build kwargs based on model type
        create_kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
        }

        # Only add max_tokens and temperature if not a reasoning model
        if model_name not in REASONING_MODELS:
            create_kwargs["max_tokens"] = max_tokens
            create_kwargs["temperature"] = temperature
        else:
            # For reasoning models, add reasoning effort if specified
            if reasoning_effort:
                create_kwargs["reasoning"] = {"effort": reasoning_effort}

        # Add tools if provided
        if tools:
            create_kwargs["tools"] = tools

        response: ChatCompletion = await self.client.chat.completions.create(
            **create_kwargs,
        )

        # Log the full API response for debugging (only when debug level is enabled)
        logger.debug(
            "openai_api_response",
            model=model_name,
            response_content=response.choices[0].message.content if response.choices else None,
            tool_calls=[
                {"name": tc.function.name, "args": tc.function.arguments}
                for tc in (response.choices[0].message.tool_calls or [])
            ] if response.choices else [],
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            } if response.usage else None,
        )

        message = response.choices[0].message
        usage = response.usage

        if not usage:
            raise ValueError("No usage information returned from OpenAI API")

        # Calculate cost (approximate pricing as of 2024)
        prompt_cost = usage.prompt_tokens * 0.01 / 1000  # $0.01 per 1K tokens
        completion_cost = usage.completion_tokens * 0.03 / 1000  # $0.03 per 1K tokens
        total_cost = prompt_cost + completion_cost

        result = {
            "content": message.content or "",
            "usage": TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=total_cost,
            ),
        }

        # Add tool calls if present
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    ),
                )
            result["tool_calls"] = tool_calls

        return result

    async def _complete_anthropic(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Complete using Anthropic API."""
        if not self.client:
            raise ValueError("Anthropic client not initialized")

        # Check client type - handle both real client and mocks
        try:
            is_anthropic_client = isinstance(self.client, AsyncAnthropic)
        except TypeError:
            # Handle mocked clients in tests
            is_anthropic_client = hasattr(self.client, "messages") and hasattr(
                self.client.messages, "create",
            )

        if not is_anthropic_client:
            raise ValueError("Anthropic client not initialized")

        # Handle both string prompts and message lists
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
            prompt_text = prompt
        else:
            messages = []
            system_msg = None
            prompt_text = ""

            # Extract system message and format other messages
            for msg in prompt:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                    prompt_text += msg["content"] + "\n"
                else:
                    messages.append(msg)
                    prompt_text += msg.get("content", "") + "\n"

        # Count tokens using tiktoken (approximation for Claude)
        prompt_tokens = self._count_tokens(prompt_text)

        # Use the passed model or default
        model_name = model or "claude-3-sonnet-20240229"

        # Build kwargs based on model type
        create_kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
        }

        # Add system message if present
        if "system_msg" in locals() and system_msg:
            create_kwargs["system"] = system_msg

        # Only add max_tokens and temperature if not a reasoning model
        if model_name not in REASONING_MODELS:
            create_kwargs["max_tokens"] = max_tokens
            create_kwargs["temperature"] = temperature

        # Add tools if provided
        if tools:
            create_kwargs["tools"] = tools

        response: AnthropicMessage = await self.client.messages.create(**create_kwargs)

        # Extract content and tool calls from response
        content = ""
        tool_calls = []

        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=dict(block.input)
                        if isinstance(block.input, dict)
                        else {},
                    ),
                )

        # Calculate tokens
        completion_text = content + json.dumps(
            [{"name": tc.name, "args": tc.arguments} for tc in tool_calls],
        )
        completion_tokens = self._count_tokens(completion_text)

        # Log the full API response for debugging (only when debug level is enabled)
        logger.debug(
            "anthropic_api_response",
            model=model_name,
            response_content=response.content[0].text if response.content and hasattr(response.content[0], "text") else None,
            tool_calls=[
                {"name": block.name, "args": block.input}
                for block in response.content
                if hasattr(block, "name")
            ] if response.content else [],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )

        total_tokens = prompt_tokens + completion_tokens

        # Calculate cost (approximate pricing for Claude 3 Sonnet)
        prompt_cost = prompt_tokens * 0.003 / 1000  # $0.003 per 1K tokens
        completion_cost = completion_tokens * 0.015 / 1000  # $0.015 per 1K tokens
        total_cost = prompt_cost + completion_cost

        result = {
            "content": content,
            "usage": TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=total_cost,
            ),
        }

        # Add tool calls if present
        if tool_calls:
            result["tool_calls"] = tool_calls

        return result

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        This is an approximation for non-OpenAI models.
        """
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))

    def estimate_cost(self, prompt: str, response: str) -> TokenUsage:
        """Estimate the cost of a prompt/response pair.

        Args:
            prompt: The input prompt
            response: The generated response

        Returns:
            TokenUsage object with cost estimate
        """
        prompt_tokens = self._count_tokens(prompt)
        completion_tokens = self._count_tokens(response)
        total_tokens = prompt_tokens + completion_tokens

        if self.provider == "openai":
            prompt_cost = prompt_tokens * 0.01 / 1000
            completion_cost = completion_tokens * 0.03 / 1000
        elif self.provider == "anthropic":
            prompt_cost = prompt_tokens * 0.003 / 1000
            completion_cost = completion_tokens * 0.015 / 1000
        else:
            prompt_cost = completion_cost = 0

        total_cost = prompt_cost + completion_cost

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=total_cost,
        )
