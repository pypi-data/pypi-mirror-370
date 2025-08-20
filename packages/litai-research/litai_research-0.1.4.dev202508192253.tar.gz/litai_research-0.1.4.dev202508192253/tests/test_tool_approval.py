"""Tests for tool approval system."""

from unittest.mock import MagicMock, patch

import pytest

from litai.config import Config
from litai.tool_approval import ApprovalResponse, ToolApprovalManager, ToolCall


@pytest.fixture
def mock_config():
    """Create mock config with tool_approval enabled."""
    config = MagicMock(spec=Config)
    config.load_config.return_value = {"synthesis": {"tool_approval": True}}
    return config


@pytest.fixture
def mock_config_disabled():
    """Create mock config with tool_approval disabled."""
    config = MagicMock(spec=Config)
    config.load_config.return_value = {"synthesis": {"tool_approval": False}}
    return config


@pytest.mark.asyncio
async def test_approval_disabled(mock_config_disabled):
    """Test that tools execute without approval when disabled."""
    manager = ToolApprovalManager(mock_config_disabled)

    tool_calls = [
        ToolCall("1", "search_papers", "Search papers", {"query": "attention"}),
        ToolCall("2", "extract_context", "Extract context", {"depth": "abstracts"}),
    ]

    approved = await manager.get_approval(tool_calls)
    assert approved == tool_calls  # All passed through unchanged


@pytest.mark.asyncio
async def test_approval_enabled_approve_all(mock_config):
    """Test approving all tool calls."""
    manager = ToolApprovalManager(mock_config)

    with patch.object(manager, "show_and_get_response") as mock_show:
        mock_show.return_value = ApprovalResponse(approved=True)

        tool_calls = [
            ToolCall("1", "search_papers", "Search papers", {"query": "attention"}),
            ToolCall("2", "extract_context", "Extract context", {"depth": "abstracts"}),
        ]

        approved = await manager.get_approval(tool_calls)
        assert len(approved) == 2
        assert mock_show.call_count == 2
        assert approved[0].name == "search_papers"
        assert approved[1].name == "extract_context"


@pytest.mark.asyncio
async def test_cancel_all(mock_config):
    """Test canceling all tool calls."""
    manager = ToolApprovalManager(mock_config)

    with patch.object(manager, "show_and_get_response") as mock_show:
        mock_show.return_value = ApprovalResponse(approved=False, cancel_all=True)

        tool_calls = [
            ToolCall("1", "search_papers", "Search papers", {"query": "attention"}),
            ToolCall("2", "extract_context", "Extract context", {"depth": "abstracts"}),
        ]

        approved = await manager.get_approval(tool_calls)
        assert len(approved) == 0  # All cancelled
        assert mock_show.call_count == 1  # Only showed first


def test_format_params():
    """Test parameter formatting for display."""
    manager = ToolApprovalManager(MagicMock())

    # Test empty params
    assert manager._format_params({}) == "  (no parameters)"

    # Test simple params
    params = {"query": "test", "limit": 10}
    formatted = manager._format_params(params)
    assert "query: test" in formatted
    assert "limit: 10" in formatted

    # Test list truncation
    params = {"ids": ["1", "2", "3", "4", "5"]}
    formatted = manager._format_params(params)
    assert "[1, 2, 3...]" in formatted

    # Test dict params
    params = {"config": {"nested": "value"}}
    formatted = manager._format_params(params)
    assert "config: {...}" in formatted

    # Test long string truncation
    params = {"query": "a" * 60}
    formatted = manager._format_params(params)
    assert "..." in formatted
    assert len(formatted.split(":")[1]) < 60


@pytest.mark.asyncio
async def test_show_and_get_response_approve():
    """Test user approval interaction."""
    manager = ToolApprovalManager(MagicMock())

    call = ToolCall("1", "search_papers", "Search papers", {"query": "test"})

    with patch("litai.tool_approval.Prompt.ask", return_value=""):
        with patch("litai.tool_approval.console.print"):
            response = await manager.show_and_get_response(call, 1, 2)

            assert response.approved is True
            assert response.cancel_all is False


@pytest.mark.asyncio
async def test_show_and_get_response_cancel():
    """Test user cancel all interaction."""
    manager = ToolApprovalManager(MagicMock())

    call = ToolCall("1", "search_papers", "Search papers", {"query": "test"})

    with patch("litai.tool_approval.Prompt.ask", return_value="q"):
        with patch("litai.tool_approval.console.print"):
            response = await manager.show_and_get_response(call, 1, 2)

            assert response.approved is False
            assert response.cancel_all is True


def test_get_approval_setting():
    """Test reading approval setting from config."""
    # Test enabled (default)
    config = MagicMock()
    config.load_config.return_value = {}
    manager = ToolApprovalManager(config)
    assert manager.enabled is True

    # Test explicitly enabled
    config.load_config.return_value = {"synthesis": {"tool_approval": True}}
    manager = ToolApprovalManager(config)
    assert manager.enabled is True

    # Test disabled
    config.load_config.return_value = {"synthesis": {"tool_approval": False}}
    manager = ToolApprovalManager(config)
    assert manager.enabled is False
