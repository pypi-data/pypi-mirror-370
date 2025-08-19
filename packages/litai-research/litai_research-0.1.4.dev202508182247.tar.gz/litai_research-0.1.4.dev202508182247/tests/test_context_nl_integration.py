"""Integration tests for natural language context management.

This module tests that natural language requests for context management
correctly map to the appropriate context tools with the correct parameters.
Tests use real LLM calls (GPT-5-nano) for end-to-end validation.

Test Categories:
1. Context Query Classification - Identifies context management vs other queries
2. Add ALL Papers - Tests bulk add operations 
3. Tag-Based Operations - Tests filtering by tags
4. Modify Operations - Tests bulk modify operations
5. Complex Workflows - Tests multi-step context management


TODO:
  - Make tests that check the modification case

"""

import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio

from litai.config import Config
from litai.context_manager import SessionContext
from litai.database import Database
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler

# Skip tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config(temp_dir):
    """Create a real config with GPT-5-nano for cost-effective testing."""
    config = Config(base_dir=temp_dir)
    config.update_config("llm.provider", "openai")
    config.update_config("llm.model", "gpt-5-nano")
    return config


@pytest.fixture
def db(config):
    """Create a real database."""
    return Database(config)


@pytest.fixture
def sample_papers(db):
    """Add sample papers to the database for testing context operations."""
    papers = [
        Paper(
            paper_id="paper1",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            abstract="The Transformer architecture based solely on attention mechanisms.",
            citation_count=50000,
            tags=["transformers", "attention", "NLP"],
        ),
        Paper(
            paper_id="paper2",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang"],
            year=2018,
            abstract="Bidirectional Encoder Representations from Transformers.",
            citation_count=40000,
            tags=["BERT", "NLP", "pretraining"],
        ),
        Paper(
            paper_id="paper3",
            title="GPT-3: Language Models are Few-Shot Learners",
            authors=["Brown", "Mann"],
            year=2020,
            abstract="Large language models demonstrate few-shot learning capabilities.",
            citation_count=30000,
            tags=["GPT", "few-shot", "language-models"],
        ),
        Paper(
            paper_id="paper4",
            title="Efficient Inference in Transformers",
            authors=["Zhang", "Li"],
            year=2021,
            abstract="Methods for improving transformer inference efficiency.",
            citation_count=5000,
            tags=["inference", "optimization", "transformers"],
        ),
        Paper(
            paper_id="paper5",
            title="Attention Mechanisms in Computer Vision",
            authors=["Wang", "Chen"],
            year=2022,
            abstract="Applying attention mechanisms to vision tasks.",
            citation_count=2000,
            tags=["attention", "computer-vision", "old"],
        ),
    ]

    # Add papers to database
    for paper in papers:
        db.add_paper(paper)

    return papers


class ContextToolTracker:
    """Tracks context tool calls and their parameters."""
    
    def __init__(self):
        self.tool_calls = []
        self.context_operations = []
        
    def clear(self):
        """Clear all tracked calls."""
        self.tool_calls.clear()
        self.context_operations.clear()
        
    def track_operation(self, tool_name: str, params: dict[str, Any]):
        """Track a context operation with its parameters."""
        self.tool_calls.append(tool_name)
        self.context_operations.append({
            "tool": tool_name,
            "params": params,
        })


@pytest_asyncio.fixture
async def nl_handler_with_tracking(db, config, sample_papers):
    """Create NL handler with context tool tracking."""
    from litai.cli import (
        handle_tag_command,
        list_papers,
        list_tags,
    )
    from litai.commands.context_commands import (
        handle_context_add,
        handle_context_modify,
        handle_context_remove,
        handle_context_show,
    )
    
    # Create tracker
    tracker = ContextToolTracker()
    
    # Wrap context handlers to track calls
    async def tracked_context_add(*args, **kwargs):
        tracker.track_operation("handle_context_add", {"args": args, "kwargs": kwargs})
        # Call the original handler with the same arguments
        return await handle_context_add(*args, **kwargs)
    
    async def tracked_context_modify(*args, **kwargs):
        tracker.track_operation("handle_context_modify", {"args": args, "kwargs": kwargs})
        # Call the original handler with the same arguments
        return await handle_context_modify(*args, **kwargs)
    
    async def tracked_context_remove(*args, **kwargs):
        tracker.track_operation("handle_context_remove", {"args": args, "kwargs": kwargs})
        # Call the original handler with the same arguments
        return await handle_context_remove(*args, **kwargs)
    
    def tracked_context_show(*args, **kwargs):
        tracker.track_operation("handle_context_show", {"args": args, "kwargs": kwargs})
        return handle_context_show(*args, **kwargs)
    
    def tracked_list_papers(*args, **kwargs):
        tracker.track_operation("list_papers", {"args": args, "kwargs": kwargs})
        return list_papers(*args, **kwargs)
    
    def tracked_list_tags(*args, **kwargs):
        tracker.track_operation("list_tags", {"args": args, "kwargs": kwargs})
        return list_tags(*args, **kwargs)
    
    def tracked_tag_command(*args, **kwargs):
        tracker.track_operation("handle_tag_command", {"args": args, "kwargs": kwargs})
        return handle_tag_command(*args, **kwargs)
    
    command_handlers = {
        "handle_context_add": tracked_context_add,
        "handle_context_modify": tracked_context_modify,
        "handle_context_remove": tracked_context_remove,
        "handle_context_show": tracked_context_show,
        "list_papers": tracked_list_papers,
        "list_tags": tracked_list_tags,
        "handle_tag_command": tracked_tag_command,
    }
    
    session_context = SessionContext()
    search_results = []
    
    nl_handler = NaturalLanguageHandler(
        db, command_handlers, search_results, config, session_context,
    )
    
    # Disable tool approval for testing
    nl_handler.approval_manager.enabled = False
    
    # Attach tracker to handler for test access
    nl_handler.tracker = tracker
    
    yield nl_handler
    
    # Cleanup
    await nl_handler.close()


# ==============================================================================
# Test Context Query Classification  
# ==============================================================================

class TestContextQueryClassification:
    """Test that queries are correctly classified as context management vs regular queries."""
    
    #@TODO: Find way to run in parallel, or batch
    #@TODO: Format these logs
    @pytest.mark.asyncio
    async def test_context_add_queries_are_identified(self, nl_handler_with_tracking, capsys):
        """Test that context ADD queries trigger context add tools.
        
        Each query starts with an EMPTY context and should trigger handle_context_add.
        """
        add_queries = [
            "add all papers to context",
            #"add papers with attention tag to context as abstracts",  # Changed to use existing tag
            "add the paper about attention mechanisms to context",
        ]
        
        # Patch console.input to auto-accept all context operations
        with patch('litai.nl_handler.console.input', return_value=""):
            for query in add_queries:
                # Clear previous tracking and context for clean state
                nl_handler_with_tracking.tracker.clear()
                nl_handler_with_tracking.session_context.clear()
                
                # Process query
                await nl_handler_with_tracking.handle_query(query)
                
                # Debug: Print what was tracked
                print(f"\nQuery: {query}")
                print(f"Tracked tools: {nl_handler_with_tracking.tracker.tool_calls}")
                
                # Verify handle_context_add was called
                called_add_tools = [
                    tool for tool in nl_handler_with_tracking.tracker.tool_calls 
                    if tool == "handle_context_add"
                ]
                
                assert len(called_add_tools) > 0, f"No context add tool called for query: {query}"
    
    #@TODO: Keep running test if one thing fails
    @pytest.mark.asyncio
    async def test_context_modify_queries_are_identified(self, nl_handler_with_tracking, capsys):
        """Test that context MODIFY queries trigger context modify tools.
        
        Each query starts with papers already in context, then attempts to modify them.
        """
        # Pre-populate context for modify operations
        async def setup_context():
            nl_handler_with_tracking.session_context.clear()
            # Add some papers to context first (need paper_id, paper_title, context_type)
            nl_handler_with_tracking.session_context.add_paper("paper1", "Attention Is All You Need", "abstract")
            nl_handler_with_tracking.session_context.add_paper("paper2", "BERT: Pre-training of Deep Bidirectional Transformers", "abstract")
            nl_handler_with_tracking.session_context.add_paper("paper3", "GPT-3: Language Models are Few-Shot Learners", "abstract")
        
        modify_queries = [
            "change all papers to full text",
            #"modify the context for the paper about efficient inference to use notes",
            #"change the BERT paper to use full text",
        ]
        
        # Patch console.input to auto-accept all context operations
        with patch('litai.nl_handler.console.input', return_value=""):
            for query in modify_queries:
                # Setup context with papers
                await setup_context()
                
                # Clear tracking but keep context
                nl_handler_with_tracking.tracker.clear()
                
                # Process query
                await nl_handler_with_tracking.handle_query(query)
                
                # Debug: Print what was tracked
                print(f"\nQuery: {query}")
                print(f"Tracked tools: {nl_handler_with_tracking.tracker.tool_calls}")
                
                # Verify a modify tool was called (could be add with different type or modify)
                context_tools = ["handle_context_add", "handle_context_modify"]
                
                called_context_tools = [
                    tool for tool in nl_handler_with_tracking.tracker.tool_calls 
                    if tool in context_tools
                ]
                
                assert len(called_context_tools) > 0, f"No context modify tool called for query: {query}"
    
    # All pass, let's go
    @pytest.mark.asyncio
    async def test_context_remove_queries_are_identified(self, nl_handler_with_tracking, capsys):
        """Test that context REMOVE queries trigger context remove tools.
        
        Each query starts with papers already in context, then attempts to remove them.
        """
        # Pre-populate context for remove operations
        async def setup_context():
            nl_handler_with_tracking.session_context.clear()
            # Add some papers to context first (need paper_id, paper_title, context_type)
            nl_handler_with_tracking.session_context.add_paper("paper1", "Attention Is All You Need", "abstract")
            nl_handler_with_tracking.session_context.add_paper("paper2", "BERT: Pre-training of Deep Bidirectional Transformers", "abstract")
            nl_handler_with_tracking.session_context.add_paper("paper3", "GPT-3: Language Models are Few-Shot Learners", "abstract")
        
        remove_queries = [
            "remove the BERT paper from context",
            "remove all papers from context",
            "remove the paper about attention from context",
        ]
        
        # Patch console.input to auto-accept all context operations
        with patch('litai.nl_handler.console.input', return_value=""):
            for query in remove_queries:
                # Setup context with papers
                await setup_context()
                
                # Clear tracking but keep context
                nl_handler_with_tracking.tracker.clear()
                
                # Process query
                await nl_handler_with_tracking.handle_query(query)
                
                # Debug: Print what was tracked
                print(f"\nQuery: {query}")
                print(f"Tracked tools: {nl_handler_with_tracking.tracker.tool_calls}")
                
                # Verify remove tool was called
                called_remove_tools = [
                    tool for tool in nl_handler_with_tracking.tracker.tool_calls 
                    if tool == "handle_context_remove"
                ]
                
                assert len(called_remove_tools) > 0, f"No context remove tool called for query: {query}"
    
    @pytest.mark.asyncio
    async def test_non_context_queries_are_not_classified_as_context(self, nl_handler_with_tracking):
        """Test that non-context queries don't trigger context modification tools."""
        non_context_queries = [
            "show me what's in the context",  # This is viewing, not modifying
            "what papers are in my context?",  # Query about context, not modifying
        ]
        
        # Patch console.input in case any prompts occur
        with patch('litai.nl_handler.console.input', return_value=""):
            for query in non_context_queries:
                # Clear previous tracking
                nl_handler_with_tracking.tracker.clear()
                
                # Process query
                await nl_handler_with_tracking.handle_query(query)
                
                # Verify no context modification tools were called
                context_modification_tools = [
                    "handle_context_add",
                    "handle_context_modify", 
                    "handle_context_remove",
                ]
                
                called_modification_tools = [
                    tool for tool in nl_handler_with_tracking.tracker.tool_calls
                    if tool in context_modification_tools
                ]
                
                # View operations shouldn't trigger modification tools
                # (handle_context_show is ok)
                assert len(called_modification_tools) == 0, f"Modification tool called for view query: {query}"
