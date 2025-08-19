"""Unit tests for natural language query handling with real LLM.

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
        tool_calls.append("synthesize")
        return handle_synthesize_command(*args, **kwargs)

    def tracked_context_show(*args, **kwargs):
        tool_calls.append("handle_context_show")
        return handle_context_show(*args, **kwargs)

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
        "synthesize": tracked_synthesize,
        "handle_context_show": tracked_context_show,
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
# Find/Search command tests
#=======================================================================

class TestFindPapersQueries:
    """Test natural language queries related to finding/searching papers."""

    @pytest.mark.asyncio
    async def test_find_papers_query(self, nl_handler_with_tracking, capsys):
        """Test that search queries trigger find command."""
        await nl_handler_with_tracking.handle_query("Find papers about transformers")

        # Check that find_papers was intended to be called
        assert "find_papers" in nl_handler_with_tracking.tool_calls
        # Since approval is false, it might not actually execute
        captured = capsys.readouterr()
        assert "transform" in captured.out.lower() or "search" in captured.out.lower()


#=======================================================================
# Add paper command tests
#=======================================================================

#@TODO: Need to patch the find resutls for this to work
class TestAddPaperQueries:
    """Test natural language queries related to adding papers."""

##  @pytest.mark.asyncio
##  async def test_add_paper_basic_query(self, nl_handler_with_tracking, capsys):
##      """Test basic add paper request."""
##      await nl_handler_with_tracking.handle_query(
##          "Add a paper titled 'Deep Learning' by Goodfellow from 2016",
##      )
##      assert "add_paper" in nl_handler_with_tracking.tool_calls
##      captured = capsys.readouterr()
##      assert "add" in captured.out.lower() or "paper" in captured.out.lower()
##
##  #@TODO: Change to meet the papers
##  @pytest.mark.asyncio
##  async def test_batch_add_papers(self, nl_handler_with_tracking, capsys):
##      """Test adding multiple papers at once."""
##      await nl_handler_with_tracking.handle_query(
##          "Add these papers: arxiv:2103.14030, arxiv:2104.09125, and arxiv:2105.01601",
##      )
##      # Should call add_paper multiple times or handle batch addition
##      assert "add_paper" in nl_handler_with_tracking.tool_calls


#=======================================================================
# Collection/List command tests  
#=======================================================================

class TestCollectionQueries:
    """Test natural language queries related to listing/viewing collection."""

#   @pytest.mark.asyncio
#   async def test_basic_list_query(self, nl_handler_with_tracking, capsys):
#       """Test that asking about papers triggers list command."""
#       await nl_handler_with_tracking.handle_query(
#           "What papers do I have in my collection?",
#       )
#
#       # TODO: This test may need redefining - LLM might not call list_papers
#       # if paper info is already injected in context (which happens on first query)
#       # Check that list_papers was called
#       assert "list_papers" in nl_handler_with_tracking.tool_calls
#
#       captured = capsys.readouterr()
#       # Should see papers listed
#       assert (
#           "Attention Is All You Need" in captured.out
#           or "papers" in captured.out.lower()
#       )

    @pytest.mark.asyncio
    async def test_specific_paper_query(self, nl_handler_with_tracking, capsys):
        """Test asking about a specific paper."""
        await nl_handler_with_tracking.handle_query(
            "What can you tell me about the Attention Is All You Need paper?",
        )

        captured = capsys.readouterr()
        # Should provide information about the paper
        assert any(
            term in captured.out
            for term in ["Attention", "Transformer", "Vaswani", "2017"]
        )

    @pytest.mark.asyncio
    async def test_citation_count_query(self, nl_handler_with_tracking, capsys):
        """Test asking about citation counts."""
        await nl_handler_with_tracking.handle_query(
            "Which of my papers has the most citations?",
        )

        captured = capsys.readouterr()
        # Should mention the highest cited paper
        assert (
            "Attention Is All You Need" in captured.out
            or "50000" in captured.out
            or "citations" in captured.out.lower()
        )

    @pytest.mark.asyncio
    async def test_year_based_query(self, nl_handler_with_tracking, capsys):
        """Test queries about papers from specific years."""
        await nl_handler_with_tracking.handle_query(
            "What papers do I have from 2018?",
        )

        captured = capsys.readouterr()
        # Should mention BERT which is from 2018
        assert "BERT" in captured.out or "2018" in captured.out

    @pytest.mark.asyncio
    async def test_author_query(self, nl_handler_with_tracking, capsys):
        """Test asking about papers by specific authors."""
        await nl_handler_with_tracking.handle_query(
            "Do I have any papers by Vaswani?",
        )

        captured = capsys.readouterr()
        # Should mention the Attention paper
        assert "Attention" in captured.out or "Vaswani" in captured.out

    @pytest.mark.asyncio
    async def test_comparison_query(self, nl_handler_with_tracking, capsys):
        """Test comparison queries between papers."""
        await nl_handler_with_tracking.handle_query(
            "Compare the BERT and GPT-3 papers in my collection",
        )

        captured = capsys.readouterr()
        # Should mention both papers
        assert ("BERT" in captured.out or "GPT" in captured.out) and (
            "compare" in captured.out.lower() or "both" in captured.out.lower()
        )

    @pytest.mark.asyncio
    async def test_tool_call_verification(self, nl_handler_with_tracking, capsys):
        """Test that the right tools are being called for different queries."""
        # TODO: These assertions may need adjustment since paper info is injected
        # Clear previous calls
        nl_handler_with_tracking.tool_calls.clear()

        # Test list papers
        await nl_handler_with_tracking.handle_query("Show me all my papers")
        assert "list_papers" in nl_handler_with_tracking.tool_calls

        # Clear and test another query type
        nl_handler_with_tracking.tool_calls.clear()
        await nl_handler_with_tracking.handle_query(
            "What tags do I have in my collection?",
        )
        # This might call list_tags or list_papers depending on LLM interpretation
        assert len(nl_handler_with_tracking.tool_calls) > 0


#=======================================================================
# Remove paper command tests
#=======================================================================

class TestRemovePaperQueries:
    """Test natural language queries related to removing papers."""

    @pytest.mark.asyncio
    async def test_remove_paper_by_title(self, nl_handler_with_tracking, capsys):
        """Test removing paper by title."""
        await nl_handler_with_tracking.handle_query(
            "Remove the BERT from my collection",
        )
        assert "remove_paper" in nl_handler_with_tracking.tool_calls
        captured = capsys.readouterr()
        assert "remove" in captured.out.lower() or "delete" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_remove_paper_by_id(self, nl_handler_with_tracking, capsys):
        """Test removing paper by ID."""
        await nl_handler_with_tracking.handle_query(
            "Delete paper bert2018",
        )
        assert "remove_paper" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_remove_multiple_papers(self, nl_handler_with_tracking, capsys):
        """Test removing multiple papers."""
        await nl_handler_with_tracking.handle_query(
            "Remove all papers from 2017",
        )
        assert "remove_paper" in nl_handler_with_tracking.tool_calls

    #@TODO: Figure out what to do
#   @pytest.mark.asyncio
#   async def test_remove_nonexistent_paper(self, nl_handler_with_tracking, capsys):
#       """Test removing a paper that doesn't exist."""
#       await nl_handler_with_tracking.handle_query(
#           "Remove the paper about quantum computing",
#       )
#       captured = capsys.readouterr()
#       assert any(term in captured.out.lower() 
#                  for term in ["not found", "doesn't exist", "no paper", "quantum"])
#

#=======================================================================
# Tag command tests
#=======================================================================

class TestTagQueries:
    """Test natural language queries related to tags."""

    @pytest.mark.asyncio
    async def test_tag_query(self, nl_handler_with_tracking, db, capsys):
        """Test natural language tag queries."""
        # Ask about papers with specific tag
        await nl_handler_with_tracking.handle_query("Show me papers tagged with NLP")

        captured = capsys.readouterr()
        # Should show papers with NLP tag
        assert "NLP" in captured.out or "papers" in captured.out.lower()


#=======================================================================
# Note command tests
#=======================================================================

class TestNoteQueries:
    """Test natural language queries related to notes."""
    # No existing tests for note queries

    @pytest.mark.asyncio
    async def test_add_note_to_paper(self, nl_handler_with_tracking, capsys):
        """Test adding a note to a specific paper."""
        await nl_handler_with_tracking.handle_query(
            "Add a note to the BERT paper: 'Important for my research on language models'",
        )
        assert "handle_note" in nl_handler_with_tracking.tool_calls
        captured = capsys.readouterr()
        assert "note" in captured.out.lower() or "added" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_view_paper_notes(self, nl_handler_with_tracking, capsys):
        """Test viewing notes for a paper."""
        await nl_handler_with_tracking.handle_query(
            "Show me the notes for the Attention paper",
        )
        assert "handle_note" in nl_handler_with_tracking.tool_calls

    #@TODO: Idk how this will beahve; wait this is kind of good tbh
    @pytest.mark.asyncio
    async def test_add_note_without_paper_specified(self, nl_handler_with_tracking, capsys):
        """Test adding note without specifying paper."""
        await nl_handler_with_tracking.handle_query(
            "Add a note: 'This is relevant to my thesis'",
        )
        captured = capsys.readouterr()
        # Should ask which paper
        assert any(term in captured.out.lower() 
                   for term in ["which paper", "specify", "paper"])

    @pytest.mark.asyncio
    async def test_delete_note(self, nl_handler_with_tracking, capsys):
        """Test deleting a note from a paper."""
        await nl_handler_with_tracking.handle_query(
            "Remove the note from the GPT-3 paper",
        )
        assert "handle_note" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_list_all_notes(self, nl_handler_with_tracking, capsys):
        """Test listing all notes across papers."""
        await nl_handler_with_tracking.handle_query(
            "Show me all my notes",
        )
        assert "handle_note" in nl_handler_with_tracking.tool_calls



#=======================================================================
# Synthesize command tests
#=======================================================================

#@TODO: Come back, it's calling cshow, understandbly
class TestSynthesizeQueries:
    """Test natural language queries related to synthesis."""
    # No existing tests for synthesize queries
    @pytest.mark.asyncio
    async def test_basic_synthesize_query(self, nl_handler_with_tracking, capsys, db, config):
        """Test basic synthesis request."""
        # Add all papers to context before synthesis
        from litai.commands.context_commands import handle_context_add
        from litai.llm import LLMClient
        from litai.token_tracker import TokenTracker

        # Initialize token tracker for usage monitoring
        token_tracker = TokenTracker(config)
        llm_client = LLMClient(config, token_tracker=token_tracker)
        await handle_context_add(
            "",  # Empty args means add all papers
            db, 
            nl_handler_with_tracking.handler.session_context, 
            llm_client,
            skip_resolution=True,
        )
        
        await nl_handler_with_tracking.handle_query(
            "Synthesize the papers in my collection",
        )
        assert "synthesize" in nl_handler_with_tracking.tool_calls
        captured = capsys.readouterr()
        assert "synthesize" in captured.out.lower() or "review" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_synthesize_with_topic(self, nl_handler_with_tracking, capsys, db, config):
        """Test synthesis with specific topic focus."""
        # Add all papers to context before synthesis
        from litai.commands.context_commands import handle_context_add
        from litai.llm import LLMClient
        from litai.token_tracker import TokenTracker
        # Initialize token tracker for usage monitoring
        token_tracker = TokenTracker(config)
        llm_client = LLMClient(config, token_tracker=token_tracker)
        await handle_context_add(
            "",  # Empty args means add all papers
            db, 
            nl_handler_with_tracking.handler.session_context, 
            llm_client,
            skip_resolution=True,
        )
        
        await nl_handler_with_tracking.handle_query(
            "Use synthesize to compare my papers.",
        )
        assert "synthesize" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_synthesize_subset_of_papers(self, nl_handler_with_tracking, capsys, db, config):
        """Test synthesizing specific papers."""
        # Add all papers to context before synthesis
        from litai.commands.context_commands import handle_context_add
        from litai.llm import LLMClient
        from litai.token_tracker import TokenTracker
        # Initialize token tracker for usage monitoring
        token_tracker = TokenTracker(config)
        llm_client = LLMClient(config, token_tracker=token_tracker)
        await handle_context_add(
            "",  # Empty args means add all papers
            db, 
            nl_handler_with_tracking.handler.session_context, 
            llm_client,
            skip_resolution=True,
        )
        
        await nl_handler_with_tracking.handle_query(
            "Synthesize the BERT and GPT-3 papers",
        )
        assert "synthesize" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_synthesize_by_year(self, nl_handler_with_tracking, capsys, db, config):
        """Test synthesizing papers from specific time period."""
        # Add all papers to context before synthesis
        from litai.commands.context_commands import handle_context_add
        from litai.llm import LLMClient
        from litai.token_tracker import TokenTracker
        # Initialize token tracker for usage monitoring
        token_tracker = TokenTracker(config)
        llm_client = LLMClient(config, token_tracker=token_tracker)
        await handle_context_add(
            "",  # Empty args means add all papers
            db, 
            nl_handler_with_tracking.handler.session_context, 
            llm_client,
            skip_resolution=True,
        )
        
        await nl_handler_with_tracking.handle_query(
            "Create a literature review of papers from 2018-2020",
        )
        assert "synthesize" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_synthesize_with_format(self, nl_handler_with_tracking, capsys, db, config):
        """Test synthesis with specific format request."""
        # Add all papers to context before synthesis
        from litai.commands.context_commands import handle_context_add
        from litai.llm import LLMClient
        from litai.token_tracker import TokenTracker
        # Initialize token tracker for usage monitoring
        token_tracker = TokenTracker(config)
        llm_client = LLMClient(config, token_tracker=token_tracker)
        await handle_context_add(
            "",  # Empty args means add all papers
            db, 
            nl_handler_with_tracking.handler.session_context, 
            llm_client,
            skip_resolution=True,
        )
        
        await nl_handler_with_tracking.handle_query(
            "Generate a synthesis in bullet points",
        )
        assert "synthesize" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_synthesize_empty_collection(self, nl_handler_with_tracking, capsys):
        """Test synthesizing when no papers match criteria."""
        await nl_handler_with_tracking.handle_query(
            "Synthesize papers about quantum computing",
        )
        captured = capsys.readouterr()
        assert any(term in captured.out.lower() 
                   for term in ["no papers", "empty", "not found", "quantum"])



#=======================================================================
# Context command tests (cshow, cclear)
#=======================================================================

class TestContextQueries:
    """Test natural language queries related to context management."""
    # No existing tests for context queries


#=======================================================================
# User research profile command tests
#=======================================================================

class TestUserPromptQueries:
    """Test natural language queries related to user prompts."""
    @pytest.mark.asyncio
    async def test_set_user_prompt(self, nl_handler_with_tracking, capsys):
        """Test setting a custom user prompt."""
        await nl_handler_with_tracking.handle_query(
            "Set my prompt to focus on methodology critique",
        )
        assert "handle_user_prompt" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_view_current_prompt(self, nl_handler_with_tracking, capsys):
        """Test viewing current user prompt."""
        await nl_handler_with_tracking.handle_query(
            "Show me my current prompt settings",
        )
        assert "handle_user_prompt" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_reset_prompt(self, nl_handler_with_tracking, capsys):
        """Test resetting to default prompt."""
        await nl_handler_with_tracking.handle_query(
            "Reset my prompt to default",
        )
        assert "handle_user_prompt" in nl_handler_with_tracking.tool_calls

    @pytest.mark.asyncio
    async def test_prompt_with_template(self, nl_handler_with_tracking, capsys):
        """Test using prompt templates."""
        await nl_handler_with_tracking.handle_query(
            "Use the academic review prompt template",
        )
        assert "handle_user_prompt" in nl_handler_with_tracking.tool_calls

#=======================================================================
# Clear command tests; unclear whether this exists
#=======================================================================

class TestClearQueries:
    """Test natural language queries related to clearing."""
    # No existing tests for clear queries

#=======================================================================
# Error handling and edge cases
#=======================================================================

class TestErrorHandlingIntegration:
    """Test error handling with real LLM."""

##  @pytest.mark.asyncio
##  async def test_empty_collection_query(self, config, capsys):
##      """Test querying an empty collection."""
##      # Create fresh database with no papers
##      empty_db = Database(config)
##      command_handlers = {"list_papers": lambda db, page=1: "No papers in collection"}
##      search_results = []
##      from litai.context_manager import SessionContext
##
##      session_context = SessionContext()
##
##      nl_handler = NaturalLanguageHandler(
##          empty_db, command_handlers, search_results, config, session_context,
##      )
##      nl_handler.approval_manager.enabled = False
##
##      try:
##          await nl_handler.handle_query("Show me my papers")
##          captured = capsys.readouterr()
##          assert (
##              "no papers" in captured.out.lower() or "empty" in captured.out.lower()
##          )
##      finally:
##          await nl_handler.close()

    @pytest.mark.asyncio
    async def test_ambiguous_reference(self, nl_handler_with_tracking, capsys):
        """Test handling ambiguous references."""
        await nl_handler_with_tracking.handle_query(
            "Tell me about the paper",  # Ambiguous - which paper?
        )

        captured = capsys.readouterr()
        # Should either ask for clarification or list options
        assert any(
            term in captured.out.lower()
            for term in ["which", "specific", "papers", "collection"]
        )

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
