"""Tests for data models."""

from litai.models import LLMConfig, Paper


class TestLLMConfig:
    """Test the LLMConfig model."""

    def test_default_values(self):
        """Test default LLMConfig values."""
        config = LLMConfig()
        assert config.provider == "auto"
        assert config.model is None
        assert config.api_key_env is None
        assert config.is_auto is True

    def test_custom_values(self):
        """Test LLMConfig with custom values."""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key_env="MY_API_KEY",
        )
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key_env == "MY_API_KEY"
        assert config.is_auto is False

    def test_to_dict(self):
        """Test converting LLMConfig to dict."""
        config = LLMConfig(provider="anthropic", model="claude-3")
        d = config.to_dict()

        assert d == {
            "provider": "anthropic",
            "model": "claude-3",
            "api_key_env": None,
        }

    def test_from_dict(self):
        """Test creating LLMConfig from dict."""
        data = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key_env": "CUSTOM_KEY",
        }
        config = LLMConfig.from_dict(data)

        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key_env == "CUSTOM_KEY"

    def test_from_dict_with_defaults(self):
        """Test creating LLMConfig from partial dict."""
        config = LLMConfig.from_dict({})
        assert config.provider == "auto"
        assert config.model is None
        assert config.api_key_env is None

        config = LLMConfig.from_dict({"provider": "anthropic"})
        assert config.provider == "anthropic"
        assert config.model is None
        assert config.api_key_env is None


class TestPaper:
    """Test the Paper model."""

    def test_citation_key_single_author(self):
        """Test citation key with single author."""
        paper = Paper(
            paper_id="123",
            title="Learning from Data",
            authors=["John Smith"],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "smith-2024-learning"

    def test_citation_key_multiple_authors(self):
        """Test citation key with multiple authors."""
        paper = Paper(
            paper_id="124",
            title="Neural Networks for NLP",
            authors=["Alice Johnson", "Bob Williams", "Charlie Brown"],
            year=2023,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "johnson-etal-2023-neural"

    def test_citation_key_skip_common_words(self):
        """Test that common words are skipped in title."""
        paper = Paper(
            paper_id="125",
            title="The Analysis of Large Language Models",
            authors=["Emily Davis"],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "davis-2024-analysis"

    def test_citation_key_no_year(self):
        """Test citation key when year is missing."""
        paper = Paper(
            paper_id="126",
            title="Machine Learning Research",
            authors=["Frank Miller"],
            year=0,  # 0 is falsy
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "miller-nd-machine"

    def test_citation_key_no_authors(self):
        """Test citation key when authors are missing."""
        paper = Paper(
            paper_id="127",
            title="Autonomous Systems",
            authors=[],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "unknown-2024-autonomous"

    def test_citation_key_special_characters(self):
        """Test citation key with special characters in names."""
        paper = Paper(
            paper_id="128",
            title="Deep Learning Applications",
            authors=["José García-López", "François Müller"],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "garcia-lopez-etal-2024-deep"  # Hyphen is preserved in last name

    def test_citation_key_duplicates(self):
        """Test handling of duplicate citation keys."""
        existing_keys = {"smith-2024-learning", "smith-2024-learning-2"}
        paper = Paper(
            paper_id="129",
            title="Learning from Experience",
            authors=["John Smith"],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key(existing_keys)
        assert key == "smith-2024-learning-3"

    def test_citation_key_short_title(self):
        """Test with very short title or all common words."""
        paper = Paper(
            paper_id="130",
            title="The In Of",  # All common words
            authors=["Grace Wilson"],
            year=2024,
            abstract="Test abstract",
        )
        key = paper.generate_citation_key()
        assert key == "wilson-2024-paper"  # Falls back to "paper"
