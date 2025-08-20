"""Tests for StatusManager integration with tool approval workflow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from litai.config import Config
from litai.tool_approval import ToolApprovalManager, ToolCall
from litai.ui.status_manager import StatusManager


@pytest.fixture
def config():
    """Create a test configuration."""
    config = MagicMock(spec=Config)
    config.load_config.return_value = {"tool_approval": True}
    return config


@pytest.fixture
def status_manager():
    """Create a test StatusManager."""
    manager = MagicMock(spec=StatusManager)
    manager.pause = AsyncMock()
    manager.resume = AsyncMock()
    manager.start = MagicMock()
    manager.stop = MagicMock()
    manager.update = MagicMock()
    manager.is_paused = MagicMock(return_value=False)
    return manager


@pytest.fixture
def approval_manager(config, status_manager):
    """Create a ToolApprovalManager with StatusManager."""
    return ToolApprovalManager(config, status_manager)


@pytest.mark.asyncio
async def test_status_pauses_during_approval_prompt(approval_manager, status_manager):
    """Test that status animation pauses when showing approval prompt."""
    # Create a test tool call
    tool_call = ToolCall(
        id="test-1",
        name="find_papers",
        description="Search for papers about testing",
        arguments={"query": "test query"},
    )

    # Mock the prompt to auto-approve
    with patch("litai.tool_approval.Prompt.ask", return_value=""):
        response = await approval_manager.show_and_get_response(tool_call, 1, 1)

    # Verify pause was called before prompt
    status_manager.pause.assert_called_once()
    # Verify resume was called after prompt
    status_manager.resume.assert_called_once()
    # Verify approval
    assert response.approved is True


@pytest.mark.asyncio
async def test_status_resumes_after_approval(approval_manager, status_manager):
    """Test that status animation resumes after approval completes."""
    # Create test tool calls
    tool_calls = [
        ToolCall(
            id="test-1",
            name="find_papers",
            description="Search for papers",
            arguments={"query": "test"},
        ),
        ToolCall(
            id="test-2",
            name="add_paper",
            description="Add paper to library",
            arguments={"paper_numbers": "1"},
        ),
    ]

    # Mock prompt to approve first, reject second
    with patch("litai.tool_approval.Prompt.ask", side_effect=["", "q"]):
        approved = await approval_manager.interactive_approval(tool_calls)

    # Verify pause/resume called for each prompt
    assert status_manager.pause.call_count == 2
    assert status_manager.resume.call_count == 2
    # Verify only first tool approved
    assert len(approved) == 1
    assert approved[0].name == "find_papers"


@pytest.mark.asyncio
async def test_status_resumes_on_cancellation(approval_manager, status_manager):
    """Test that status resumes even when user cancels."""
    tool_call = ToolCall(
        id="test-1",
        name="find_papers",
        description="Search for papers",
        arguments={"query": "test"},
    )

    # Mock prompt to cancel
    with patch("litai.tool_approval.Prompt.ask", return_value="q"):
        response = await approval_manager.show_and_get_response(tool_call, 1, 1)

    # Verify pause/resume still called
    status_manager.pause.assert_called_once()
    status_manager.resume.assert_called_once()
    # Verify cancellation
    assert response.approved is False
    assert response.cancel_all is True


@pytest.mark.asyncio
async def test_status_resumes_on_exception(approval_manager, status_manager):
    """Test that status resumes even if an exception occurs."""
    tool_call = ToolCall(
        id="test-1",
        name="find_papers",
        description="Search for papers",
        arguments={"query": "test"},
    )

    # Mock prompt to raise exception
    with (
        patch("litai.tool_approval.Prompt.ask", side_effect=ValueError("Test error")),
        pytest.raises(ValueError),
    ):
        await approval_manager.show_and_get_response(tool_call, 1, 1)

    # Verify pause was called
    status_manager.pause.assert_called_once()
    # Verify resume was still called (in finally block)
    status_manager.resume.assert_called_once()


@pytest.mark.asyncio
async def test_no_pause_resume_without_status_manager():
    """Test that approval works without StatusManager."""
    config = MagicMock(spec=Config)
    config.load_config.return_value = {"tool_approval": True}

    # Create manager without StatusManager
    approval_manager = ToolApprovalManager(config, status_manager=None)

    tool_call = ToolCall(
        id="test-1",
        name="find_papers",
        description="Search for papers",
        arguments={"query": "test"},
    )

    # Mock prompt to approve
    with patch("litai.tool_approval.Prompt.ask", return_value=""):
        response = await approval_manager.show_and_get_response(tool_call, 1, 1)

    # Should work without errors
    assert response.approved is True


@pytest.mark.asyncio
async def test_status_manager_state_preserved():
    """Test that StatusManager state is properly preserved during pause/resume."""
    # Create real StatusManager
    status_manager = StatusManager()

    # Configure and start status
    status_manager.configure(spinner_style="dots")
    status_manager.start("Testing...")

    # Verify it's active
    assert status_manager.is_active()
    assert not status_manager.is_paused()

    # Pause
    await status_manager.pause()
    assert status_manager.is_paused()

    # Resume
    await status_manager.resume()
    assert not status_manager.is_paused()
    assert status_manager.is_active()

    # Stop
    status_manager.stop()
    assert not status_manager.is_active()
    assert not status_manager.is_paused()


@pytest.mark.asyncio
async def test_approval_disabled_no_status_interaction(config, status_manager):
    """Test that when approval is disabled, status manager is not used."""
    # Disable approval
    config.load_config.return_value = {"tool_approval": False}
    approval_manager = ToolApprovalManager(config, status_manager)

    tool_calls = [
        ToolCall(
            id="test-1",
            name="find_papers",
            description="Search for papers",
            arguments={"query": "test"},
        ),
    ]

    # Get approval (should auto-approve)
    approved = await approval_manager.get_approval(tool_calls)

    # Verify no status interaction
    status_manager.pause.assert_not_called()
    status_manager.resume.assert_not_called()
    # Verify auto-approval
    assert approved == tool_calls


@pytest.mark.asyncio
async def test_multiple_tools_sequential_pause_resume(approval_manager, status_manager):
    """Test that pause/resume happens sequentially for multiple tools."""
    tool_calls = [
        ToolCall(
            id=f"test-{i}",
            name="find_papers",
            description=f"Search {i}",
            arguments={"query": f"query {i}"},
        )
        for i in range(3)
    ]

    # Mock prompt to approve all
    with patch("litai.tool_approval.Prompt.ask", return_value=""):
        approved = await approval_manager.interactive_approval(tool_calls)

    # Verify pause/resume called for each tool
    assert status_manager.pause.call_count == 3
    assert status_manager.resume.call_count == 3
    # Verify all approved
    assert len(approved) == 3
