"""Tests for Semantic Scholar API client."""

import pytest

from litai.semantic_scholar import SemanticScholarClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.semantic_scholar
async def test_search_real_api():
    """Integration test: actually search for papers."""
    async with SemanticScholarClient() as client:
        papers = await client.search("attention is all you need", limit=5)

        # Should find the famous transformer paper
        assert len(papers) > 0
        assert any("attention" in p.title.lower() for p in papers)

        # Check paper has expected fields
        paper = papers[0]
        assert paper.paper_id
        assert paper.title
        assert paper.authors
        assert paper.year >= 2017  # Paper was published in 2017


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.semantic_scholar
async def test_search_no_results():
    """Integration test: search that returns no results."""
    async with SemanticScholarClient() as client:
        papers = await client.search("xyzabc123randomquery", limit=5)
        assert len(papers) == 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.semantic_scholar
async def test_get_paper_by_id():
    """Integration test: get a known paper by ID."""
    # Using a well-known paper ID (Attention is All You Need)
    paper_id = "204e3073870fae3d05bcbc2f6a8e263d9b72e776"

    async with SemanticScholarClient() as client:
        paper = await client.get_paper(paper_id)

        assert paper is not None
        assert paper.paper_id == paper_id
        assert "attention" in paper.title.lower()
        assert paper.year == 2017
        assert len(paper.authors) > 0


def test_paper_conversion():
    """Test conversion from API response to Paper model."""
    # This tests actual logic, not just mocks
    client = SemanticScholarClient()

    # Test with full data
    api_data = {
        "paperId": "test123",
        "title": "Test Paper",
        "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}],
        "year": 2023,
        "abstract": "Test abstract",
        "citationCount": 42,
        "tldr": {"text": "Short summary"},
        "openAccessPdf": {"url": "https://example.com/paper.pdf"},
        "externalIds": {"ArXiv": "2301.00000", "DOI": "10.1234/test"},
        "venue": "ICML",
    }

    paper = client._convert_to_paper(api_data)

    assert paper.paper_id == "test123"
    assert paper.title == "Test Paper"
    assert paper.authors == ["John Doe", "Jane Smith"]
    assert paper.year == 2023
    assert paper.tldr == "Short summary"
    assert paper.arxiv_id == "2301.00000"
    assert paper.doi == "10.1234/test"
    assert paper.open_access_pdf_url == "https://example.com/paper.pdf"

    # Test with minimal data
    minimal_data = {
        "paperId": "test456",
        "title": "Minimal Paper",
    }

    paper = client._convert_to_paper(minimal_data)
    assert paper.paper_id == "test456"
    assert paper.authors == []
    assert paper.year == 0
    assert paper.tldr is None
