"""BibTeX import functionality for LitAI."""

import hashlib
import re
from pathlib import Path
from typing import Any

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from ..models import Paper
from ..utils.logger import get_logger

logger = get_logger(__name__)


def extract_arxiv_id(text: str) -> str | None:
    """Extract arXiv ID from URL or text.

    Args:
        text: Text that might contain an arXiv ID

    Returns:
        ArXiv ID if found, None otherwise
    """
    if not text:
        return None

    # Match arxiv URLs and IDs
    patterns = [
        r"arxiv\.org/abs/(\d{4}\.\d{4,5}v?\d*)",
        r"arxiv\.org/pdf/(\d{4}\.\d{4,5}v?\d*)",
        r"(\d{4}\.\d{4,5}v?\d*)",  # Just the ID
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_doi(text: str) -> str | None:
    """Extract DOI from URL or text.

    Args:
        text: Text that might contain a DOI

    Returns:
        DOI if found, None otherwise
    """
    if not text:
        return None

    # DOI patterns
    patterns = [
        r"doi\.org/(10\.\d{4,9}/[-._;()/:\w]+)",
        r"doi:\s*(10\.\d{4,9}/[-._;()/:\w]+)",
        r"(10\.\d{4,9}/[-._;()/:\w]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def generate_paper_id(entry: dict[str, Any]) -> str:
    """Generate a unique paper ID from BibTeX entry.

    Priority order:
    1. ArXiv ID
    2. DOI
    3. Hash of citation key

    Args:
        entry: BibTeX entry dict

    Returns:
        Generated paper ID
    """
    # Try to extract arXiv ID
    url = entry.get("url", "")
    if arxiv_id := extract_arxiv_id(url):
        return f"arxiv:{arxiv_id}"

    # Try DOI from doi field or URL
    doi = entry.get("doi") or extract_doi(url)
    if doi:
        return f"doi:{doi}"

    # Fallback to hash of citation key
    citation_key = entry.get("ID", "unknown")
    hash_val = hashlib.md5(citation_key.encode()).hexdigest()[:12]
    return f"bib:{hash_val}"


def clean_latex(text: str) -> str:
    """Clean LaTeX formatting from text.

    Args:
        text: Text with potential LaTeX formatting

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove common LaTeX commands
    text = re.sub(r"\\textit{([^}]*)}", r"\1", text)
    text = re.sub(r"\\textbf{([^}]*)}", r"\1", text)
    text = re.sub(r"\\emph{([^}]*)}", r"\1", text)
    text = re.sub(r"\\cite{[^}]*}", "", text)
    text = re.sub(r"\\[a-zA-Z]+{([^}]*)}", r"\1", text)

    # Remove braces
    text = text.replace("{", "").replace("}", "")

    # Clean up whitespace
    return " ".join(text.split())


def parse_authors(author_str: str) -> list[str]:
    """Parse author string into list of names.

    Args:
        author_str: Author string from BibTeX

    Returns:
        List of author names
    """
    if not author_str:
        return []

    # Split by 'and'
    authors = author_str.split(" and ")

    # Clean up each author
    cleaned_authors = []
    for author in authors:
        author = author.strip()
        if not author:
            continue

        # Handle "Last, First" format
        if "," in author:
            parts = author.split(",", 1)
            author = f"{parts[1].strip()} {parts[0].strip()}"

        cleaned_authors.append(author)

    return cleaned_authors


def bibtex_to_paper(entry: dict[str, Any]) -> Paper | None:
    """Convert BibTeX entry to Paper object.

    Args:
        entry: BibTeX entry dict

    Returns:
        Paper object or None if required fields missing
    """
    # Check required fields
    if not all(key in entry for key in ["title", "author", "year"]):
        logger.warning("Missing required fields", entry_id=entry.get("ID", "unknown"))
        return None

    try:
        # Clean and extract fields
        paper_id = generate_paper_id(entry)
        title = clean_latex(entry["title"])
        authors = parse_authors(entry["author"])
        year = int(entry["year"])
        abstract = clean_latex(entry.get("abstract", ""))

        # Extract identifiers
        url = entry.get("url", "")
        arxiv_id = extract_arxiv_id(url)
        doi = entry.get("doi") or extract_doi(url)

        # Try to get venue from journal or booktitle
        venue = entry.get("journal") or entry.get("booktitle")
        if venue:
            venue = clean_latex(venue)

        # Generate arXiv PDF URL if we have arXiv ID
        open_access_pdf_url = None
        if arxiv_id:
            open_access_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        return Paper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            arxiv_id=arxiv_id,
            doi=doi,
            citation_count=0,  # Will be enriched later
            tldr=None,  # Will be generated later
            venue=venue,
            open_access_pdf_url=open_access_pdf_url,
            citation_key=entry.get("ID"),
        )

    except Exception as e:
        logger.error(
            "Error converting BibTeX entry",
            entry_id=entry.get("ID", "unknown"),
            error=str(e),
        )
        return None


def parse_bibtex_file(file_path: Path) -> list[Paper]:
    """Parse BibTeX file and return list of Paper objects.

    Args:
        file_path: Path to BibTeX file

    Returns:
        List of successfully parsed Paper objects
    """
    papers = []

    try:
        with open(file_path, encoding="utf-8") as bibfile:
            parser = BibTexParser()
            parser.customization = convert_to_unicode
            bib_database = bibtexparser.load(bibfile, parser=parser)

            logger.info(
                "Parsing BibTeX file",
                path=str(file_path),
                entry_count=len(bib_database.entries),
            )

            for entry in bib_database.entries:
                paper = bibtex_to_paper(entry)
                if paper:
                    papers.append(paper)
                    logger.debug(
                        "Parsed paper",
                        paper_id=paper.paper_id,
                        title=paper.title[:50] + "...",
                    )

            logger.info(
                "BibTeX parsing complete",
                parsed=len(papers),
                skipped=len(bib_database.entries) - len(papers),
            )

    except Exception as e:
        logger.error("Error parsing BibTeX file", path=str(file_path), error=str(e))
        raise

    return papers
