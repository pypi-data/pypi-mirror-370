"""Tests for user prompt integration in conversation management."""

import shutil
import tempfile
from pathlib import Path

import pytest

from litai.config import Config
from litai.conversation import ConversationManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestConversationUserPrompt:
    """Test user prompt integration in ConversationManager."""

    def test_conversation_without_config(self):
        """Test ConversationManager works without config."""
        conv = ConversationManager()
        assert len(conv.messages) == 1
        assert conv.messages[0].role == "developer"
        assert "LitAI" in conv.messages[0].content

    def test_conversation_with_empty_config(self, temp_dir):
        """Test ConversationManager with config but no user prompt."""
        config = Config(base_dir=temp_dir)
        conv = ConversationManager(config)

        assert len(conv.messages) == 1
        assert conv.messages[0].role == "developer"
        assert "User Research Context" not in conv.messages[0].content

    def test_conversation_with_user_prompt(self, temp_dir):
        """Test ConversationManager loads user prompt."""
        config = Config(base_dir=temp_dir)

        # Create user prompt file
        user_prompt = """## Research Context
I'm researching transformer architectures for edge deployment.

## Background
PhD student in ML optimization."""

        config.user_prompt_path.write_text(user_prompt)

        # Create conversation manager
        conv = ConversationManager(config)

        assert len(conv.messages) == 1
        assert conv.messages[0].role == "developer"
        assert "User Research Context" in conv.messages[0].content
        assert (
            "transformer architectures for edge deployment" in conv.messages[0].content
        )
        assert "PhD student in ML optimization" in conv.messages[0].content

    def test_conversation_handles_prompt_read_error(self, temp_dir):
        """Test ConversationManager handles errors reading user prompt gracefully."""
        config = Config(base_dir=temp_dir)

        # Create unreadable file (on Unix systems)
        config.user_prompt_path.touch()
        config.user_prompt_path.chmod(0o000)

        try:
            # Should not raise exception
            conv = ConversationManager(config)
            assert len(conv.messages) == 1
            assert "User Research Context" not in conv.messages[0].content
        finally:
            # Restore permissions for cleanup
            config.user_prompt_path.chmod(0o644)

    def test_conversation_ignores_empty_prompt(self, temp_dir):
        """Test ConversationManager ignores empty user prompt."""
        config = Config(base_dir=temp_dir)

        # Create empty prompt file
        config.user_prompt_path.write_text("")

        conv = ConversationManager(config)

        assert len(conv.messages) == 1
        assert "User Research Context" not in conv.messages[0].content

    def test_conversation_trims_whitespace_prompt(self, temp_dir):
        """Test ConversationManager trims whitespace from user prompt."""
        config = Config(base_dir=temp_dir)

        # Create prompt with only whitespace
        config.user_prompt_path.write_text("   \n\n   \t   ")

        conv = ConversationManager(config)

        assert len(conv.messages) == 1
        assert "User Research Context" not in conv.messages[0].content
