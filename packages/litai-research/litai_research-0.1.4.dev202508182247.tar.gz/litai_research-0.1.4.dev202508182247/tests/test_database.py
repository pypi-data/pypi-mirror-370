"""Tests for database operations."""

import shutil
import tempfile
from pathlib import Path

import pytest

from litai.config import Config
from litai.database import Database
from litai.models import Paper


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test config with temporary directory."""
    return Config(base_dir=temp_dir)


@pytest.fixture
def db(config):
    """Create a test database."""
    return Database(config)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    return Paper(
        paper_id="test123",
        title="Test Paper: A Study of Testing",
        authors=["John Doe", "Jane Smith"],
        year=2024,
        abstract="This is a test abstract about testing things.",
        arxiv_id="2401.12345",
        doi="10.1234/test.2024",
        citation_count=42,
        tldr="Testing is important",
        venue="Test Conference 2024",
        open_access_pdf_url="https://arxiv.org/pdf/2401.12345.pdf",
    )


class TestDatabase:
    """Test database operations."""

    def test_init_creates_tables(self, db, config):
        """Test that database initialization creates required tables."""
        # Check that database file exists
        assert config.db_path.exists()

        # Check tables exist
        with db._get_conn() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
            table_names = [row[0] for row in tables]

            assert "papers" in table_names

    def test_add_paper(self, db, sample_paper):
        """Test adding a paper to the database."""
        # Add paper
        assert db.add_paper(sample_paper) is True

        # Try to add same paper again
        assert db.add_paper(sample_paper) is False

    def test_get_paper(self, db, sample_paper):
        """Test retrieving a paper by ID."""
        # Add paper
        db.add_paper(sample_paper)

        # Retrieve paper
        retrieved = db.get_paper(sample_paper.paper_id)
        assert retrieved is not None
        assert retrieved.title == sample_paper.title
        assert retrieved.authors == sample_paper.authors
        assert retrieved.year == sample_paper.year

        # Try to retrieve non-existent paper
        assert db.get_paper("nonexistent") is None

    def test_list_papers(self, db):
        """Test listing papers."""
        # Add multiple papers
        for i in range(5):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2020 + i,
                abstract=f"Abstract {i}",
            )
            db.add_paper(paper)

        # List all papers
        papers = db.list_papers()
        assert len(papers) == 5

        # Test pagination
        papers = db.list_papers(limit=2)
        assert len(papers) == 2

        papers = db.list_papers(limit=2, offset=2)
        assert len(papers) == 2

    def test_count_papers(self, db):
        """Test counting papers."""
        assert db.count_papers() == 0

        # Add papers
        for i in range(3):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2024,
                abstract=f"Abstract {i}",
            )
            db.add_paper(paper)

        assert db.count_papers() == 3

    def test_search_papers(self, db):
        """Test searching papers."""
        # Add papers with different content
        papers = [
            Paper(
                paper_id="ml1",
                title="Machine Learning Fundamentals",
                authors=["ML Author"],
                year=2024,
                abstract="This paper covers machine learning basics.",
            ),
            Paper(
                paper_id="dl1",
                title="Deep Learning Advanced Topics",
                authors=["DL Author"],
                year=2024,
                abstract="Advanced deep learning techniques.",
            ),
            Paper(
                paper_id="nlp1",
                title="Natural Language Processing",
                authors=["NLP Author"],
                year=2024,
                abstract="NLP with machine learning approaches.",
            ),
        ]

        for paper in papers:
            db.add_paper(paper)

        # Search by title
        results = db.search_papers("machine learning")
        assert len(results) == 2  # Found in ML paper title and NLP abstract
        paper_ids = [r.paper_id for r in results]
        assert "ml1" in paper_ids
        assert "nlp1" in paper_ids

        # Search by abstract
        results = db.search_papers("learning")
        assert len(results) == 3  # All papers mention learning

    def test_delete_paper(self, db, sample_paper):
        """Test deleting a paper."""
        # Add paper
        db.add_paper(sample_paper)
        assert db.get_paper(sample_paper.paper_id) is not None

        # Delete paper
        assert db.delete_paper(sample_paper.paper_id) is True
        assert db.get_paper(sample_paper.paper_id) is None

        # Try to delete non-existent paper
        assert db.delete_paper("nonexistent") is False

    def test_add_note(self, db, sample_paper):
        """Test adding user notes to a paper."""
        # Add paper first
        db.add_paper(sample_paper)

        # Add note
        note_content = "This paper has interesting insights about testing methodology."
        assert db.add_note(sample_paper.paper_id, note_content) is True

        # Verify note was saved
        saved_note = db.get_note(sample_paper.paper_id)
        assert saved_note == note_content

    def test_get_note(self, db, sample_paper):
        """Test retrieving user notes."""
        # Add paper
        db.add_paper(sample_paper)

        # No note initially
        assert db.get_note(sample_paper.paper_id) is None

        # Add note
        note_content = "## Key Insights\n\nTesting is crucial for software quality."
        db.add_note(sample_paper.paper_id, note_content)

        # Retrieve note
        retrieved_note = db.get_note(sample_paper.paper_id)
        assert retrieved_note == note_content

    def test_update_note(self, db, sample_paper):
        """Test updating existing user notes."""
        # Add paper and initial note
        db.add_paper(sample_paper)
        initial_note = "Initial thoughts"
        db.add_note(sample_paper.paper_id, initial_note)

        # Update note
        updated_note = "Initial thoughts\n\n## Additional Ideas\n\nMore insights here."
        assert db.add_note(sample_paper.paper_id, updated_note) is True

        # Verify update
        retrieved_note = db.get_note(sample_paper.paper_id)
        assert retrieved_note == updated_note

    def test_delete_note(self, db, sample_paper):
        """Test deleting user notes."""
        # Add paper and note
        db.add_paper(sample_paper)
        db.add_note(sample_paper.paper_id, "Some notes")

        # Verify note exists
        assert db.get_note(sample_paper.paper_id) is not None

        # Delete note
        assert db.delete_note(sample_paper.paper_id) is True

        # Verify note is deleted
        assert db.get_note(sample_paper.paper_id) is None

        # Try to delete non-existent note
        assert db.delete_note(sample_paper.paper_id) is False

    def test_list_papers_with_notes(self, db):
        """Test listing papers that have notes."""
        from datetime import datetime

        # Add multiple papers
        papers = []
        for i in range(4):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2024,
                abstract=f"Abstract {i}",
            )
            db.add_paper(paper)
            papers.append(paper)

        # Add notes to some papers
        db.add_note(papers[0].paper_id, "Short note")
        db.add_note(
            papers[2].paper_id,
            "This is a longer note that should be truncated in the preview because it exceeds the 100 character limit for previews",
        )

        # List papers with notes
        papers_with_notes = db.list_papers_with_notes()
        assert len(papers_with_notes) == 2

        # Check results
        paper_ids = [p[0].paper_id for p in papers_with_notes]
        assert "test0" in paper_ids
        assert "test2" in paper_ids

        # Check note preview truncation
        for paper, preview, updated_at in papers_with_notes:
            if paper.paper_id == "test0":
                assert preview == "Short note"
            elif paper.paper_id == "test2":
                assert preview.endswith("...")
                assert len(preview) == 103  # 100 chars + "..."

            # Check updated_at is a datetime
            assert isinstance(updated_at, datetime)

    def test_notes_stored_as_plain_text(self, db, sample_paper):
        """Test that notes are stored as plain text, not JSON."""
        # Add paper
        db.add_paper(sample_paper)

        # Add markdown note
        markdown_note = """# My Notes

## Key Points
- Testing is important
- This paper validates our approach

### Implementation Ideas
1. Use pytest for testing
2. Add CI/CD pipeline
"""
        db.add_note(sample_paper.paper_id, markdown_note)

        # Verify stored as plain text in papers.notes column
        with db._get_conn() as conn:
            row = conn.execute(
                "SELECT notes FROM papers WHERE paper_id = ?",
                (sample_paper.paper_id,),
            ).fetchone()

            # Content should be the markdown string
            assert row["notes"] == markdown_note

            # Verify it's not JSON by checking it doesn't start with { or [
            assert not row["notes"].strip().startswith("{")
            assert not row["notes"].strip().startswith("[")

    def test_delete_paper_with_notes(self, db, sample_paper):
        """Test that deleting a paper also deletes its notes."""
        # Add paper and note
        db.add_paper(sample_paper)
        db.add_note(sample_paper.paper_id, "Important notes about this paper")

        # Verify note exists
        assert db.get_note(sample_paper.paper_id) is not None

        # Delete paper
        db.delete_paper(sample_paper.paper_id)

        # Verify note is also deleted
        assert db.get_note(sample_paper.paper_id) is None


class TestTagOperations:
    """Test tag-related database operations."""

    # test_create_tag removed - tags are now stored as CSV, not as separate entities

    def test_add_tags_to_paper(self, db, sample_paper):
        """Test adding tags to a paper."""
        db.add_paper(sample_paper)

        # Add tags
        db.add_tags_to_paper(
            sample_paper.paper_id, ["nlp", "transformers", "attention"],
        )

        # Verify tags were added
        tags = db.get_paper_tags(sample_paper.paper_id)
        assert len(tags) == 3
        assert "nlp" in tags
        assert "transformers" in tags
        assert "attention" in tags

    def test_remove_tag_from_paper(self, db, sample_paper):
        """Test removing a tag from a paper."""
        db.add_paper(sample_paper)
        db.add_tags_to_paper(sample_paper.paper_id, ["nlp", "transformers"])

        # Remove one tag
        success = db.remove_tag_from_paper(sample_paper.paper_id, "nlp")
        assert success

        # Verify tag was removed
        tags = db.get_paper_tags(sample_paper.paper_id)
        assert len(tags) == 1
        assert "transformers" in tags
        assert "nlp" not in tags

    def test_search_papers_by_tags(self, db, sample_paper):
        """Test searching papers by tags."""
        # Add multiple papers with different tags
        db.add_paper(sample_paper)
        db.add_tags_to_paper(sample_paper.paper_id, ["nlp", "transformers"])

        paper2 = Paper(
            paper_id="test456",
            title="Another Test Paper",
            authors=["Bob Smith"],
            year=2023,
            abstract="Another abstract",
        )
        db.add_paper(paper2)
        db.add_tags_to_paper(paper2.paper_id, ["nlp", "rnn"])

        # Search for papers with "nlp" tag
        papers = db.search_papers_by_tags(["nlp"])
        assert len(papers) == 2

        # Search for papers with "transformers" tag
        papers = db.search_papers_by_tags(["transformers"])
        assert len(papers) == 1
        assert papers[0].paper_id == sample_paper.paper_id

    def test_list_all_tags(self, db, sample_paper):
        """Test listing all tags with paper counts."""
        # Add papers with tags
        db.add_paper(sample_paper)
        db.add_tags_to_paper(sample_paper.paper_id, ["nlp", "transformers"])

        paper2 = Paper(
            paper_id="test456",
            title="Another Test Paper",
            authors=["Bob Smith"],
            year=2023,
            abstract="Another abstract",
        )
        db.add_paper(paper2)
        db.add_tags_to_paper(paper2.paper_id, ["nlp"])

        # List all tags
        tags_with_counts = db.list_all_tags()
        assert len(tags_with_counts) == 2

        # Check counts (nlp should have 2, transformers should have 1)
        tag_dict = {tag_name: count for tag_name, count in tags_with_counts}
        assert tag_dict["nlp"] == 2
        assert tag_dict["transformers"] == 1

    def test_delete_paper_removes_tag_associations(self, db, sample_paper):
        """Test that deleting a paper removes its tag associations."""
        db.add_paper(sample_paper)
        db.add_tags_to_paper(sample_paper.paper_id, ["nlp", "transformers"])

        # Verify tags exist
        tags = db.get_paper_tags(sample_paper.paper_id)
        assert len(tags) == 2

        # Delete paper
        db.delete_paper(sample_paper.paper_id)

        # Verify tag associations are removed
        tags = db.get_paper_tags(sample_paper.paper_id)
        assert len(tags) == 0

    def test_list_papers_with_tag_filter(self, db, sample_paper):
        """Test listing papers with tag filter."""
        # Add papers with different tags
        db.add_paper(sample_paper)
        db.add_tags_to_paper(sample_paper.paper_id, ["nlp"])

        paper2 = Paper(
            paper_id="test456",
            title="Another Test Paper",
            authors=["Bob Smith"],
            year=2023,
            abstract="Another abstract",
        )
        db.add_paper(paper2)
        db.add_tags_to_paper(paper2.paper_id, ["cv"])

        # List papers with "nlp" tag
        papers = db.list_papers(tag="nlp")
        assert len(papers) == 1
        assert papers[0].paper_id == sample_paper.paper_id
        assert papers[0].tags == ["nlp"]  # Tags should be populated

        # List papers with "cv" tag
        papers = db.list_papers(tag="cv")
        assert len(papers) == 1
        assert papers[0].paper_id == paper2.paper_id
        assert papers[0].tags == ["cv"]
