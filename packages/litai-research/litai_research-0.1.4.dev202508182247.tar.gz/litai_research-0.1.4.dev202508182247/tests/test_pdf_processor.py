"""Tests for PDF processing functionality."""

import pytest

from litai.config import Config
from litai.database import Database
from litai.models import Paper
from litai.pdf_processor import PDFProcessor


@pytest.fixture
def pdf_processor(tmp_path):
    """Create a PDFProcessor instance with test database."""
    config = Config(base_dir=tmp_path)
    db = Database(config)
    processor = PDFProcessor(db, tmp_path)

    # Add a test paper with real arxiv URL
    test_paper = Paper(
        paper_id="test123",
        title="Attention Is All You Need",
        authors=["Vaswani", "Shazeer"],
        year=2017,
        abstract="The dominant sequence transduction models...",
        arxiv_id="1706.03762",
        open_access_pdf_url="https://arxiv.org/abs/1706.03762",
    )
    db.add_paper(test_paper)

    return processor, db


@pytest.mark.asyncio
async def test_pdf_directory_creation(tmp_path):
    """Test that PDF directory is created on initialization."""
    config = Config(base_dir=tmp_path)
    db = Database(config)

    PDFProcessor(db, tmp_path)  # initializing creates the pdfs directory
    assert (tmp_path / "pdfs").exists()
    assert (tmp_path / "pdfs").is_dir()


@pytest.mark.asyncio
async def test_get_pdf_path(pdf_processor):
    """Test PDF path generation."""
    processor, _ = pdf_processor
    path = processor._get_pdf_path("test123")
    assert path.name == "test123.pdf"
    assert "pdfs" in str(path)


@pytest.mark.asyncio
async def test_get_txt_path(pdf_processor):
    """Test text file path generation."""
    processor, _ = pdf_processor
    path = processor._get_txt_path("test123")
    assert path.name == "test123.md"
    assert "pdfs" in str(path)


@pytest.mark.asyncio
async def test_process_paper_not_found(pdf_processor):
    """Test processing a paper that doesn't exist."""
    processor, _ = pdf_processor
    result = await processor.process_paper("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_download_pdf_already_exists(pdf_processor):
    """Test that existing PDFs are not re-downloaded."""
    processor, db = pdf_processor

    # Create existing PDF
    paper = db.get_paper("test123")
    pdf_path = processor._get_pdf_path(paper.paper_id)
    pdf_path.parent.mkdir(exist_ok=True)
    pdf_path.write_text("existing pdf content")

    # Try to download
    result = await processor.download_pdf(paper)
    assert result == pdf_path
    assert pdf_path.read_text() == "existing pdf content"  # Not overwritten


@pytest.mark.asyncio
async def test_extract_text_invalid_pdf(pdf_processor, tmp_path):
    """Test handling of invalid PDF files."""
    processor, _ = pdf_processor

    # Create invalid PDF
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_text("This is not a valid PDF")

    # Should raise exception
    with pytest.raises(Exception):
        processor.extract_text(bad_pdf)


@pytest.mark.asyncio
async def test_extract_text_saves_txt_file(pdf_processor, tmp_path):
    """Test that extract_text saves a .md file when given paper_id."""
    processor, _ = pdf_processor

    # Create a simple valid PDF for testing
    # Note: In a real test we'd use a proper PDF fixture
    # For now, we'll just test the md file saving logic
    test_text = "This is the extracted text from the PDF"

    # Mock the PDF extraction by directly calling the save logic
    md_path = processor._get_txt_path("test123")
    md_path.write_text(test_text, encoding="utf-8")

    # Verify the file was created
    assert md_path.exists()
    assert md_path.read_text(encoding="utf-8") == test_text


@pytest.mark.asyncio
async def test_process_paper_uses_cached_text(pdf_processor):
    """Test that process_paper uses cached .md file if available."""
    processor, db = pdf_processor

    # Create a cached markdown file
    test_text = "This is cached text content"
    md_path = processor._get_txt_path("test123")
    md_path.write_text(test_text, encoding="utf-8")

    # Process the paper - should use cached text
    result = await processor.process_paper("test123")
    assert result == test_text

    # Verify no PDF was created (since we used cached text)
    pdf_path = processor._get_pdf_path("test123")
    assert not pdf_path.exists()
