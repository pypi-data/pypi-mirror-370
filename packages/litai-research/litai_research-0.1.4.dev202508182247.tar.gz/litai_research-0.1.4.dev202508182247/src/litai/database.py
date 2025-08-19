"""Database management for LitAI."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from litai.utils.logger import get_logger

from .config import Config
from .models import Paper

logger = get_logger(__name__)


class Database:
    """Manages SQLite database for papers."""

    def __init__(self, config: Config):
        """Initialize database with config.

        Args:
            config: Configuration object with database path
        """
        self.config = config
        self.db_path = config.db_path
        self._init_db()

    @contextmanager
    def _get_conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _row_to_paper(self, row: sqlite3.Row) -> Paper:
        """Convert a database row to a Paper object."""
        paper = Paper.from_dict(dict(row))
        # Parse tags from CSV field
        if row["tags"]:
            paper.tags = [tag.strip() for tag in row["tags"].split(",")]
        return paper

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self._get_conn() as conn:
            # Papers table with tags and notes right after title
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    tags TEXT,        
                    notes TEXT,         
                    authors TEXT NOT NULL,  -- JSON list
                    year INTEGER NOT NULL,
                    abstract TEXT NOT NULL,
                    arxiv_id TEXT,
                    doi TEXT,
                    citation_count INTEGER DEFAULT 0,
                    tldr TEXT,
                    venue TEXT,
                    open_access_pdf_url TEXT,
                    added_at TEXT NOT NULL,
                    citation_key TEXT,
                    UNIQUE(arxiv_id),
                    UNIQUE(doi)
                )
            """)

            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")

            logger.info("Database initialized", path=str(self.db_path))

    # Paper CRUD operations

    def add_paper(self, paper: Paper) -> bool:
        """Add a paper to the database.

        Args:
            paper: Paper object to add

        Returns:
            True if added successfully, False if already exists
        """
        try:
            with self._get_conn() as conn:
                data = paper.to_dict()
                conn.execute(
                    """
                    INSERT INTO papers (
                        paper_id, title, authors, year, abstract,
                        arxiv_id, doi, citation_count, tldr, venue,
                        open_access_pdf_url, added_at, citation_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["paper_id"],
                        data["title"],
                        data["authors"],
                        data["year"],
                        data["abstract"],
                        data["arxiv_id"],
                        data["doi"],
                        data["citation_count"],
                        data["tldr"],
                        data["venue"],
                        data["open_access_pdf_url"],
                        data["added_at"],
                        data["citation_key"],
                    ),
                )
                logger.info("Paper added", paper_id=paper.paper_id, title=paper.title)
                return True
        except sqlite3.IntegrityError as e:
            # Check what type of constraint was violated
            error_msg = str(e).lower()
            if "paper_id" in error_msg:
                constraint_type = "paper_id"
            elif "arxiv_id" in error_msg:
                constraint_type = "arxiv_id"
            elif "doi" in error_msg:
                constraint_type = "doi"
            else:
                constraint_type = "unknown"

            logger.warning(
                "Paper already exists",
                paper_id=paper.paper_id,
                constraint_violated=constraint_type,
                arxiv_id=paper.arxiv_id,
                doi=paper.doi,
                error_details=str(e),
            )
            return False

    def get_paper(self, paper_id: str) -> Paper | None:
        """Get a paper by ID.

        Args:
            paper_id: ID of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            if row:
                return self._row_to_paper(row)
            return None

    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        """Get a paper by ArXiv ID.

        Args:
            arxiv_id: ArXiv ID of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        if not arxiv_id:
            return None

        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE arxiv_id = ?",
                (arxiv_id,),
            ).fetchone()

            if row:
                return self._row_to_paper(row)
            return None

    def get_paper_by_doi(self, doi: str) -> Paper | None:
        """Get a paper by DOI.

        Args:
            doi: DOI of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        if not doi:
            return None

        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE doi = ?",
                (doi,),
            ).fetchone()

            if row:
                return self._row_to_paper(row)
            return None

    def list_papers(
        self, limit: int = 50, offset: int = 0, tag: str | None = None,
    ) -> list[Paper]:
        """list all papers in the database, optionally filtered by tag.

        Args:
            limit: Maximum number of papers to return
            offset: Number of papers to skip
            tag: Optional tag name to filter by

        Returns:
            list of Paper objects
        """
        with self._get_conn() as conn:
            if tag:
                # Filter by tag using LIKE on CSV tags
                # Handle tags at beginning, middle, and end of comma-separated list
                # Account for spaces after commas in storage format
                tag = tag.lower().strip()
                rows = conn.execute(
                    """
                    SELECT * FROM papers
                    WHERE LOWER(tags) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(tags) = ?
                    ORDER BY added_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (
                        f"{tag},%",
                        f"{tag}, %",
                        f"%, {tag}",
                        f"%,{tag}",
                        tag,
                        limit,
                        offset,
                    ),
                ).fetchall()
            else:
                # No tag filter
                rows = conn.execute(
                    "SELECT * FROM papers ORDER BY added_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()

            papers = []
            for row in rows:
                papers.append(self._row_to_paper(row))
            return papers

    def count_papers(self) -> int:
        """Get total number of papers in database."""
        with self._get_conn() as conn:
            result = conn.execute("SELECT COUNT(*) FROM papers").fetchone()
            return result[0] if result else 0

    def search_papers(self, query: str) -> list[Paper]:
        """Search papers by title or abstract.

        Args:
            query: Search query

        Returns:
            list of matching Paper objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM papers 
                WHERE title LIKE ? OR abstract LIKE ?
                ORDER BY citation_count DESC
                LIMIT 20
            """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()

            return [self._row_to_paper(row) for row in rows]

    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper.

        Args:
            paper_id: ID of the paper to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_conn() as conn:
            # Delete paper
            cursor = conn.execute("DELETE FROM papers WHERE paper_id = ?", (paper_id,))

            if cursor.rowcount > 0:
                # Delete associated PDF and text files
                self._delete_paper_files(paper_id)
                logger.info("Paper deleted", paper_id=paper_id)
                return True
            return False

    def _delete_paper_files(self, paper_id: str) -> None:
        """Delete PDF and markdown files associated with a paper.

        Args:
            paper_id: ID of the paper whose files should be deleted
        """
        pdf_dir = self.config.base_dir / "pdfs"
        pdf_path = pdf_dir / f"{paper_id}.pdf"
        md_path = pdf_dir / f"{paper_id}.md"
        txt_path = pdf_dir / f"{paper_id}.txt"  # Legacy support

        # Delete PDF file if it exists
        if pdf_path.exists():
            try:
                pdf_path.unlink()
                logger.info("PDF deleted", paper_id=paper_id, path=str(pdf_path))
            except Exception as e:
                logger.error(
                    "Failed to delete PDF",
                    paper_id=paper_id,
                    path=str(pdf_path),
                    error=str(e),
                )

        # Delete markdown file if it exists
        if md_path.exists():
            try:
                md_path.unlink()
                logger.info(
                    "Markdown file deleted", paper_id=paper_id, path=str(md_path),
                )
            except Exception as e:
                logger.error(
                    "Failed to delete markdown file",
                    paper_id=paper_id,
                    path=str(md_path),
                    error=str(e),
                )


    # Full text operations

    def get_full_text(self, paper_id: str) -> str | None:
        """Read full text from cached .md file.

        Args:
            paper_id: ID of the paper

        Returns:
            Full text content or None if not found
        """
        md_path = self.config.base_dir / "pdfs" / f"{paper_id}.md"
        if md_path.exists():
            try:
                return md_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(
                    "Failed to read markdown file", paper_id=paper_id, error=str(e),
                )
                return None
        return None

    # User Notes operations

    def add_note(self, paper_id: str, content: str) -> bool:
        """Add or update user notes for a paper.

        Args:
            paper_id: ID of the paper
            content: Markdown content of the note

        Returns:
            True if successful
        """
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE papers SET notes = ? WHERE paper_id = ?",
                (content, paper_id),
            )
            logger.info(
                "User notes saved",
                paper_id=paper_id,
            )
            return True

    def get_note(self, paper_id: str) -> str | None:
        """Get user notes for a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            Note content as markdown string or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT notes FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            if row and row["notes"]:
                return str(row["notes"])
            return None

    def delete_note(self, paper_id: str) -> bool:
        """Delete user notes for a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            True if deleted, False if note didn't exist
        """
        with self._get_conn() as conn:
            # First check if notes exist
            row = conn.execute(
                "SELECT notes FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            if not row or row["notes"] is None:
                return False

            # Delete the notes
            conn.execute(
                "UPDATE papers SET notes = NULL WHERE paper_id = ?",
                (paper_id,),
            )
            return True

    def list_papers_with_notes(self) -> list[tuple[Paper, str, datetime]]:
        """List all papers that have user notes.

        Returns:
            List of tuples containing (paper, note_preview, updated_at)
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM papers
                WHERE notes IS NOT NULL
                ORDER BY added_at DESC
            """).fetchall()

            results = []
            for row in rows:
                paper = self._row_to_paper(row)
                note_preview = (
                    row["notes"][:100] + "..."
                    if len(row["notes"]) > 100
                    else row["notes"]
                )
                # Use added_at as the update timestamp for notes
                updated_at = datetime.fromisoformat(row["added_at"])
                results.append((paper, note_preview, updated_at))
            return results

    # Paper-tag associations

    def add_tags_to_paper(self, paper_id: str, tag_names: list[str]) -> None:
        """Add tags to a paper (appends to existing tags).

        Args:
            paper_id: ID of the paper
            tag_names: List of tag names to add
        """
        if not tag_names:
            return

        with self._get_conn() as conn:
            # Get existing tags
            row = conn.execute(
                "SELECT tags FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            existing_tags = []
            if row and row["tags"]:
                existing_tags = [tag.strip().lower() for tag in row["tags"].split(",")]

            # Add new tags (avoiding duplicates)
            new_tags = [tag.lower().strip() for tag in tag_names]
            all_tags = list(set(existing_tags + new_tags))

            # Update the tags column
            tags_csv = ", ".join(sorted(all_tags))
            conn.execute(
                "UPDATE papers SET tags = ? WHERE paper_id = ?",
                (tags_csv, paper_id),
            )

        logger.info("Tags added to paper", paper_id=paper_id, tags=tag_names)

    def remove_tag_from_paper(self, paper_id: str, tag_name: str) -> bool:
        """Remove a tag from a paper.

        Args:
            paper_id: ID of the paper
            tag_name: Name of the tag to remove

        Returns:
            True if removed, False if not found
        """
        tag_name = tag_name.lower().strip()

        with self._get_conn() as conn:
            # Get existing tags
            row = conn.execute(
                "SELECT tags FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            if not row or not row["tags"]:
                return False

            existing_tags = [tag.strip().lower() for tag in row["tags"].split(",")]

            if tag_name not in existing_tags:
                return False

            # Remove the tag
            existing_tags.remove(tag_name)

            # Update the tags column
            tags_csv = ", ".join(sorted(existing_tags)) if existing_tags else None

            cursor = conn.execute(
                "UPDATE papers SET tags = ? WHERE paper_id = ?",
                (tags_csv, paper_id),
            )
            return cursor.rowcount > 0

    def get_paper_tags(self, paper_id: str) -> list[str]:
        """Get all tag names for a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            List of tag names
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT tags FROM papers WHERE paper_id = ?",
                (paper_id,),
            ).fetchone()

            if row and row["tags"]:
                return [tag.strip() for tag in row["tags"].split(",")]
            return []

    def set_paper_tags(self, paper_id: str, tag_names: list[str]) -> None:
        """Replace all tags for a paper.

        Args:
            paper_id: ID of the paper
            tag_names: New list of tag names
        """
        with self._get_conn() as conn:
            if tag_names:
                # Normalize and sort tags
                normalized_tags = sorted(
                    {tag.lower().strip() for tag in tag_names if tag.strip()},
                )
                tags_csv = ", ".join(normalized_tags)
            else:
                tags_csv = None

            conn.execute(
                "UPDATE papers SET tags = ? WHERE paper_id = ?",
                (tags_csv, paper_id),
            )

    def list_all_tags(self) -> list[tuple[str, int]]:
        """List all unique tags with their paper counts.

        Returns:
            List of (tag_name, count) tuples sorted by tag name
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT tags FROM papers WHERE tags IS NOT NULL AND tags != ''",
            ).fetchall()

            # Count occurrences of each tag
            tag_counts: dict[str, int] = {}
            for row in rows:
                if row["tags"]:
                    for tag in row["tags"].split(","):
                        tag = tag.strip()
                        if tag:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Return sorted list of (tag, count) tuples
            return sorted(tag_counts.items())

    # Search operations

    def search_papers_by_tags(
        self, tag_names: list[str], match_all: bool = False,
    ) -> list[Paper]:
        """Search papers by tags (AND/OR logic).

        Args:
            tag_names: List of tag names to search for
            match_all: If True, papers must have ALL tags (AND).
                      If False, papers can have ANY tag (OR).

        Returns:
            List of Paper objects matching the criteria
        """
        if not tag_names:
            return []

        # Normalize tag names
        tag_names = [name.lower().strip() for name in tag_names]

        with self._get_conn() as conn:
            # Get all papers with tags
            query = "SELECT * FROM papers WHERE tags IS NOT NULL AND tags != '' ORDER BY added_at DESC"
            rows = conn.execute(query).fetchall()

            papers = []
            for row in rows:
                # Parse tags from CSV
                if row["tags"]:
                    paper_tags = [tag.strip().lower() for tag in row["tags"].split(",")]
                else:
                    continue

                # Check if paper matches tag criteria
                if match_all:
                    # Paper must have ALL specified tags
                    if all(tag in paper_tags for tag in tag_names):
                        paper = Paper.from_dict(dict(row))
                        paper.tags = [tag.strip() for tag in row["tags"].split(",")]
                        papers.append(paper)
                else:
                    # Paper can have ANY of the specified tags
                    if any(tag in paper_tags for tag in tag_names):
                        paper = Paper.from_dict(dict(row))
                        paper.tags = [tag.strip() for tag in row["tags"].split(",")]
                        papers.append(paper)

            return papers

    def get_papers_for_tag(self, tag_name: str) -> list[Paper]:
        """Get all papers with a specific tag.

        Args:
            tag_name: Name of the tag

        Returns:
            List of Paper objects with the tag
        """
        return self.search_papers_by_tags([tag_name], match_all=False)
