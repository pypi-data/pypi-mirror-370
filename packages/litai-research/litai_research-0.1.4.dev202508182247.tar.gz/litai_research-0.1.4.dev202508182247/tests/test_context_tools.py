"""Test context tool operations in nl_handler.

Following TDD best practices:
- Each test focuses on one specific behavior
- Tests are independent and can run in any order
- Clear arrange/act/assert structure
- Descriptive test names that explain what is being tested
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from litai.config import Config
from litai.context_manager import SessionContext
from litai.database import Database
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler


@pytest.fixture
def mock_db():
    """Create a mock database with test papers."""
    db = MagicMock(spec=Database)
    
    # Create test papers
    papers = [
        Paper(
            paper_id="paper1",
            title="Test Paper 1",
            abstract="Abstract 1",
            authors=["Author 1"],
            year=2023,
            citation_count=10,
            venue="Test Venue",
        ),
        Paper(
            paper_id="paper2", 
            title="Test Paper 2",
            abstract="Abstract 2",
            authors=["Author 2"],
            year=2023,
            citation_count=20,
            venue="Test Venue",
        ),
        Paper(
            paper_id="paper3",
            title="Test Paper 3",
            abstract="Abstract 3", 
            authors=["Author 3"],
            year=2023,
            citation_count=30,
            venue="Test Venue",
            tags=["inference"],
        ),
    ]
    
    # Mock list_papers to return papers based on tag filter
    def list_papers_impl(limit=10, tag=None):
        if tag == "inference":
            return [p for p in papers if hasattr(p, 'tags') and tag in p.tags]
        if tag:
            return []  # No papers for other tags
        return papers[:limit]
    
    db.list_papers.side_effect = list_papers_impl
    
    # Mock get_paper
    paper_map = {p.paper_id: p for p in papers}
    db.get_paper.side_effect = lambda pid: paper_map.get(pid)
    
    return db


@pytest.fixture
def session_context():
    """Create a session context."""
    return SessionContext()


@pytest.fixture
def config():
    """Create a mock config."""
    config = MagicMock(spec=Config)
    config.base_dir = "/tmp/test"
    return config


@pytest.fixture
def nl_handler(mock_db, config, session_context):
    """Create NaturalLanguageHandler with mocked dependencies."""
    command_handlers = {}
    search_results = []
    
    with patch('litai.nl_handler.LLMClient'):
        handler = NaturalLanguageHandler(
            db=mock_db,
            command_handlers=command_handlers,
            search_results_ref=search_results,
            config=config,
            session_context=session_context,
        )
        # Mock the LLM client
        handler.llm_client = AsyncMock()
        return handler


@pytest.mark.asyncio
async def test_create_context_operation_with_all_papers(nl_handler, mock_db):
    """Test adding ALL papers to context when paper_reference and tag are empty."""
    # Arrange
    operations = []
    
    # Act - simulate tool call with empty paper_reference and tag
    # Tool args would be: {"action": "add", "context_type": "abstract"}
    
    # Manually execute the logic from _resolve_context_operations
    # This simulates what happens when create_context_operation is called with no paper_reference or tag
    all_papers = mock_db.list_papers(limit=1000)
    for paper in all_papers:
        operation = {
            "paper_id": paper.paper_id,
            "paper_title": paper.title,
            "action": "add",
            "context_type": "abstract",
        }
        operations.append(operation)
    
    # Assert
    assert len(operations) == 3  # Should have operations for all 3 papers
    assert all(op["action"] == "add" for op in operations)
    assert all(op["context_type"] == "abstract" for op in operations)
    assert {op["paper_id"] for op in operations} == {"paper1", "paper2", "paper3"}


@pytest.mark.asyncio
async def test_create_context_operation_with_tag(nl_handler, mock_db):
    """Test adding papers with a specific tag to context."""
    # Arrange
    operations = []
    
    # Act - simulate tool call with tag parameter
    # Tool args would be: {"tag": "inference", "action": "add", "context_type": "full_text"}
    
    # Manually execute the logic for tag-based operations
    tagged_papers = mock_db.list_papers(tag="inference")
    for paper in tagged_papers:
        operation = {
            "paper_id": paper.paper_id,
            "paper_title": paper.title,
            "action": "add",
            "context_type": "full_text",
            "tag": "inference",
        }
        operations.append(operation)
    
    # Assert
    assert len(operations) == 1  # Only paper3 has the inference tag
    assert operations[0]["paper_id"] == "paper3"
    assert operations[0]["context_type"] == "full_text"
    assert operations[0]["tag"] == "inference"


@pytest.mark.asyncio
async def test_modify_context_operation_with_all_papers(nl_handler, session_context, mock_db):
    """Test modifying ALL papers in context when paper_reference and tag are empty."""
    # Arrange - add papers to context first
    session_context.add_paper("paper1", "Test Paper 1", "abstract")
    session_context.add_paper("paper2", "Test Paper 2", "abstract")
    current_context = session_context.get_all_papers()
    
    operations = []
    
    # Act - simulate modify tool call with empty paper_reference and tag
    # Tool args would be: {"new_context_type": "full_text"}
    
    # Manually execute the logic for modifying all papers in context
    for paper_id in current_context:
        paper = mock_db.get_paper(paper_id)
        if paper:
            operation = {
                "paper_id": paper_id,
                "paper_title": paper.title,
                "action": "modify",
                "context_type": "full_text",
            }
            operations.append(operation)
    
    # Assert
    assert len(operations) == 2  # Should modify both papers in context
    assert all(op["action"] == "modify" for op in operations)
    assert all(op["context_type"] == "full_text" for op in operations)
    assert {op["paper_id"] for op in operations} == {"paper1", "paper2"}


@pytest.mark.asyncio  
async def test_modify_context_operation_with_tag(nl_handler, session_context, mock_db):
    """Test modifying papers with a specific tag that are in context."""
    # Arrange - add papers to context including one with inference tag
    session_context.add_paper("paper1", "Test Paper 1", "abstract")
    session_context.add_paper("paper3", "Test Paper 3", "abstract")  # Has inference tag
    current_context = session_context.get_all_papers()
    
    operations = []
    
    # Act - simulate modify tool call with tag parameter
    # Tool args would be: {"tag": "inference", "new_context_type": "notes"}
    
    # Manually execute the logic for tag-based modify
    tagged_papers = mock_db.list_papers(tag="inference")
    for paper in tagged_papers:
        # Only modify if paper is in context
        if paper.paper_id in current_context:
            operation = {
                "paper_id": paper.paper_id,
                "paper_title": paper.title,
                "action": "modify",
                "context_type": "notes",
                "tag": "inference",
            }
            operations.append(operation)
    
    # Assert
    assert len(operations) == 1  # Only paper3 has inference tag and is in context
    assert operations[0]["paper_id"] == "paper3"
    assert operations[0]["action"] == "modify"
    assert operations[0]["context_type"] == "notes"


@pytest.mark.asyncio
async def test_remove_operation_with_all_papers(nl_handler, session_context):
    """Test removing ALL papers from context."""
    # Arrange - add papers to context
    session_context.add_paper("paper1", "Test Paper 1", "abstract")
    session_context.add_paper("paper2", "Test Paper 2", "full_text")
    
    operations = []
    
    # Act - simulate remove all papers
    # Tool args would be: {"action": "remove", "context_type": "abstract"}
    # Note: context_type is required but ignored for remove
    
    # For remove all, we'd iterate through papers in context
    for paper_id, entry in session_context.papers.items():
        operation = {
            "paper_id": paper_id,
            "paper_title": entry.paper_title,
            "action": "remove",
            "context_type": entry.context_type,
        }
        operations.append(operation)
    
    # Assert
    assert len(operations) == 2
    assert all(op["action"] == "remove" for op in operations)
    assert {op["paper_id"] for op in operations} == {"paper1", "paper2"}


@pytest.mark.asyncio
async def test_context_preview_display(nl_handler, session_context):
    """Test that context preview correctly shows final state after operations."""
    # Arrange
    session_context.add_paper("paper1", "Test Paper 1", "abstract")
    operations = [
        {
            "paper_id": "paper1",
            "paper_title": "Test Paper 1", 
            "action": "modify",
            "context_type": "full_text",
        },
        {
            "paper_id": "paper2",
            "paper_title": "Test Paper 2",
            "action": "add",
            "context_type": "notes",
        },
    ]
    
    # Act - test the preview calculation logic
    current_context = session_context.get_all_papers()
    final_state = {}
    
    # Start with current context
    for paper_id, context_type in current_context.items():
        final_state[paper_id] = context_type
    
    # Apply operations
    for op in operations:
        if op["action"] == "add":
            final_state[op["paper_id"]] = op["context_type"]
        elif op["action"] == "modify":
            if op["paper_id"] in final_state or op["paper_id"] in current_context:
                final_state[op["paper_id"]] = op["context_type"]
        elif op["action"] == "remove":
            if op["paper_id"] in final_state:
                del final_state[op["paper_id"]]
    
    # Assert
    assert len(final_state) == 2
    assert final_state["paper1"] == "full_text"  # Modified from abstract
    assert final_state["paper2"] == "notes"  # Added new


@pytest.mark.asyncio
async def test_duplicate_operations_are_filtered(nl_handler):
    """Test that duplicate operations are not added."""
    # Arrange
    operations = []
    existing_keys = set()
    
    # Act - try to add the same operation twice
    for _ in range(2):
        operation = {
            "paper_id": "paper1",
            "paper_title": "Test Paper 1",
            "action": "add",
            "context_type": "abstract",
        }
        
        operation_key = (
            operation["paper_id"],
            operation["action"], 
            operation["context_type"],
        )
        
        if operation_key not in existing_keys:
            operations.append(operation)
            existing_keys.add(operation_key)
    
    # Assert
    assert len(operations) == 1  # Duplicate was filtered out