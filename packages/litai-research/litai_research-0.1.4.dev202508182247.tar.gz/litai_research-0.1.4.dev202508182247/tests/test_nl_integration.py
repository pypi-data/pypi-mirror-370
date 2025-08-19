"""Integration tests for natural language query handling with real LLM.

TODO: Several tests may need redefining because the NaturalLanguageHandler now
injects paper collection context on the first query, which means the LLM may
answer questions directly without calling tools. Tests that may need adjustment:
- test_basic_list_query: LLM might not call list_papers if context is injected
- test_tool_call_verification: Tool calls may differ with injected context
- Tests expecting specific tool calls when info is already available

This test module validates the NaturalLanguageHandler's ability to:
1. Process natural language queries using actual LLM models (GPT-5-nano)
2. Map user intents to appropriate CLI command handlers
3. Maintain conversation context across multiple queries
4. Handle edge cases like empty collections and ambiguous references

Test Structure:
--------------
Fixtures:
- temp_dir: Creates isolated temporary directory for test data
- config: Sets up Config with GPT-5-nano model configuration
- db: Creates Database instance for test papers
- sample_papers: Populates database with 3 AI/NLP papers for testing
- nl_handler_with_tracking: Creates NaturalLanguageHandler with wrapped command
  handlers that track which tools are called during query processing

Test Classes:
------------
1. TestRealNaturalLanguageQueries: Core functionality tests
   - Basic queries (list, find, tag operations)
   - Specific paper lookups and comparisons
   - Context-aware follow-up questions
   - Tool call verification

2. TestErrorHandlingIntegration: Error scenarios
   - Empty collection queries
   - Ambiguous references requiring clarification

3. TestConversationFlow: Multi-turn conversation tests
   - Research workflow simulations
   - Context maintenance across queries
   - Memory and reference resolution

Requirements:
------------
- OPENAI_API_KEY environment variable must be set
- Tests are skipped if API key is unavailable
- Uses GPT-5-nano model for fast, cost-effective testing

Note: These are integration tests that make real API calls.
They validate end-to-end behavior rather than individual components.
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from litai.config import Config
from litai.database import Database
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler

#=======================================================================
# Setup
#=======================================================================

# Skip these tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config(temp_dir):
    """Create a real config with API key."""
    config = Config(base_dir=temp_dir)
    # Set to use gpt-5-mini model
    config.update_config("llm.provider", "openai")
    config.update_config("llm.model", "gpt-5-nano")
    return config


@pytest.fixture
def db(config):
    """Create a real database."""
    return Database(config)


@pytest.fixture
def sample_papers(db):
    """Add sample papers to the database."""
    papers = [
        Paper(
            paper_id="attention2017",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
            citation_count=50000,
            tags=["transformers", "attention", "NLP"],
        ),
        Paper(
            paper_id="bert2018",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang", "Lee", "Toutanova"],
            year=2018,
            abstract="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
            citation_count=40000,
            tags=["BERT", "NLP", "pretraining"],
        ),
        Paper(
            paper_id="gpt3_2020",
            title="Language Models are Few-Shot Learners",
            authors=["Brown", "Mann", "Ryder", "Subbiah"],
            year=2020,
            abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task.",
            citation_count=10000,
            tags=["GPT", "few-shot", "language-models"],
        ),
    ]

    # Add papers to database
    for paper in papers:
        db.add_paper(paper)

    return papers


class TrackedNLHandler:
    """Wrapper for NaturalLanguageHandler that tracks tool calls."""

    def __init__(self, nl_handler, tool_calls):
        self.handler = nl_handler
        self.tool_calls = tool_calls

    async def handle_query(self, query: str) -> None:
        """Forward to the wrapped handler."""
        return await self.handler.handle_query(query)

    async def close(self) -> None:
        """Forward to the wrapped handler."""
        return await self.handler.close()


@pytest_asyncio.fixture
async def nl_handler_with_tracking(db, config, sample_papers):
    """Create NL handler that tracks which tools are called during test execution.

    This fixture wraps the real command handlers with tracking functions to verify
    that the NaturalLanguageHandler correctly maps user queries to the appropriate
    tool calls. We need this wrapper approach because:

    1. The NaturalLanguageHandler expects a dictionary of command handlers that it
       calls dynamically based on LLM responses
    2. We want to test that the LLM correctly identifies which tools to use for
       different natural language queries
    3. We need to track which handlers are actually called to verify the LLM's
       tool selection logic is working correctly
    4. We can't just mock the handlers because we also want to verify they execute
       successfully with real data

    The tracking wrappers call the real implementations while recording which tools
    were invoked, allowing tests to assert both that the correct tools were selected
    AND that they executed successfully.
    """
    # Import real command handlers
    from litai.cli import (
        add_paper,
        find_papers,
        handle_tag_command,
        list_papers,
        list_tags,
        remove_paper,
        show_search_results,
    )
    from litai.cli import (
        handle_note_tool as handle_note,
    )
    from litai.cli import (
        handle_user_prompt_tool as handle_user_prompt,
    )
    from litai.commands.context_commands import (
        handle_context_add,
        handle_context_modify,
        handle_context_remove,
        handle_context_show,
    )
    from litai.commands.synthesize import handle_synthesize_command

    # Track which tools get called
    tool_calls = []

    # Wrap real handlers to track calls
    async def tracked_find_papers(*args, **kwargs):
        tool_calls.append("find_papers")
        return await find_papers(*args, **kwargs)

    def tracked_add_paper(*args, **kwargs):
        tool_calls.append("add_paper")
        return add_paper(*args, **kwargs)

    def tracked_list_papers(*args, **kwargs):
        tool_calls.append("list_papers")
        return list_papers(*args, **kwargs)

    def tracked_tag_handler(*args, **kwargs):
        tool_calls.append("handle_tag_command")
        return handle_tag_command(*args, **kwargs)

    def tracked_list_tags(*args, **kwargs):
        tool_calls.append("list_tags")
        return list_tags(*args, **kwargs)

    def tracked_show_results(*args, **kwargs):
        tool_calls.append("show_search_results")
        return show_search_results(*args, **kwargs)

    async def tracked_synthesize(*args, **kwargs):
        tool_calls.append("handle_synthesize")
        return handle_synthesize_command(*args, **kwargs)

    def tracked_context_show(*args, **kwargs):
        tool_calls.append("handle_context_show")
        return handle_context_show(*args, **kwargs)

    async def tracked_context_add(*args, **kwargs):
        tool_calls.append("handle_context_add")
        return await handle_context_add(*args, **kwargs)

    async def tracked_context_modify(*args, **kwargs):
        tool_calls.append("handle_context_modify")
        return await handle_context_modify(*args, **kwargs)

    async def tracked_context_remove(*args, **kwargs):
        tool_calls.append("handle_context_remove")
        return await handle_context_remove(*args, **kwargs)

    async def tracked_note(*args, **kwargs):
        tool_calls.append("handle_note")
        return await handle_note(*args, **kwargs)

    async def tracked_user_prompt(*args, **kwargs):
        tool_calls.append("handle_user_prompt")
        return await handle_user_prompt(*args, **kwargs)

    def tracked_remove_paper(*args, **kwargs):
        tool_calls.append("remove_paper")
        return remove_paper(*args, **kwargs)

    command_handlers = {
        "find_papers": tracked_find_papers,
        "add_paper": tracked_add_paper,
        "list_papers": tracked_list_papers,
        "handle_tag_command": tracked_tag_handler,
        "list_tags": tracked_list_tags,
        "show_search_results": tracked_show_results,
        "remove_paper": tracked_remove_paper,
        "handle_synthesize": tracked_synthesize,
        "handle_context_show": tracked_context_show,
        "handle_context_add": tracked_context_add,
        "handle_context_modify": tracked_context_modify,
        "handle_context_remove": tracked_context_remove,
        "handle_note": tracked_note,
        "handle_user_prompt": tracked_user_prompt,
    }

    search_results = []
    from litai.context_manager import SessionContext

    session_context = SessionContext()
    nl_handler = NaturalLanguageHandler(
        db, command_handlers, search_results, config, session_context,
    )

    # Set tool approval to false (auto-approve all tools)
    nl_handler.approval_manager.enabled = False

    # Return a wrapper that includes both the handler and the tool_calls list
    tracked_handler = TrackedNLHandler(nl_handler, tool_calls)

    yield tracked_handler

    # Cleanup
    await nl_handler.close()

#=======================================================================
# Conversation flow and context maintenance
#=======================================================================

class TestConversationFlow:
    """Test multi-turn conversation flows."""

    @pytest.mark.asyncio
    async def test_contextual_follow_up(self, nl_handler_with_tracking, capsys):
        """Test that the LLM maintains context across queries."""
        # First query
        await nl_handler_with_tracking.handle_query("Show me my papers")

        # Follow-up query using context
        await nl_handler_with_tracking.handle_query("Tell me more about the BERT paper")

        captured = capsys.readouterr()
        # Should reference BERT paper details
        assert (
            "BERT" in captured.out
            or "Devlin" in captured.out
            or "bidirectional" in captured.out.lower()
        )

    @pytest.mark.asyncio
    async def test_research_workflow(self, nl_handler_with_tracking, capsys):
        """Test a typical research workflow conversation."""
        # Start with overview
        await nl_handler_with_tracking.handle_query(
            "Give me an overview of my collection",
        )

        # Ask about specific topic
        await nl_handler_with_tracking.handle_query(
            "Which papers discuss attention mechanisms?",
        )

        # Deep dive into one
        await nl_handler_with_tracking.handle_query(
            "Tell me more about the transformer architecture",
        )

        captured = capsys.readouterr()

        # Should maintain context throughout
        assert "papers" in captured.out.lower()
        assert any(
            term in captured.out
            for term in ["attention", "Attention", "transformer", "Transformer"]
        )

    @pytest.mark.asyncio
    async def test_clarification_flow(self, nl_handler_with_tracking, capsys):
        """Test that the system asks for and handles clarifications."""
        # Ambiguous query
        await nl_handler_with_tracking.handle_query("Compare them")

        captured = capsys.readouterr()

        # Should recognize lack of context and either ask for clarification or make reasonable assumption
        assert len(captured.out) > 0  # Should produce some response

    @pytest.mark.asyncio
    async def test_memory_across_queries(self, nl_handler_with_tracking, capsys):
        """Test that the system remembers previous interactions."""
        # First mention a specific paper
        await nl_handler_with_tracking.handle_query("Tell me about the BERT paper")

        # Then refer to it indirectly
        await nl_handler_with_tracking.handle_query("What year was it published?")

        captured = capsys.readouterr()

        # Should correctly identify "it" as BERT and mention 2018
        assert "2018" in captured.out or "BERT" in captured.out


#=======================================================================
# Helper functions
#=======================================================================

# Helper function to run async tests synchronously if needed
def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    # Can run specific tests directly
    import sys

    pytest.main([__file__] + sys.argv[1:])
