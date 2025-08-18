"""Tests for paper reference resolution using real LLM."""

import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from litai.config import Config
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.paper_resolver import extract_context_type, resolve_paper_references

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
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            citation_count=50000,
            tags=["transformers", "attention", "NLP"],
        ),
        Paper(
            paper_id="bert2018",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang", "Lee", "Toutanova"],
            year=2018,
            abstract="We introduce a new language representation model called BERT.",
            citation_count=40000,
            tags=["BERT", "NLP", "pretraining"],
        ),
        Paper(
            paper_id="gpt3_2020",
            title="Language Models are Few-Shot Learners",
            authors=["Brown", "Mann", "Ryder", "Subbiah"],
            year=2020,
            abstract="Recent work has demonstrated substantial gains on many NLP tasks.",
            citation_count=10000,
            tags=["GPT", "few-shot", "language-models"],
        ),
        Paper(
            paper_id="resnet2016",
            title="Deep Residual Learning for Image Recognition",
            authors=["He", "Zhang", "Ren", "Sun"],
            year=2016,
            abstract="Deeper neural networks are more difficult to train.",
            citation_count=60000,
            tags=["computer-vision", "CNN", "residual"],
        ),
    ]

    for paper in papers:
        db.add_paper(paper)

    return papers


@pytest_asyncio.fixture
async def llm_client(config):
    """Create an LLM client."""
    client = LLMClient(config)
    yield client
    await client.close()


class TestBasicPaperResolution:
    """Test basic paper reference resolution scenarios."""

    @pytest.mark.asyncio
    async def test_resolve_attention_paper(self, db, llm_client, sample_papers):
        """Test resolving 'attention paper' to the correct paper ID."""
        query = "Tell me about the attention paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"
        assert "Attention Is All You Need" in resolved_query
        assert "attention2017" in resolved_query

    @pytest.mark.asyncio
    async def test_resolve_bert_paper(self, db, llm_client, sample_papers):
        """Test resolving 'BERT paper' to the correct paper ID."""
        query = "What does the BERT paper say about embeddings?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "bert2018"
        assert "BERT: Pre-training of Deep Bidirectional Transformers" in resolved_query

    @pytest.mark.asyncio
    async def test_resolve_by_author(self, db, llm_client, sample_papers):
        """Test resolving paper by author name."""
        query = "Show me the paper by Vaswani"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"
        assert "Attention Is All You Need" in resolved_query

    @pytest.mark.asyncio
    async def test_resolve_by_year(self, db, llm_client, sample_papers):
        """Test resolving paper by publication year."""
        query = "Tell me about the 2020 paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "gpt3_2020"
        assert "Language Models are Few-Shot Learners" in resolved_query

    @pytest.mark.asyncio
    async def test_resolve_transformer_paper(self, db, llm_client, sample_papers):
        """Test resolving 'transformer paper' to attention paper."""
        query = "Explain the transformer paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"
        assert "Attention Is All You Need" in resolved_query

    @pytest.mark.asyncio
    async def test_resolve_resnet_paper(self, db, llm_client, sample_papers):
        """Test resolving computer vision paper."""
        query = "What about the ResNet paper?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "resnet2016"
        assert "Deep Residual Learning for Image Recognition" in resolved_query


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_empty_collection(self, config, llm_client):
        """Test resolution with empty paper collection."""
        empty_db = Database(config)
        query = "Tell me about the attention paper"

        resolved_query, paper_id = await resolve_paper_references(
            query, empty_db, llm_client,
        )

        assert paper_id is None
        assert resolved_query == query  # Original query unchanged

    @pytest.mark.asyncio
    async def test_no_paper_reference(self, db, llm_client, sample_papers):
        """Test query with no paper references."""
        query = "What is machine learning?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id is None
        assert resolved_query == query  # Original query unchanged

    @pytest.mark.asyncio
    async def test_multiple_paper_references(self, db, llm_client, sample_papers):
        """Test query referencing multiple papers."""
        query = "Compare the BERT and attention papers"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        # Should not resolve when multiple papers are referenced
        assert paper_id is None
        assert resolved_query == query

    @pytest.mark.asyncio
    async def test_ambiguous_reference(self, db, llm_client, sample_papers):
        """Test ambiguous paper reference."""
        query = "Tell me about the paper"  # Too vague
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        # Should not resolve ambiguous references
        assert paper_id is None
        assert resolved_query == query

    @pytest.mark.asyncio
    async def test_nonexistent_paper_reference(self, db, llm_client, sample_papers):
        """Test reference to paper not in collection."""
        query = "Tell me about the AlexNet paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        # Should not resolve references to papers not in collection
        assert paper_id is None
        assert resolved_query == query


class TestQueryTypes:
    """Test different types of queries with paper references."""

    @pytest.mark.asyncio
    async def test_command_style_query(self, db, llm_client, sample_papers):
        """Test command-style queries like '/note attention paper'."""
        query = "attention paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"
        assert "Attention Is All You Need" in resolved_query

    @pytest.mark.asyncio
    async def test_question_about_paper(self, db, llm_client, sample_papers):
        """Test questions about specific papers."""
        query = "What are the key contributions of the BERT study?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "bert2018"
        assert "BERT: Pre-training of Deep Bidirectional Transformers" in resolved_query

    @pytest.mark.asyncio
    async def test_analysis_request(self, db, llm_client, sample_papers):
        """Test analysis requests."""
        query = "Analyze the methodology in the transformer paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"
        assert "Attention Is All You Need" in resolved_query

    @pytest.mark.asyncio
    async def test_note_taking_query(self, db, llm_client, sample_papers):
        """Test note-taking style queries."""
        query = "Add a note to the GPT-3 paper about few-shot learning"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "gpt3_2020"
        assert "Language Models are Few-Shot Learners" in resolved_query

    @pytest.mark.asyncio
    async def test_tagging_query(self, db, llm_client, sample_papers):
        """Test tagging style queries."""
        query = "Tag the BERT paper with deep-learning"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "bert2018"
        assert "BERT: Pre-training of Deep Bidirectional Transformers" in resolved_query


class TestReferencePatterns:
    """Test different ways of referring to papers."""

    @pytest.mark.asyncio
    async def test_informal_names(self, db, llm_client, sample_papers):
        """Test informal paper names."""
        test_cases = [
            ("the attention paper", "attention2017"),
            ("transformer paper", "attention2017"),
            ("BERT paper", "bert2018"),
            ("GPT-3 paper", "gpt3_2020"),
            ("ResNet paper", "resnet2016"),
        ]

        for query_text, expected_id in test_cases:
            query = f"Tell me about {query_text}"
            resolved_query, paper_id = await resolve_paper_references(
                query, db, llm_client,
            )
            assert paper_id == expected_id, (
                f"Failed to resolve '{query_text}' to {expected_id}"
            )

    @pytest.mark.asyncio
    async def test_partial_titles(self, db, llm_client, sample_papers):
        """Test partial title references."""
        query = "What does 'Attention Is All You Need' discuss?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id == "attention2017"

    @pytest.mark.asyncio
    async def test_author_references(self, db, llm_client, sample_papers):
        """Test author-based references."""
        test_cases = [
            ("paper by Vaswani", "attention2017"),
            ("Devlin paper", "bert2018"),
            ("Brown et al paper", "gpt3_2020"),
            ("He paper", "resnet2016"),
        ]

        for query_text, expected_id in test_cases:
            query = f"Show me the {query_text}"
            resolved_query, paper_id = await resolve_paper_references(
                query, db, llm_client,
            )
            assert paper_id == expected_id, (
                f"Failed to resolve '{query_text}' to {expected_id}"
            )


class TestLLMErrorHandling:
    """Test handling of LLM errors and edge cases."""

    @pytest.mark.asyncio
    async def test_llm_returns_invalid_id(
        self, db, llm_client, sample_papers, monkeypatch,
    ):
        """Test handling when LLM returns invalid paper ID."""

        # Mock the LLM to return an invalid ID
        async def mock_complete(prompt):
            return "invalid_id_123"

        monkeypatch.setattr(llm_client, "complete", mock_complete)

        query = "Tell me about the attention paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        # Should fallback to original query when invalid ID is returned
        assert paper_id is None
        assert resolved_query == query

    @pytest.mark.asyncio
    async def test_llm_exception(self, db, llm_client, sample_papers, monkeypatch):
        """Test handling when LLM throws exception."""

        # Mock the LLM to throw exception
        async def mock_complete(prompt):
            raise Exception("LLM error")

        monkeypatch.setattr(llm_client, "complete", mock_complete)

        query = "Tell me about the attention paper"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        # Should fallback to original query when exception occurs
        assert paper_id is None
        assert resolved_query == query

    @pytest.mark.asyncio
    async def test_llm_returns_none_correctly(
        self, db, llm_client, sample_papers, monkeypatch,
    ):
        """Test when LLM correctly returns NONE."""

        # Mock the LLM to return NONE
        async def mock_complete(prompt):
            return "NONE"

        monkeypatch.setattr(llm_client, "complete", mock_complete)

        query = "What is machine learning?"
        resolved_query, paper_id = await resolve_paper_references(query, db, llm_client)

        assert paper_id is None
        assert resolved_query == query


class TestExtractContextType:
    """Test context type extraction from natural language."""

    def test_extract_full_text(self):
        """Test extracting full_text context type."""
        test_cases = [
            "full text",
            "full-text",
            "give me the full version",
            "entire paper",
            "Full document",
            "FULL TEXT",
        ]

        for text in test_cases:
            assert extract_context_type(text) == "full_text", f"Failed for: {text}"

    def test_extract_notes(self):
        """Test extracting notes context type."""
        test_cases = [
            "notes",
            "key points",
            "summary",
            "key point",
            "my notes",
            "NOTES",
            "Summary of paper",
        ]

        for text in test_cases:
            assert extract_context_type(text) == "notes", f"Failed for: {text}"

    def test_extract_abstract(self):
        """Test extracting abstract context type."""
        test_cases = [
            "abstract",
            "overview",
            "paper abstract",
            "ABSTRACT",
            "quick overview",
        ]

        for text in test_cases:
            assert extract_context_type(text) == "abstract", f"Failed for: {text}"

    def test_default_to_full_text(self):
        """Test defaulting to full_text when unclear."""
        test_cases = [
            "something else",
            "paper",
            "document",
            "content",
            "",
            "xyz",
        ]

        for text in test_cases:
            assert extract_context_type(text) == "full_text", f"Failed for: {text}"

    def test_mixed_context(self):
        """Test extraction from mixed text."""
        assert extract_context_type("I want the full text of the paper") == "full_text"
        assert extract_context_type("Show me the abstract section") == "abstract"
        assert extract_context_type("Get my notes on this") == "notes"
        assert extract_context_type("Can you pull up the summary?") == "notes"


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.mark.asyncio
    async def test_research_workflow(self, db, llm_client, sample_papers):
        """Test typical research workflow queries."""
        scenarios = [
            "Add a note to the attention paper about multi-head attention",
            "Tag the BERT paper with bidirectional",
            "What are the limitations mentioned in the GPT-3 paper?",
            "Compare the ResNet approach with traditional CNNs",
        ]

        for query in scenarios:
            resolved_query, paper_id = await resolve_paper_references(
                query, db, llm_client,
            )
            # Should resolve to some paper
            assert paper_id is not None, f"Failed to resolve: {query}"
            assert paper_id in ["attention2017", "bert2018", "gpt3_2020", "resnet2016"]

    @pytest.mark.asyncio
    async def test_command_integration(self, db, llm_client, sample_papers):
        """Test integration with command-style inputs."""
        command_queries = [
            "attention paper",  # Simple reference
            "BERT paper important findings",  # Reference with context
            "transformer paper methodology",  # Alternative name
        ]

        for query in command_queries:
            resolved_query, paper_id = await resolve_paper_references(
                query, db, llm_client,
            )
            assert paper_id is not None
            assert any(
                title in resolved_query
                for title in [
                    "Attention Is All You Need",
                    "BERT: Pre-training of Deep Bidirectional Transformers",
                ]
            )
