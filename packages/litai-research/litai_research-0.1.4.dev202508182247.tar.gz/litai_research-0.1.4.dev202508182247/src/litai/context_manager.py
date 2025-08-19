"""Context management for papers in conversation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litai.utils.logger import get_logger

if TYPE_CHECKING:
    from litai.config import Config
    from litai.database import Database

logger = get_logger(__name__)


@dataclass
class ContextEntry:
    """Represents a paper in the context with a single extraction type."""

    paper_id: str
    paper_title: str
    context_type: str  # Single type instead of set


class SessionContext:
    """Manages papers and their context for the current session."""

    def __init__(self) -> None:
        self.papers: dict[str, ContextEntry] = {}
        logger.info("session_context_initialized")

    def add_paper(self, paper_id: str, paper_title: str, context_type: str) -> None:
        """Add a paper with a specific context type. Replaces any existing context."""
        if paper_id in self.papers:
            logger.info(
                "paper_context_replaced",
                paper_id=paper_id,
                old_type=self.papers[paper_id].context_type,
                new_type=context_type,
            )
        else:
            logger.info("paper_added_to_context", paper_id=paper_id, title=paper_title)
        self.papers[paper_id] = ContextEntry(paper_id, paper_title, context_type)
        logger.info("context_type_set", paper_id=paper_id, context_type=context_type)

    def remove_paper(self, paper_id: str) -> None:
        """Remove a paper from context."""
        if paper_id in self.papers:
            del self.papers[paper_id]
            logger.info("paper_removed_from_context", paper_id=paper_id)

    def clear(self) -> None:
        """Clear all context."""
        self.papers.clear()
        logger.info("context_cleared")

    async def get_all_context(
        self, db: Database, config: Config,
    ) -> str:
        """Get combined context from all papers for synthesis.

        Args:
            db: Database instance for loading content
            config: Config instance for PDFProcessor
        """
        if not self.papers:
            return ""

        # Load actual content based on context type
        combined = []
        for paper_id, entry in self.papers.items():
            combined.append(f"Paper: {entry.paper_title}")
            combined.append(f"=== {entry.context_type.upper()} ===")

            content = await self._load_paper_content(
                db, paper_id, entry.context_type, config,
            )
            if content:
                combined.append(content)
            else:
                combined.append(f"[Content not available for {entry.context_type}]")

            combined.append("")  # Blank line between papers

        return "\n".join(combined)

    async def _load_paper_content(
        self,
        db: Database,
        paper_id: str,
        context_type: str,
        config: Config | None = None,
    ) -> str | None:
        """Load content for a paper based on context type.

        Args:
            db: Database instance
            paper_id: Paper ID
            context_type: Type of content to load (full_text, abstract, notes)
            config: Config instance for PDFProcessor (required for full_text)

        Returns:
            Content string or None if not available
        """
        try:
            if context_type == "abstract":
                paper = db.get_paper(paper_id)
                return paper.abstract if paper else None

            if context_type == "notes":
                return db.get_note(paper_id)

            if context_type == "full_text":
                # First try to get cached full text
                full_text = db.get_full_text(paper_id)
                if full_text:
                    return full_text

                # If not cached and we have config, try using PDFProcessor
                if config:
                    from litai.pdf_processor import PDFProcessor

                    pdf_processor = PDFProcessor(db, config.base_dir)

                    try:
                        # Try to process the paper (download + extract if needed)
                        full_text = await pdf_processor.process_paper(paper_id)
                        if full_text:
                            return full_text
                        # Fall back to abstract if PDF processing failed
                        paper = db.get_paper(paper_id)
                        if paper and paper.abstract:
                            logger.warning(
                                "pdf_processing_failed_fallback_to_abstract",
                                paper_id=paper_id,
                                title=paper.title,
                            )
                            # Also print user-friendly warning
                            from rich.console import Console

                            console = Console()
                            console.print(
                                f"[yellow]Could not download full text for '{paper.title}', using abstract[/yellow]",
                            )
                            return paper.abstract
                    except Exception as e:
                        logger.error(
                            "pdf_processor_error", paper_id=paper_id, error=str(e),
                        )
                        # Fall back to abstract
                        paper = db.get_paper(paper_id)
                        if paper and paper.abstract:
                            logger.warning(
                                "pdf_processing_error_fallback_to_abstract",
                                paper_id=paper_id,
                                title=paper.title,
                            )
                            # Also print user-friendly warning
                            from rich.console import Console

                            console = Console()
                            console.print(
                                f"[yellow]Could not download full text for '{paper.title}', using abstract[/yellow]",
                            )
                            return paper.abstract

                return None

            logger.warning(
                "unknown_context_type", context_type=context_type, paper_id=paper_id,
            )
            return None

        except Exception as e:
            logger.error(
                "content_loading_failed",
                paper_id=paper_id,
                context_type=context_type,
                error=str(e),
            )
            return None

    def get_paper_count(self) -> int:
        """Get number of papers in context."""
        return len(self.papers)

    def has_paper(self, paper_id: str) -> bool:
        """Check if a paper is in context."""
        return paper_id in self.papers

    def get_all_papers(self) -> dict[str, str]:
        """Get all papers with their context type."""
        return {paper_id: entry.context_type for paper_id, entry in self.papers.items()}
