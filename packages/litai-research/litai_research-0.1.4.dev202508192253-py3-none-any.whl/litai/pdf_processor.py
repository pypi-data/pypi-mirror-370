"""PDF processing functionality for downloading and extracting text from papers."""

import logging
from pathlib import Path

import arxiv  # type: ignore[import-untyped]
import pymupdf4llm  # type: ignore[import-untyped]

from litai.database import Database
from litai.models import Paper
from litai.utils.logger import get_logger

logger = get_logger(__name__)

# Silence arxiv package logging
logging.getLogger("arxiv").setLevel(logging.WARNING)


class PDFProcessor:
    """Handles PDF downloading and text extraction for papers."""

    def __init__(self, db: Database, base_dir: Path):
        """Initialize PDF processor.

        Args:
            db: Database instance for paper lookup
            base_dir: Base directory for storing PDFs (usually ~/.litai)
        """
        self.db = db
        self.pdf_dir = base_dir / "pdfs"
        self.pdf_dir.mkdir(exist_ok=True)
        self.arxiv_client = arxiv.Client()

    def _get_pdf_path(self, paper_id: str) -> Path:
        """Get the local path for a paper's PDF.

        Args:
            paper_id: Paper ID

        Returns:
            Path to PDF file
        """
        return self.pdf_dir / f"{paper_id}.pdf"

    def _get_txt_path(self, paper_id: str) -> Path:
        """Get the local path for a paper's extracted text.

        Args:
            paper_id: Paper ID

        Returns:
            Path to text file
        """
        return self.pdf_dir / f"{paper_id}.md"

    async def download_pdf(self, paper: Paper) -> Path | None:
        """Download PDF for a paper using arxiv.

        Args:
            paper: Paper object with title and authors

        Returns:
            Path to downloaded PDF or None if download failed
        """
        pdf_path = self._get_pdf_path(paper.paper_id)

        # Check if already downloaded
        if pdf_path.exists():
            await logger.ainfo(
                "pdf_already_exists",
                paper_id=paper.paper_id,
                path=str(pdf_path),
            )
            return pdf_path

        try:
            # If paper has arxiv_id, use it directly
            if paper.arxiv_id:
                await logger.ainfo(
                    "searching_by_arxiv_id",
                    paper_id=paper.paper_id,
                    arxiv_id=paper.arxiv_id,
                )
                search = arxiv.Search(id_list=[paper.arxiv_id])
                results = list(self.arxiv_client.results(search))

                if results:
                    result = results[0]
                else:
                    await logger.awarning(
                        "arxiv_id_not_found",
                        paper_id=paper.paper_id,
                        arxiv_id=paper.arxiv_id,
                    )
                    return None
            else:
                # @TODO: This will sometimes just pull in a random paper
                # Fallback to title search if no arxiv_id
                # Build author query
                author_query = ""
                if paper.authors:
                    first_author = paper.authors[0]
                    author_query = f" AND au:{first_author}"

                # Try specific search with title and author
                search = arxiv.Search(
                    query=f"ti:{paper.title}{author_query}",
                    max_results=1,
                )
                results = list(self.arxiv_client.results(search))

                # If no results, try title only
                if not results:
                    await logger.ainfo(
                        "trying_title_only_search", paper_id=paper.paper_id,
                    )
                    search = arxiv.Search(query=paper.title, max_results=1)
                    results = list(self.arxiv_client.results(search))

                if not results:
                    await logger.awarning(
                        "no_arxiv_results",
                        paper_id=paper.paper_id,
                        title=paper.title,
                    )
                    return None

                result = results[0]

            # Check if titles match (case-insensitive)
            arxiv_title = result.title.lower().strip()
            paper_title = paper.title.lower().strip()

            if arxiv_title != paper_title:
                await logger.awarning(
                    "title_mismatch",
                    paper_id=paper.paper_id,
                    expected=paper_title,
                    found=arxiv_title,
                )
                # You might want to be more lenient here
                # For now, we'll continue with the download

            # Download PDF
            await logger.ainfo(
                "downloading_pdf",
                paper_id=paper.paper_id,
                arxiv_id=result.entry_id,
                title=result.title,
            )

            downloaded_path = result.download_pdf(dirpath=str(self.pdf_dir))

            # Rename to our standard naming
            if downloaded_path:
                downloaded_path = Path(downloaded_path)
                if downloaded_path != pdf_path:
                    downloaded_path.rename(pdf_path)

                await logger.ainfo(
                    "pdf_downloaded",
                    paper_id=paper.paper_id,
                    size=pdf_path.stat().st_size,
                )
                return pdf_path

        except Exception as e:
            await logger.aexception(
                "pdf_download_failed",
                paper_id=paper.paper_id,
                error=str(e),
            )
            return None
        return None

    def extract_text(
        self, pdf_path: Path, save_as_txt: bool = True, paper_id: str | None = None,
    ) -> str:
        """Extract text from a PDF file.

        Args:
            pdf_path: Path to PDF file
            save_as_txt: Whether to save extracted text as .txt file
            paper_id: Paper ID for saving text file (required if save_as_txt is True)

        Returns:
            Extracted text
        """
        try:
            # Use pymupdf4llm for better text extraction with markdown formatting
            full_text: str = pymupdf4llm.to_markdown(str(pdf_path))

            logger.info(
                "text_extracted",
                pdf_path=str(pdf_path),
                text_length=len(full_text),
            )

            # Save as markdown file if requested
            if save_as_txt and paper_id:
                md_path = self._get_txt_path(paper_id)
                md_path.write_text(full_text, encoding="utf-8")
                logger.info(
                    "text_cached",
                    paper_id=paper_id,
                    md_path=str(md_path),
                    size=md_path.stat().st_size,
                )

            return full_text

        except Exception as e:
            logger.exception(
                "pdf_extraction_failed",
                pdf_path=str(pdf_path),
                error=str(e),
            )
            raise

    async def process_paper(self, paper_id: str) -> str | None:
        """Download and extract text from a paper.

        Args:
            paper_id: ID of the paper to process

        Returns:
            Extracted text or None if processing failed
        """
        # Get paper from database
        paper = self.db.get_paper(paper_id)
        if not paper:
            await logger.aerror("paper_not_found", paper_id=paper_id)
            return None

        # Check if markdown file already exists
        md_path = self._get_txt_path(paper_id)
        if md_path.exists():
            await logger.ainfo(
                "text_cache_hit",
                paper_id=paper_id,
                md_path=str(md_path),
            )
            try:
                return md_path.read_text(encoding="utf-8")
            except Exception as e:
                await logger.awarning(
                    "text_cache_read_failed",
                    paper_id=paper_id,
                    error=str(e),
                )
                # Fall through to re-extract

        # Check if PDF already exists
        pdf_path = self._get_pdf_path(paper_id)

        # Download if needed
        if not pdf_path.exists():
            downloaded_path = await self.download_pdf(paper)
            if not downloaded_path:
                return None

        # Extract text
        try:
            return self.extract_text(pdf_path, save_as_txt=True, paper_id=paper_id)
        except Exception:
            return None
