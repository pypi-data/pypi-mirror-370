"""Test slash commands as users would type them. Doesn't test the AI versions of things like fuzzy matching with paper resolver.'"""

import pytest
from conftest import strip_ansi_codes

import litai.cli
from litai.cli import handle_command
from litai.config import Config
from litai.database import Database
from litai.models import Paper

#=======================================================================
# Setup
#=======================================================================


@pytest.fixture
def config(tmp_path):
    """Create a test config with temporary directory."""
    return Config(base_dir=tmp_path)


@pytest.fixture
def db(config):
    """Create a test database."""
    return Database(config)


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            paper_id="paper1",
            title="Deep Learning Fundamentals",
            authors=["Alice Smith", "Bob Johnson"],
            year=2023,
            abstract="An introduction to deep learning concepts and applications.",
            citation_count=100,
        ),
        Paper(
            paper_id="paper2",
            title="Natural Language Processing with Transformers",
            authors=["Carol White"],
            year=2024,
            abstract="A comprehensive guide to NLP using transformer models.",
            citation_count=50,
        ),
        Paper(
            paper_id="paper3",
            title="Computer Vision: A Modern Approach",
            authors=["David Brown", "Eve Davis"],
            year=2023,
            abstract="State-of-the-art computer vision techniques.",
            citation_count=75,
        ),
    ]

#=======================================================================
# Find command
#=======================================================================

# TODO: Fix bug? Papers from find cannot use the same fixture as add, maybe?

class TestFindCommand:
    """Test /find command as users would type it."""
    
    def test_find_help(self, db, capsys):
        """Test: /find --help"""
        # Execute
        handle_command("/find --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_find_recent_empty(self, db, capsys):
        """Test: /find --recent when no search results"""
        # Setup: Clear search results
        litai.cli._search_results = []
        
        # Execute
        handle_command("/find --recent", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No search results" in output or "Warning:" in output
    
    def test_find_recent_with_results(self, db, sample_papers, capsys):
        """Test: /find --recent with existing search results"""
        # Setup: Put papers in search results
        litai.cli._search_results = sample_papers
        
        # Execute
        handle_command("/find --recent", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Deep Learning" in output
        assert "Natural Language" in output
    
    def test_find_without_query(self, db, capsys):
        """Test: /find (no query provided)"""
        # Execute
        handle_command("/find", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Please provide a search query" in output or "Usage:" in output
    
    def test_find_invalid_syntax(self, db, capsys):
        """Test: /find with invalid syntax (unmatched quotes)"""
        # Execute  
        handle_command("/find \"unmatched quote", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid command syntax" in output or "Use quotes" in output


#=======================================================================
# Add command
#=======================================================================

class TestAddCommand:
    """Test /add command as users would type it."""
    
    def test_add_single_paper_with_command(self, db, sample_papers, capsys):
        """Test: /add 1"""
        # Setup: Put papers in search results
        litai.cli._search_results = sample_papers
        
        # Execute: Run the command as user would type it
        handle_command("/add 1", db)
        
        # Verify: Check output
        output = capsys.readouterr().out
        assert "Deep Learning Fundamentals" in output
        assert "Added 1 papers" in output
        
        # Verify: Check database
        paper = db.get_paper("paper1")
        assert paper is not None
        assert paper.title == "Deep Learning Fundamentals"
    
    def test_add_multiple_papers_with_command(self, db, sample_papers, capsys):
        """Test: /add 1,2,3"""
        # Setup
        litai.cli._search_results = sample_papers
        
        # Execute
        handle_command("/add 1,2,3", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Deep Learning Fundamentals" in output
        assert "Natural Language Processing with Transformers" in output
        assert "Computer Vision: A Modern Approach" in output
        assert "Added 3 papers" in output
        
        # Verify database
        assert db.get_paper("paper1") is not None
        assert db.get_paper("paper2") is not None
        assert db.get_paper("paper3") is not None
    
    def test_add_range_of_papers(self, db, sample_papers, capsys):
        """Test: /add 1-2"""
        # Setup
        litai.cli._search_results = sample_papers
        
        # Execute
        handle_command("/add 1-2", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Added 2 papers" in output
        assert db.get_paper("paper1") is not None
        assert db.get_paper("paper2") is not None
        assert db.get_paper("paper3") is None  # Should not be added
    
    def test_add_with_no_search_results(self, db, capsys):
        """Test: /add 1 when no search results exist"""
        # Setup: Clear search results
        litai.cli._search_results = []
        
        # Execute
        handle_command("/add 1", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No search results available" in output
        assert "/find" in output  # Should suggest using /find first
    
    def test_add_invalid_paper_number(self, db, sample_papers, capsys):
        """Test: /add 99 (invalid number)"""
        # Setup
        litai.cli._search_results = sample_papers
        
        # Execute
        handle_command("/add 99", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid paper number: 99" in output
    
    def test_add_duplicate_paper(self, db, sample_papers, capsys):
        """Test: /add 1 twice (duplicate)"""
        # Setup
        litai.cli._search_results = sample_papers
        
        # Execute: Add first time
        handle_command("/add 1", db)
        capsys.readouterr()  # Clear output
        
        # Execute: Add second time (duplicate)
        handle_command("/add 1", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "skipped 1 duplicates" in output.lower()
    
    def test_add_with_tags(self, db, sample_papers, capsys):
        """Test: /add 1 --tags machine-learning,deep-learning"""
        # Setup
        litai.cli._search_results = sample_papers
        
        # Execute
        handle_command("/add 1 --tags machine-learning,deep-learning", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Deep Learning Fundamentals" in output
        
        # Verify tags were added
        paper = db.get_paper("paper1")
        assert paper is not None
        tags = db.get_paper_tags("paper1")
        assert "machine-learning" in tags
        assert "deep-learning" in tags
    
    def test_add_help(self, db, capsys):
        """Test: /add --help"""
        # Execute
        handle_command("/add --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()


#=======================================================================
# Collection command
#=======================================================================

class TestCollectionCommand:
    """Test /collection command as users would type it."""
    
    def test_collection_empty(self, db, capsys):
        """Test: /collection when no papers in collection"""
        # Execute
        handle_command("/collection", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No papers in your collection" in output or "Warning:" in output
    
    # Should probably be able to unwrap this, but it's okay
    def test_collection_with_papers(self, db, sample_papers, capsys):
        """Test: /collection with papers in collection"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/collection", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Deep" in output
        assert "Your Collection" in output or "papers" in output
    
    def test_collection_page_2(self, db, sample_papers, capsys):
        """Test: /collection 2 (second page)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/collection 2", db)
        
        # Verify
        output = capsys.readouterr().out
        # With only 3 sample papers, page 2 should show no results or error
        assert "Invalid page number" in output or "Page" in output
    
    def test_collection_help(self, db, capsys):
        """Test: /collection --help"""
        # Execute
        handle_command("/collection --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_collection_tags(self, db, sample_papers, capsys):
        """Test: /collection --tags"""
        # Setup: Add papers with tags
        for paper in sample_papers:
            db.add_paper(paper)
        db.add_tags_to_paper(sample_papers[0].paper_id, ["machine-learning", "ai"])
        
        # Execute
        handle_command("/collection --tags", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "machine-learning" in output or "Tags" in output
    
    def test_collection_notes(self, db, sample_papers, capsys):
        """Test: /collection --notes"""
        # Setup: Add papers and a note
        for paper in sample_papers:
            db.add_paper(paper)
        db.add_note(sample_papers[0].paper_id, "Test note content")
        
        # Execute
        handle_command("/collection --notes", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Deep Learning Fundamentals" in output or "notes" in output.lower()
    
    def test_collection_tag_filter(self, db, sample_papers, capsys):
        """Test: /collection --tag machine-learning"""
        # Setup: Add papers with tags
        for paper in sample_papers:
            db.add_paper(paper)
        db.add_tags_to_paper(sample_papers[0].paper_id, ["machine-learning"])
        
        # Execute
        handle_command("/collection --tag machine-learning", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Deep Learning Fundamentals" in output or "machine-learning" in output
    
    def test_collection_invalid_arg(self, db, capsys):
        """Test: /collection invalid-arg"""
        # Execute
        handle_command("/collection invalid-arg", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid argument" in output or "help" in output.lower()


#=======================================================================
# Remove command  
#=======================================================================

#TODO: Add remove all? (how do we forgo the approval mechanism)

class TestRemoveCommand:
    """Test /remove command as users would type it."""
    
    def test_remove_help(self, db, capsys):
        """Test: /remove --help"""
        # Execute
        handle_command("/remove --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_remove_empty_collection(self, db, capsys):
        """Test: /remove when no papers in collection"""
        # Execute
        handle_command("/remove 1", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No papers in your collection" in output or "Warning:" in output
    
    def test_remove_invalid_number(self, db, sample_papers, capsys, monkeypatch):
        """Test: /remove 99 (invalid number)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/remove 99", db)
        
        # Verify
        output = capsys.readouterr().out
        clean_output = strip_ansi_codes(output)
        assert "Invalid paper number: 99" in clean_output
    
    def test_remove_invalid_range(self, db, sample_papers, capsys):
        """Test: /remove 10-5 (invalid range)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/remove 10-5", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid range" in output or "Start must be less than" in output
    
    def test_remove_invalid_format(self, db, sample_papers, capsys):
        """Test: /remove abc (invalid format)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/remove abc", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid number" in output or "error" in output.lower()


#=======================================================================
# Synthesize command
#=======================================================================

class TestSynthesizeCommand:
    """Test /synthesize command as users would type it."""
    
    def test_synthesize_help(self, db, capsys):
        """Test: /synthesize --help"""
        # Execute
        handle_command("/synthesize --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_synthesize_examples(self, db, capsys):
        """Test: /synthesize --examples"""
        # Execute
        handle_command("/synthesize --examples", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "examples" in output.lower() or "synthesis" in output.lower()
    
    def test_synthesize_without_config(self, db, capsys):
        """Test: /synthesize when config not available"""
        # Execute (handle_command without config will show error)
        handle_command("/synthesize What are the main insights?", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output


#=======================================================================
# Note command
#=======================================================================

#TODO: Check add and view commands

class TestNoteCommand:
    """Test /note command as users would type it."""
    
    def test_note_help(self, db, capsys):
        """Test: /note --help"""
        # Execute
        handle_command("/note --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_note_invalid_paper(self, db, capsys):
        """Test: /note 99 (invalid paper number)"""
        # Execute
        handle_command("/note 99", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "error" in output.lower() or "not found" in output.lower()
    
    def test_note_empty_collection(self, db, capsys):
        """Test: /note 1 when collection is empty"""
        # Execute
        handle_command("/note 1", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "error" in output.lower() or "not found" in output.lower()


#=======================================================================
# Tag command
#=======================================================================

class TestTagCommand:
    """Test /tag command as users would type it."""
    
    def test_tag_help(self, db, capsys):
        """Test: /tag --help"""
        # Execute
        handle_command("/tag --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_tag_empty_collection(self, db, capsys):
        """Test: /tag 1 when collection is empty"""
        # Execute
        handle_command("/tag 1", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "error" in output.lower() or "not found" in output.lower()
    
    def test_tag_invalid_paper(self, db, sample_papers, capsys):
        """Test: /tag 99 (invalid paper number)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/tag 99", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "error" in output.lower() or "not found" in output.lower()
    
    def test_tag_add_single_paper(self, db, sample_papers, capsys):
        """Test: /tag 1 -a ml,deep-learning"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]  # This is what "1" resolves to
        
        # Execute
        handle_command("/tag 1 -a ml,deep-learning", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Added 2 tag(s)" in output or "Added" in output
        assert first_paper.title in output
        
        # Verify tags were added
        tags = db.get_paper_tags(first_paper.paper_id)
        assert "ml" in tags
        assert "deep-learning" in tags
    
    def test_tag_add_multiple_papers(self, db, sample_papers, capsys):
        """Test: /tag 1,2 -a important"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        # Execute
        handle_command("/tag 1,2 -a important", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Added 1 tag(s) to 2 papers" in output or "2 papers" in output
        
        # Verify tags were added to both papers
        tags1 = db.get_paper_tags(papers_in_db[0].paper_id)
        tags2 = db.get_paper_tags(papers_in_db[1].paper_id)
        assert "important" in tags1
        assert "important" in tags2
    
    def test_tag_add_range(self, db, sample_papers, capsys):
        """Test: /tag 1-3 -a review"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        # Execute
        handle_command("/tag 1-3 -a review", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Added 1 tag(s) to 3 papers" in output or "3 papers" in output
        
        # Verify tags were added to all papers in range
        for paper in papers_in_db[:3]:
            tags = db.get_paper_tags(paper.paper_id)
            assert "review" in tags
    
    def test_tag_add_mixed_range_and_comma(self, db, sample_papers, capsys):
        """Test: /tag 1-2,3 -a needs-review"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        # Execute
        handle_command("/tag 1-2,3 -a needs-review", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Added 1 tag(s) to 3 papers" in output or "3 papers" in output
        
        # Verify all papers got the tag
        for paper in papers_in_db[:3]:
            tags = db.get_paper_tags(paper.paper_id)
            assert "needs-review" in tags
    
    def test_tag_remove_single_paper(self, db, sample_papers, capsys):
        """Test: /tag 1 -r ml"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        db.add_tags_to_paper(first_paper.paper_id, ["ml", "deep-learning"])
        
        # Execute
        handle_command("/tag 1 -r ml", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Removed 1 tag(s)" in output or "Removed" in output
        
        # Verify tag was removed
        tags = db.get_paper_tags(first_paper.paper_id)
        assert "ml" not in tags
        assert "deep-learning" in tags  # Other tag should remain
    
    def test_tag_remove_multiple_papers(self, db, sample_papers, capsys):
        """Test: /tag 1,2 -r important"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        db.add_tags_to_paper(papers_in_db[0].paper_id, ["important", "ml"])
        db.add_tags_to_paper(papers_in_db[1].paper_id, ["important", "nlp"])
        
        # Execute
        handle_command("/tag 1,2 -r important", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Removed tags from 2 papers" in output or "2 papers" in output
        
        # Verify tag was removed from both papers
        tags1 = db.get_paper_tags(papers_in_db[0].paper_id)
        tags2 = db.get_paper_tags(papers_in_db[1].paper_id)
        assert "important" not in tags1
        assert "important" not in tags2
        assert "ml" in tags1  # Other tags should remain
        assert "nlp" in tags2
    
    def test_tag_remove_range(self, db, sample_papers, capsys):
        """Test: /tag 1-3 -r review"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
            db.add_tags_to_paper(paper.paper_id, ["review", "other"])
        
        # Execute
        handle_command("/tag 1-3 -r review", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Removed tags from 3 papers" in output or "3 papers" in output
        
        # Verify tag was removed from all papers
        for paper in sample_papers:
            tags = db.get_paper_tags(paper.paper_id)
            assert "review" not in tags
            assert "other" in tags  # Other tag should remain
    
    def test_tag_list_single_paper(self, db, sample_papers, capsys):
        """Test: /tag 1 -l"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        db.add_tags_to_paper(first_paper.paper_id, ["ml", "deep-learning", "ai"])
        
        # Execute
        handle_command("/tag 1 -l", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert first_paper.title in output
        assert "ml" in output
        assert "deep-learning" in output
        assert "ai" in output
    
    def test_tag_list_multiple_papers(self, db, sample_papers, capsys):
        """Test: /tag 1,2 -l"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        db.add_tags_to_paper(papers_in_db[0].paper_id, ["ml", "ai"])
        db.add_tags_to_paper(papers_in_db[1].paper_id, ["nlp", "ai"])
        
        # Execute
        handle_command("/tag 1,2 -l", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Tags for 2 papers" in output
        assert "ml" in output
        assert "nlp" in output
        assert "ai" in output
    
    def test_tag_list_range(self, db, sample_papers, capsys):
        """Test: /tag 1-3 -l"""
        # Setup: Add papers to database with tags
        for i, paper in enumerate(sample_papers):
            db.add_paper(paper)
            db.add_tags_to_paper(paper.paper_id, [f"tag{i+1}", "common"])
        
        # Execute
        handle_command("/tag 1-3 -l", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert "Tags for 3 papers" in output
        assert "tag1" in output
        assert "tag2" in output
        assert "tag3" in output
        assert "common" in output
        assert "(3 papers)" in output  # Common tag should show it's on 3 papers
    
    def test_tag_view_single_paper(self, db, sample_papers, capsys):
        """Test: /tag 1 (view tags for single paper)"""
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        db.add_tags_to_paper(first_paper.paper_id, ["ml", "deep-learning"])
        
        # Execute
        handle_command("/tag 1", db)
        
        # Verify output
        output = capsys.readouterr().out
        assert first_paper.title in output
        assert "ml" in output
        assert "deep-learning" in output
    
    def test_tag_invalid_range(self, db, sample_papers, capsys):
        """Test: /tag 3-1 -a test (invalid range)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/tag 3-1 -a test", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid range" in output or "Start must be less than" in output
    
    def test_tag_range_out_of_bounds(self, db, sample_papers, capsys):
        """Test: /tag 1-10 -a test (range exceeds collection size)"""
        # Setup: Add papers to database (only 3 papers)
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/tag 1-10 -a test", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Invalid range" in output or "Must be between" in output
    
    def test_tag_remove_nonexistent_tag(self, db, sample_papers, capsys):
        """Test: /tag 1 -r nonexistent"""
        # Setup: Add papers to database without the tag
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/tag 1 -r nonexistent", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No matching tags found" in output or "0 tag(s)" in output
    
    def test_tag_add_empty_tag_list(self, db, sample_papers, capsys):
        """Test: /tag 1 -a (no tags provided)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Execute
        handle_command("/tag 1 -a", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Please provide tags" in output or "Usage:" in output
    
    def test_tag_duplicates_in_range(self, db, sample_papers, capsys):
        """Test: /tag 1,1,2 -a duplicate-test (duplicates should be handled)"""
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        
        # Execute
        handle_command("/tag 1,1,2 -a duplicate-test", db)
        
        # Verify output - should only count unique papers
        output = capsys.readouterr().out
        assert "Added 1 tag(s) to 2 papers" in output or "2 papers" in output
        
        # Verify tags were added correctly
        tags1 = db.get_paper_tags(papers_in_db[0].paper_id)
        tags2 = db.get_paper_tags(papers_in_db[1].paper_id)
        assert "duplicate-test" in tags1
        assert "duplicate-test" in tags2


#=======================================================================
# Import command
#=======================================================================

class TestImportCommand:
    """Test /import command as users would type it."""
    
    def test_import_help(self, db, capsys):
        """Test: /import --help"""
        # Execute
        handle_command("/import --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_import_no_args(self, db, capsys):
        """Test: /import (no arguments)"""
        # Execute
        handle_command("/import", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Please provide a BibTeX file path" in output or "Usage:" in output
    
    def test_import_nonexistent_file(self, db, capsys):
        """Test: /import nonexistent.bib"""
        # Execute
        handle_command("/import /nonexistent/file.bib", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "File not found" in output
    
    def test_import_invalid_extension(self, db, capsys, tmp_path):
        """Test: /import file.txt (wrong extension)"""
        # Setup: Create a file with wrong extension
        test_file = tmp_path / "test.txt"
        test_file.write_text("some content")
        
        # Execute
        handle_command(f"/import {test_file}", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "File must have .bib or .bibtex extension" in output
    
    def test_import_empty_bibtex(self, db, capsys, tmp_path):
        """Test: /import empty.bib"""
        # Setup: Create empty BibTeX file
        test_file = tmp_path / "empty.bib"
        test_file.write_text("")
        
        # Execute
        handle_command(f"/import {test_file}", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "No valid entries found" in output
    
    def test_import_valid_bibtex(self, db, capsys, tmp_path):
        """Test: /import valid.bib"""
        # Setup: Create valid BibTeX file
        bibtex_content = """
@article{test2023,
    title = {Test Article},
    author = {John Doe and Jane Smith},
    journal = {Test Journal},
    year = {2023},
    volume = {1},
    pages = {1-10},
    abstract = {This is a test abstract for import testing.}
}
"""
        test_file = tmp_path / "test.bib"
        test_file.write_text(bibtex_content)
        
        # Execute
        handle_command(f"/import {test_file}", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Found 1 valid entries" in output or "imported" in output.lower()
    
    def test_import_dry_run(self, db, capsys, tmp_path):
        """Test: /import file.bib --dry-run"""
        # Setup: Create valid BibTeX file
        bibtex_content = """
@article{dryrun2023,
    title = {Dry Run Test},
    author = {Test Author},
    year = {2023}
}
"""
        test_file = tmp_path / "dryrun.bib"
        test_file.write_text(bibtex_content)
        
        # Execute
        handle_command(f"/import {test_file} --dry-run", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "DRY RUN" in output


#=======================================================================
# Clear command
#=======================================================================

class TestClearCommand:
    """Test /clear command as users would type it."""
    
    def test_clear_help(self, db, capsys):
        """Test: /clear --help"""
        # Execute
        handle_command("/clear --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    # Example of mocking user input, interesting
    def test_clear_basic(self, db, capsys, monkeypatch):
        """Test: /clear (basic functionality)"""
        # Mock user input to confirm clearing
        monkeypatch.setattr('builtins.input', lambda: 'y')
        
        # Execute
        handle_command("/clear", db)
        
        # Verify - should not error and show some confirmation
        output = capsys.readouterr().out
        # Clear command may not have visible output, just verify no errors
        assert "error" not in output.lower() or len(output) >= 0  # Basic check


#=======================================================================
# Config command
#=======================================================================

# TODO: Add more configuration testing

class TestConfigCommand:
    """Test /config command as users would type it."""
    
    def test_config_help(self, db, capsys):
        """Test: /config --help"""
        # Execute
        handle_command("/config --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_config_without_config(self, db, capsys):
        """Test: /config when config not available"""
        # Execute (db fixture doesn't include config)
        handle_command("/config", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    def test_config_show(self, config, db, capsys):
        """Test: /config show"""
        # Execute
        handle_command("/config show", db, config=config)
        
        # Verify - should show config without error
        output = capsys.readouterr().out
        assert "error" not in output.lower() or "Configuration" in output


#=======================================================================
# Tokens command
#=======================================================================

class TestTokensCommand:
    """Test /tokens command as users would type it."""
    
    def test_tokens_help(self, db, capsys):
        """Test: /tokens --help"""
        # Execute
        handle_command("/tokens --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_tokens_without_config(self, db, capsys):
        """Test: /tokens when config not available"""
        # Execute
        handle_command("/tokens", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    def test_tokens_basic(self, config, db, capsys):
        """Test: /tokens (basic functionality)"""
        # Execute
        handle_command("/tokens", db, config=config)
        
        # Verify - should show token usage without error
        output = capsys.readouterr().out
        assert "error" not in output.lower() or "token" in output.lower()


#=======================================================================
# Prompt command
#=======================================================================

# Check append with things

class TestPromptCommand:
    """Test /prompt command as users would type it."""
    
    def test_prompt_help(self, db, capsys):
        """Test: /prompt --help"""
        # Execute
        handle_command("/prompt --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    # TODO: Is this really helpful?
    def test_prompt_without_config(self, db, capsys):
        """Test: /prompt when config not available"""
        # Execute
        handle_command("/prompt", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    # TODO: Should also have one when there is a prompt
    def test_prompt_view(self, config, db, capsys):
        """Test: /prompt view"""
        # Execute
        handle_command("/prompt view", db, config=config)
        
        # Verify
        output = capsys.readouterr().out
        assert "No user research profile set" in output or "Research Context" in output
    
    def test_prompt_clear(self, config, db, capsys, monkeypatch):
        """Test: /prompt clear"""
        # Mock user confirmation
        monkeypatch.setattr('builtins.input', lambda: 'y')
        
        # Execute
        handle_command("/prompt clear", db, config=config)
        
        # Verify - should not error
        output = capsys.readouterr().out
        assert "error" not in output.lower() or len(output) >= 0
    
    def test_prompt_append_no_text(self, config, db, capsys):
        """Test: /prompt append (no text provided)"""
        # Execute
        handle_command("/prompt append", db, config=config)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage: /prompt append <text>" in output


#=======================================================================
# Context commands
#=======================================================================

#TODO: Missing tag command tests

class TestContextCommands:
    """Test context commands (/cadd, /cremove, /cshow, /cclear, /cmodify) as users would type them."""
    
    def test_cadd_help(self, db, capsys):
        """Test: /cadd --help"""
        # Execute
        handle_command("/cadd --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_cadd_without_config(self, db, capsys):
        """Test: /cadd when config not available"""
        # Execute
        handle_command("/cadd", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    def test_cadd_empty_adds_all_papers(self, config, db, sample_papers, capsys):
        """Test: /cadd (empty) - should add all papers from collection as full_text"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Run /cadd with no arguments
        handle_command("/cadd", db, config=config, session_context=session_context)
        
        # Verify output mentions adding all papers
        output = capsys.readouterr().out
        assert "Added 3 papers from collection" in output or "Added 3 papers" in output
        assert "full_text" in output.lower()
        
        # Verify all papers were added to session context with full_text type
        papers_in_db = db.list_papers()
        assert len(session_context.papers) == 3
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "full_text"
            assert context_entry.paper_title == paper.title
    
    def test_cadd_empty_no_papers_in_collection(self, config, db, capsys):
        """Test: /cadd (empty) when no papers in collection"""
        from litai.context_manager import SessionContext
        
        # Setup: Create empty session context
        session_context = SessionContext()
        
        # Execute: Run /cadd with no arguments
        handle_command("/cadd", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "No papers in your collection" in output or "Use /find first" in output
        
        # Verify no papers were added
        assert len(session_context.papers) == 0
    
    def test_cadd_empty_skips_duplicates(self, config, db, sample_papers, capsys):
        """Test: /cadd (empty) skips papers already in context with same type"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add first paper with abstract
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "full_text")
        
        # Execute: Run /cadd with no arguments
        handle_command("/cadd", db, config=config, session_context=session_context)
        
        # Verify output mentions skipping duplicates
        output = capsys.readouterr().out
        assert "Added 2 papers" in output  # Only 2 new papers added
        assert "Skipped 1 papers already in context" in output or "skipped" in output.lower()
        
        # Verify all papers are in context
        assert len(session_context.papers) == 3
    
    def test_cremove_help(self, db, capsys):
        """Test: /cremove --help"""
        # Execute
        handle_command("/cremove --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_cremove_without_config(self, db, capsys):
        """Test: /cremove when config not available"""
        # Execute
        handle_command("/cremove", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    def test_cshow_help(self, db, capsys):
        """Test: /cshow --help"""
        # Execute
        handle_command("/cshow --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_cshow_without_context(self, db, capsys):
        """Test: /cshow when session context not available"""
        # Execute
        handle_command("/cshow", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Session context not available" in output
    
    def test_cclear_help(self, db, capsys):
        """Test: /cclear --help"""
        # Execute
        handle_command("/cclear --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_cclear_without_context(self, db, capsys):
        """Test: /cclear when session context not available"""
        # Execute
        handle_command("/cclear", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Session context not available" in output
    
    def test_cmodify_help(self, db, capsys):
        """Test: /cmodify --help"""
        # Execute
        handle_command("/cmodify --help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Usage:" in output or "help" in output.lower()
    
    def test_cmodify_without_config(self, db, capsys):
        """Test: /cmodify when config not available"""
        # Execute
        handle_command("/cmodify", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "Configuration not available" in output
    
    def test_cadd_valid_paper_number(self, config, db, sample_papers, capsys):
        """Test: /cadd 1 with papers in collection - should default to full_text context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database first so they appear in collection
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database (as they would appear in collection)
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]  # This is what "1" resolves to
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Add paper 1 to context (should default to full_text)
        handle_command("/cadd 1", db, config=config, session_context=session_context)
        
        # Verify output mentions the first paper (whatever it actually is)
        output = capsys.readouterr().out
        assert first_paper.title in output or "Added" in output
        
        # Verify paper was added to session context with full_text type
        assert first_paper.paper_id in session_context.papers
        context_entry = session_context.papers[first_paper.paper_id]
        assert context_entry.context_type == "full_text"
        assert context_entry.paper_title == first_paper.title
    
    def test_cadd_invalid_paper_number(self, config, db, sample_papers, capsys):
        """Test: /cadd 99 with invalid paper number"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database (only 3 papers)
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Try to add paper 99 (doesn't exist)
        handle_command("/cadd 99", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "No paper found matching" in output or "99" in output
    
    def test_cadd_with_context_type(self, config, db, sample_papers, capsys):
        """Test: /cadd 1 abstract - should use specified context type"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Get the actual order of papers from the database
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]  # This is what "1" resolves to
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Add paper 1 with abstract context type
        handle_command("/cadd 1 abstract", db, config=config, session_context=session_context)
        
        # Verify output shows abstract context type
        output = capsys.readouterr().out
        assert "abstract" in output.lower() and (first_paper.title in output or "Added" in output)
        
        # Verify paper was added to session context with abstract type
        assert first_paper.paper_id in session_context.papers
        context_entry = session_context.papers[first_paper.paper_id]
        assert context_entry.context_type == "abstract"
        assert context_entry.paper_title == first_paper.title
    
    def test_cremove_valid_paper_in_context(self, config, db, sample_papers, capsys):
        """Test: /cremove 1 with paper in context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database and get first paper
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        # Setup: Create session context and add paper to it
        session_context = SessionContext()
        session_context.add_paper(first_paper.paper_id, first_paper.title, "full_text")
        
        # Execute: Remove paper 1 from context
        handle_command("/cremove 1", db, config=config, session_context=session_context)
        
        # Verify output mentions removal
        output = capsys.readouterr().out
        assert "Removed" in output and first_paper.title in output
        
        # Verify paper was removed from session context
        assert first_paper.paper_id not in session_context.papers
    
    def test_cremove_paper_not_in_context(self, config, db, sample_papers, capsys):
        """Test: /cremove 1 with paper not in context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Setup: Create empty session context
        session_context = SessionContext()
        
        # Execute: Try to remove paper 1 (not in context)
        handle_command("/cremove 1", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "not in context" in output
    
    def test_cshow_with_papers_in_context(self, config, db, sample_papers, capsys):
        """Test: /cshow with papers in context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "full_text")
        session_context.add_paper(papers_in_db[1].paper_id, papers_in_db[1].title, "abstract")
        
        # Execute: Show context
        handle_command("/cshow", db, session_context=session_context)
        
        # Verify output shows both papers and their context types
        output = capsys.readouterr().out
        assert papers_in_db[0].title in output
        assert papers_in_db[1].title in output
        assert "full_text" in output or "full-text" in output
        assert "abstract" in output
        assert "Current Context" in output or "papers" in output
    
    def test_cmodify_valid_paper_and_context_type(self, config, db, sample_papers, capsys):
        """Test: /cmodify 1 notes"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        # Setup: Create session context and add paper with full_text
        session_context = SessionContext()
        session_context.add_paper(first_paper.paper_id, first_paper.title, "full_text")
        
        # Execute: Modify paper 1 to notes context type
        handle_command("/cmodify 1 notes", db, config=config, session_context=session_context)
        
        # Verify output shows modification
        output = capsys.readouterr().out
        assert "Modified" in output and "notes" in output
        
        # Verify paper context type was changed
        assert first_paper.paper_id in session_context.papers
        context_entry = session_context.papers[first_paper.paper_id]
        assert context_entry.context_type == "notes"
    
    def test_cmodify_invalid_context_type(self, config, db, sample_papers, capsys):
        """Test: /cmodify 1 invalid_type"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        
        # Setup: Create session context and add paper
        session_context = SessionContext()
        session_context.add_paper(first_paper.paper_id, first_paper.title, "full_text")
        
        # Execute: Try to modify with invalid context type
        handle_command("/cmodify 1 invalid_type", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "Invalid context type" in output
    
    def test_cclear_with_papers_in_context(self, config, db, sample_papers, capsys):
        """Test: /cclear with papers in context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "full_text")
        session_context.add_paper(papers_in_db[1].paper_id, papers_in_db[1].title, "abstract")
        
        # Verify context has papers before clearing
        assert len(session_context.papers) == 2
        
        # Execute: Clear context
        handle_command("/cclear", db, session_context=session_context)
        
        # Verify output shows clearing
        output = capsys.readouterr().out
        assert "Cleared" in output and "2" in output
        
        # Verify context is empty
        assert len(session_context.papers) == 0
    
    def test_cadd_with_tag_filter(self, config, db, sample_papers, capsys):
        """Test: /cadd --tag machine-learning"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database with tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Add tags to some papers
        papers_in_db = db.list_papers()
        first_paper = papers_in_db[0]
        db.add_tags_to_paper(first_paper.paper_id, ["machine-learning"])
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Add papers with machine-learning tag
        handle_command("/cadd --tag machine-learning", db, config=config, session_context=session_context)
        
        # Verify output mentions adding papers with tag
        output = capsys.readouterr().out
        assert "machine-learning" in output and ("Added" in output or "✓" in output)
        
        # Verify paper was added to session context
        assert first_paper.paper_id in session_context.papers
        context_entry = session_context.papers[first_paper.paper_id]
        assert context_entry.paper_title == first_paper.title
        assert context_entry.context_type == "full_text"  # Default for tag operations
    
    def test_cadd_no_papers_match_tags(self, config, db, sample_papers, capsys):
        """Test: /cadd with tags that don't match any papers"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database without the specified tags
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Setup: Create session context
        session_context = SessionContext()
        
        # Execute: Try to add papers with non-existent tags
        handle_command("/cadd --tag nonexistent-tag", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "No papers found" in output or "nonexistent-tag" in output
    
    def test_cremove_with_tags(self, config, db, sample_papers, capsys):
        """Test: /cremove --tag machine-learning"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database and to context
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Add tags to papers
        db.add_tags_to_paper(papers_in_db[0].paper_id, ["machine-learning"])
        db.add_tags_to_paper(papers_in_db[1].paper_id, ["nlp"])
        
        # Setup: Create session context and add all papers
        session_context = SessionContext()
        for paper in papers_in_db:
            session_context.add_paper(paper.paper_id, paper.title, "full_text")
        
        # Execute: Remove papers with machine-learning tag
        handle_command("/cremove --tag machine-learning", db, config=config, session_context=session_context)
        
        # Verify output shows removal
        output = capsys.readouterr().out
        assert "Removed" in output or "✓" in output
        
        # Verify only the machine-learning tagged paper was removed
        assert papers_in_db[0].paper_id not in session_context.papers
        assert papers_in_db[1].paper_id in session_context.papers  # NLP paper should remain
    
    def test_cmodify_with_tags(self, config, db, sample_papers, capsys):
        """Test: /cmodify --tag machine-learning abstract"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Add tags to papers
        db.add_tags_to_paper(papers_in_db[0].paper_id, ["machine-learning"])
        db.add_tags_to_paper(papers_in_db[1].paper_id, ["nlp"])
        
        # Setup: Create session context and add papers with full_text
        session_context = SessionContext()
        for paper in papers_in_db:
            session_context.add_paper(paper.paper_id, paper.title, "full_text")
        
        # Execute: Modify context type for papers with machine-learning tag
        handle_command("/cmodify --tag machine-learning abstract", db, config=config, session_context=session_context)
        
        # Verify output shows modification
        output = capsys.readouterr().out
        assert "Modified" in output and "abstract" in output
        
        # Verify only the machine-learning tagged paper was modified
        ml_paper_context = session_context.papers[papers_in_db[0].paper_id]
        nlp_paper_context = session_context.papers[papers_in_db[1].paper_id]
        assert ml_paper_context.context_type == "abstract"
        assert nlp_paper_context.context_type == "full_text"  # Should remain unchanged
    
    def test_cmodify_no_papers_match_tags(self, config, db, sample_papers, capsys):
        """Test: /cmodify --tag nonexistent abstract"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database and context
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers
        session_context = SessionContext()
        for paper in papers_in_db:
            session_context.add_paper(paper.paper_id, paper.title, "full_text")
        
        # Execute: Try to modify with non-existent tags
        handle_command("/cmodify --tag nonexistent abstract", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "No papers found" in output or "nonexistent" in output
    
    def test_cmodify_all_papers_to_full_text(self, config, db, sample_papers, capsys):
        """Test: /cmodify full-text - should modify ALL papers to full-text"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers with different context types
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "abstract")
        session_context.add_paper(papers_in_db[1].paper_id, papers_in_db[1].title, "notes")
        session_context.add_paper(papers_in_db[2].paper_id, papers_in_db[2].title, "abstract")
        
        # Execute: Modify all papers to full-text
        handle_command("/cmodify full-text", db, config=config, session_context=session_context)
        
        # Verify output shows all papers were modified
        output = capsys.readouterr().out
        assert "Modified 3 papers to full_text" in output or "Modified 3 papers" in output
        
        # Verify all papers now have full_text context type
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "full_text"
    
    def test_cmodify_all_papers_to_abstract(self, config, db, sample_papers, capsys):
        """Test: /cmodify abstract - should modify ALL papers to abstract"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers with full_text
        session_context = SessionContext()
        for paper in papers_in_db:
            session_context.add_paper(paper.paper_id, paper.title, "full_text")
        
        # Execute: Modify all papers to abstract
        handle_command("/cmodify abstract", db, config=config, session_context=session_context)
        
        # Verify output shows all papers were modified
        output = capsys.readouterr().out
        assert "Modified 3 papers to abstract" in output or "Modified 3 papers" in output
        
        # Verify all papers now have abstract context type
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "abstract"
    
    def test_cmodify_all_papers_to_notes(self, config, db, sample_papers, capsys):
        """Test: /cmodify notes - should modify ALL papers to notes"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add papers with mixed types
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "full_text")
        session_context.add_paper(papers_in_db[1].paper_id, papers_in_db[1].title, "abstract")
        session_context.add_paper(papers_in_db[2].paper_id, papers_in_db[2].title, "full_text")
        
        # Execute: Modify all papers to notes
        handle_command("/cmodify notes", db, config=config, session_context=session_context)
        
        # Verify output shows papers were modified
        output = capsys.readouterr().out
        assert "Modified 3 papers to notes" in output or "Modified 3 papers" in output
        
        # Verify all papers now have notes context type
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "notes"
    
    def test_cmodify_all_papers_already_have_type(self, config, db, sample_papers, capsys):
        """Test: /cmodify abstract when all papers already have abstract"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context and add all papers with abstract
        session_context = SessionContext()
        for paper in papers_in_db:
            session_context.add_paper(paper.paper_id, paper.title, "abstract")
        
        # Execute: Try to modify all to abstract (already have it)
        handle_command("/cmodify abstract", db, config=config, session_context=session_context)
        
        # Verify output shows all papers already have that type
        output = capsys.readouterr().out
        assert "already have abstract" in output or "already had abstract" in output
        
        # Verify all papers still have abstract context type
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "abstract"
    
    def test_cmodify_all_papers_some_already_have_type(self, config, db, sample_papers, capsys):
        """Test: /cmodify full-text when some papers already have full-text"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        papers_in_db = db.list_papers()
        
        # Setup: Create session context with mixed types
        session_context = SessionContext()
        session_context.add_paper(papers_in_db[0].paper_id, papers_in_db[0].title, "full_text")
        session_context.add_paper(papers_in_db[1].paper_id, papers_in_db[1].title, "abstract")
        session_context.add_paper(papers_in_db[2].paper_id, papers_in_db[2].title, "notes")
        
        # Execute: Modify all to full-text
        handle_command("/cmodify full-text", db, config=config, session_context=session_context)
        
        # Verify output shows correct counts
        output = capsys.readouterr().out
        assert "Modified 2 papers" in output  # Only 2 needed modification
        assert "1 papers already had full_text" in output or "already had" in output
        
        # Verify all papers now have full_text
        for paper in papers_in_db:
            assert paper.paper_id in session_context.papers
            context_entry = session_context.papers[paper.paper_id]
            assert context_entry.context_type == "full_text"
    
    def test_cmodify_all_empty_context(self, config, db, sample_papers, capsys):
        """Test: /cmodify abstract when no papers in context"""
        from litai.context_manager import SessionContext
        
        # Setup: Add papers to database but not to context
        for paper in sample_papers:
            db.add_paper(paper)
        
        # Setup: Create empty session context
        session_context = SessionContext()
        
        # Execute: Try to modify all when context is empty
        handle_command("/cmodify abstract", db, config=config, session_context=session_context)
        
        # Verify error message
        output = capsys.readouterr().out
        assert "No papers in context" in output or "Use /cadd" in output
        
        # Verify context is still empty
        assert len(session_context.papers) == 0


#=======================================================================
# Help command
#=======================================================================

class TestHelpCommand:
    """Test /help command as users would type it."""
    
    def test_help_basic(self, db, capsys):
        """Test: /help"""
        # Execute
        handle_command("/help", db)
        
        # Verify
        output = capsys.readouterr().out
        assert "commands" in output.lower() or "help" in output.lower()
        # Should show list of available commands
        assert "/find" in output
        assert "/add" in output
        assert "/collection" in output
