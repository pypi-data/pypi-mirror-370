"""Tests for BibTeX import functionality."""

import tempfile
from pathlib import Path

from litai.importers.bibtex import (
    bibtex_to_paper,
    clean_latex,
    extract_arxiv_id,
    extract_doi,
    generate_paper_id,
    parse_authors,
    parse_bibtex_file,
)


class TestIdentifierExtraction:
    """Test identifier extraction functions."""

    def test_extract_arxiv_id(self):
        """Test ArXiv ID extraction from various formats."""
        # Test URLs
        assert extract_arxiv_id("https://arxiv.org/abs/2103.14030") == "2103.14030"
        assert extract_arxiv_id("http://arxiv.org/pdf/2103.14030.pdf") == "2103.14030"
        assert extract_arxiv_id("https://arxiv.org/abs/2103.14030v2") == "2103.14030v2"

        # Test just IDs
        assert extract_arxiv_id("2103.14030") == "2103.14030"
        assert extract_arxiv_id("2103.14030v1") == "2103.14030v1"

        # Test invalid
        assert extract_arxiv_id("") is None
        assert extract_arxiv_id("not an arxiv id") is None
        assert extract_arxiv_id(None) is None

    def test_extract_doi(self):
        """Test DOI extraction from various formats."""
        # Test URLs
        assert (
            extract_doi("https://doi.org/10.1038/nature12373") == "10.1038/nature12373"
        )
        assert (
            extract_doi("http://dx.doi.org/10.1038/nature12373")
            == "10.1038/nature12373"
        )

        # Test DOI prefix
        assert extract_doi("doi: 10.1038/nature12373") == "10.1038/nature12373"
        assert extract_doi("DOI:10.1038/nature12373") == "10.1038/nature12373"

        # Test just DOI
        assert extract_doi("10.1038/nature12373") == "10.1038/nature12373"

        # Test invalid
        assert extract_doi("") is None
        assert extract_doi("not a doi") is None
        assert extract_doi(None) is None

    def test_generate_paper_id(self):
        """Test paper ID generation."""
        # Test with ArXiv
        entry = {"ID": "test2021", "url": "https://arxiv.org/abs/2103.14030"}
        assert generate_paper_id(entry) == "arxiv:2103.14030"

        # Test with DOI
        entry = {"ID": "test2021", "doi": "10.1038/nature12373"}
        assert generate_paper_id(entry) == "doi:10.1038/nature12373"

        # Test with both (ArXiv takes precedence)
        entry = {
            "ID": "test2021",
            "url": "https://arxiv.org/abs/2103.14030",
            "doi": "10.1038/nature12373",
        }
        assert generate_paper_id(entry) == "arxiv:2103.14030"

        # Test fallback to hash
        entry = {"ID": "test2021"}
        paper_id = generate_paper_id(entry)
        assert paper_id.startswith("bib:")
        assert len(paper_id) == 16  # "bib:" + 12 char hash


class TestTextProcessing:
    """Test text processing functions."""

    def test_clean_latex(self):
        """Test LaTeX cleaning."""
        # Test common LaTeX commands
        assert clean_latex(r"\textit{italic text}") == "italic text"
        assert clean_latex(r"\textbf{bold text}") == "bold text"
        assert clean_latex(r"\emph{emphasized}") == "emphasized"

        # Test citations
        assert clean_latex(r"Some text \cite{ref1} more text") == "Some text more text"

        # Test braces
        assert clean_latex("{text in braces}") == "text in braces"

        # Test empty/None
        assert clean_latex("") == ""
        assert clean_latex(None) == ""

    def test_parse_authors(self):
        """Test author parsing."""
        # Test single author
        assert parse_authors("John Doe") == ["John Doe"]

        # Test multiple authors
        assert parse_authors("John Doe and Jane Smith") == ["John Doe", "Jane Smith"]

        # Test Last, First format
        assert parse_authors("Doe, John") == ["John Doe"]
        assert parse_authors("Doe, John and Smith, Jane") == ["John Doe", "Jane Smith"]

        # Test mixed format
        assert parse_authors("John Doe and Smith, Jane") == ["John Doe", "Jane Smith"]

        # Test empty
        assert parse_authors("") == []
        assert parse_authors(None) == []


class TestBibTeXConversion:
    """Test BibTeX entry to Paper conversion."""

    def test_bibtex_to_paper_valid(self):
        """Test conversion of valid BibTeX entry."""
        entry = {
            "ID": "test2021",
            "title": "Test Paper Title",
            "author": "Doe, John and Smith, Jane",
            "year": "2021",
            "abstract": "This is a test abstract.",
            "journal": "Test Journal",
            "url": "https://arxiv.org/abs/2103.14030",
            "doi": "10.1038/nature12373",
        }

        paper = bibtex_to_paper(entry)
        assert paper is not None
        assert paper.title == "Test Paper Title"
        assert paper.authors == ["John Doe", "Jane Smith"]
        assert paper.year == 2021
        assert paper.abstract == "This is a test abstract."
        assert paper.venue == "Test Journal"
        assert paper.arxiv_id == "2103.14030"
        assert paper.doi == "10.1038/nature12373"
        assert paper.citation_key == "test2021"
        assert paper.open_access_pdf_url == "https://arxiv.org/pdf/2103.14030.pdf"

    def test_bibtex_to_paper_minimal(self):
        """Test conversion with minimal required fields."""
        entry = {
            "ID": "minimal2021",
            "title": "Minimal Paper",
            "author": "Doe, John",
            "year": "2021",
        }

        paper = bibtex_to_paper(entry)
        assert paper is not None
        assert paper.title == "Minimal Paper"
        assert paper.authors == ["John Doe"]
        assert paper.year == 2021
        assert paper.abstract == ""
        assert paper.venue is None
        assert paper.arxiv_id is None
        assert paper.doi is None
        assert paper.citation_key == "minimal2021"

    def test_bibtex_to_paper_missing_required(self):
        """Test conversion with missing required fields."""
        # Missing title
        entry = {"ID": "test2021", "author": "Doe, John", "year": "2021"}
        assert bibtex_to_paper(entry) is None

        # Missing author
        entry = {"ID": "test2021", "title": "Test", "year": "2021"}
        assert bibtex_to_paper(entry) is None

        # Missing year
        entry = {"ID": "test2021", "title": "Test", "author": "Doe, John"}
        assert bibtex_to_paper(entry) is None


class TestBibTeXFileParsing:
    """Test parsing of BibTeX files."""

    def test_parse_valid_bibtex_file(self):
        """Test parsing a valid BibTeX file."""
        bibtex_content = """
@article{test2021,
    title = {Test Paper Title},
    author = {Doe, John and Smith, Jane},
    year = {2021},
    journal = {Test Journal},
    abstract = {This is a test abstract.}
}

@inproceedings{conference2020,
    title = {Conference Paper},
    author = {Alice Brown},
    year = {2020},
    booktitle = {Test Conference}
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write(bibtex_content)
            temp_path = Path(f.name)

        try:
            papers = parse_bibtex_file(temp_path)
            assert len(papers) == 2

            # Check first paper
            assert papers[0].title == "Test Paper Title"
            assert papers[0].authors == ["John Doe", "Jane Smith"]
            assert papers[0].year == 2021
            assert papers[0].venue == "Test Journal"

            # Check second paper
            assert papers[1].title == "Conference Paper"
            assert papers[1].authors == ["Alice Brown"]
            assert papers[1].year == 2020
            assert papers[1].venue == "Test Conference"
        finally:
            temp_path.unlink()

    def test_parse_empty_bibtex_file(self):
        """Test parsing an empty BibTeX file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            papers = parse_bibtex_file(temp_path)
            assert papers == []
        finally:
            temp_path.unlink()

    def test_parse_malformed_entries(self):
        """Test parsing BibTeX file with some malformed entries."""
        bibtex_content = """
@article{valid2021,
    title = {Valid Paper},
    author = {Doe, John},
    year = {2021}
}

@article{missing_title,
    author = {Smith, Jane},
    year = {2020}
}

@article{valid2020,
    title = {Another Valid Paper},
    author = {Brown, Alice},
    year = {2020}
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write(bibtex_content)
            temp_path = Path(f.name)

        try:
            papers = parse_bibtex_file(temp_path)
            # Should skip the malformed entry
            assert len(papers) == 2
            assert papers[0].title == "Valid Paper"
            assert papers[1].title == "Another Valid Paper"
        finally:
            temp_path.unlink()
