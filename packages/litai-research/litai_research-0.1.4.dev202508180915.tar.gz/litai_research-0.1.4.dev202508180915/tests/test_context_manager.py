"""Tests for context management."""

from litai.context_manager import ContextEntry, SessionContext


def test_session_context_initialization():
    """Test that SessionContext initializes correctly."""
    context = SessionContext()
    assert context.papers == {}
    assert context.get_paper_count() == 0


def test_add_paper_to_context():
    """Test adding papers to context."""
    context = SessionContext()

    # Add first paper with full_text
    context.add_paper("paper1", "Test Paper 1", "full_text", "Full text content")
    assert context.get_paper_count() == 1
    assert context.has_paper("paper1")

    # Add second context type to same paper
    context.add_paper("paper1", "Test Paper 1", "notes", "Some notes")
    assert context.get_paper_count() == 1  # Still one paper

    entry = context.papers["paper1"]
    assert "full_text" in entry.context_types
    assert "notes" in entry.context_types


def test_remove_paper_from_context():
    """Test removing papers from context."""
    context = SessionContext()
    context.add_paper("paper1", "Test Paper 1", "full_text", "Content")
    context.add_paper("paper1", "Test Paper 1", "notes", "Notes")

    # Remove specific context type
    context.remove_paper("paper1", "notes")
    assert context.has_paper("paper1")
    assert "notes" not in context.papers["paper1"].context_types

    # Remove entire paper
    context.remove_paper("paper1")
    assert not context.has_paper("paper1")


def test_get_combined_context():
    """Test that all context types are combined for synthesis."""
    context = SessionContext()

    # Add paper with multiple context types
    context.add_paper("paper1", "BERT Paper", "full_text", "Full BERT text")
    context.add_paper("paper1", "BERT Paper", "notes", "BERT key points")
    context.add_paper("paper2", "GPT Paper", "abstract", "GPT abstract")

    combined = context.get_all_context()

    # Verify all content is included
    assert "BERT Paper" in combined
    assert "Full BERT text" in combined
    assert "BERT key points" in combined
    assert "GPT Paper" in combined
    assert "GPT abstract" in combined
    assert "FULL_TEXT" in combined
    assert "NOTES" in combined
    assert "ABSTRACT" in combined


def test_context_clear():
    """Test clearing all context."""
    context = SessionContext()
    context.add_paper("paper1", "Paper 1", "full_text", "Content 1")
    context.add_paper("paper2", "Paper 2", "notes", "Content 2")

    assert context.get_paper_count() == 2

    context.clear()
    assert context.get_paper_count() == 0
    assert not context.papers


def test_context_entry():
    """Test ContextEntry class."""
    entry = ContextEntry("paper1", "Test Paper")

    # Add context types
    entry.add_context_type("abstract", "This is the abstract")
    assert "abstract" in entry.context_types
    assert entry.extracted_content["abstract"] == "This is the abstract"

    # Add another context type
    entry.add_context_type("notes", "These are notes")
    assert len(entry.context_types) == 2

    # Get combined context
    combined = entry.get_combined_context()
    assert "ABSTRACT" in combined
    assert "NOTES" in combined
    assert "This is the abstract" in combined
    assert "These are notes" in combined

    # Remove context type
    entry.remove_context_type("abstract")
    assert "abstract" not in entry.context_types
    assert "abstract" not in entry.extracted_content
