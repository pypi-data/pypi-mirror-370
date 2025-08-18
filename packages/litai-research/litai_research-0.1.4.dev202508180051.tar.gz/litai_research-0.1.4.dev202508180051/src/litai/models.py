"""Data models for LitAI."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Paper:
    """Represents a research paper."""

    paper_id: str  # For semantic scholar, paper id is from there, whereas we make our own for import.
    title: str
    authors: list[str]
    year: int
    abstract: str
    arxiv_id: str | None = None
    doi: str | None = None
    citation_count: int = 0
    tldr: str | None = None
    venue: str | None = None
    open_access_pdf_url: str | None = None
    added_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)  # Tag names, populated from joins
    citation_key: str | None = None  # BibTeX citation key
    notes: str | None = None  # User notes, populated from database

    def generate_citation_key(self, existing_keys: set[str] | None = None) -> str:
        """Generate a BibTeX citation key using ACL Anthology format.

        Format: lastname-etal-YYYY-firstword (e.g., bhasin-etal-2024-multi)

        Args:
            existing_keys: Set of existing keys to avoid duplicates

        Returns:
            Generated citation key
        """
        import re
        import unicodedata

        existing_keys = existing_keys or set()

        # Normalize text by removing accents and special chars
        def normalize(text: str) -> str:
            # Remove accents
            text = unicodedata.normalize("NFKD", text)
            text = "".join(c for c in text if not unicodedata.combining(c))
            # Keep only alphanumeric and hyphens for names
            return re.sub(r"[^a-zA-Z0-9-]", "", text).lower()

        # Extract last name from author name
        def get_last_name(author: str) -> str:
            # Simple heuristic: last word is usually last name
            parts = author.strip().split()
            if parts:
                return normalize(parts[-1])
            return "unknown"

        # Get first author's last name
        first_author = get_last_name(self.authors[0]) if self.authors else "unknown"

        # Add "etal" if multiple authors
        author_part = f"{first_author}-etal" if len(self.authors) > 1 else first_author

        # Get year
        year_part = str(self.year) if self.year else "nd"

        # Get first significant word from title
        if self.title:
            title_words = self.title.lower().split()
            # Skip common words
            skip_words = {
                "the",
                "a",
                "an",
                "on",
                "in",
                "for",
                "and",
                "of",
                "with",
                "to",
                "is",
                "are",
                "as",
                "at",
                "by",
                "from",
            }
            first_word = None
            for word in title_words:
                clean_word = normalize(word)
                if clean_word and clean_word not in skip_words and len(clean_word) > 2:
                    first_word = clean_word
                    break
            if not first_word:
                first_word = "paper"
        else:
            first_word = "paper"

        # Build base key
        base_key = f"{author_part}-{year_part}-{first_word}"

        # Handle duplicates by appending numbers
        final_key = base_key
        counter = 2
        while final_key in existing_keys:
            final_key = f"{base_key}-{counter}"
            counter += 1

        return final_key

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": json.dumps(self.authors),
            "year": self.year,
            "abstract": self.abstract,
            "arxiv_id": self.arxiv_id,
            "doi": self.doi,
            "citation_count": self.citation_count,
            "tldr": self.tldr,
            "venue": self.venue,
            "open_access_pdf_url": self.open_access_pdf_url,
            "added_at": self.added_at.isoformat(),
            "citation_key": self.citation_key,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        """Create Paper from dictionary."""
        data = data.copy()
        if isinstance(data.get("authors"), str):
            data["authors"] = json.loads(data["authors"])
        if isinstance(data.get("added_at"), str):
            data["added_at"] = datetime.fromisoformat(data["added_at"])
        return cls(**data)


@dataclass
class LLMConfig:
    """LLM configuration settings."""

    provider: str = "auto"  # "openai", "anthropic", or "auto" for env detection
    model: str | None = None  # Specific model name, or None for default
    api_key_env: str | None = None  # Specific env var to use for API key

    @property
    def is_auto(self) -> bool:
        """Check if provider is set to auto-detect."""
        return self.provider == "auto"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_env": self.api_key_env,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        """Create LLMConfig from dictionary."""
        return cls(
            provider=data.get("provider", "auto"),
            model=data.get("model"),
            api_key_env=data.get("api_key_env"),
        )
