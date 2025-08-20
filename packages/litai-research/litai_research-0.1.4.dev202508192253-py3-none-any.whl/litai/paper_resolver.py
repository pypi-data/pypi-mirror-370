"""Paper reference resolution using LLM."""

from typing import TYPE_CHECKING

from litai.utils.logger import get_logger

if TYPE_CHECKING:
    from litai.database import Database
    from litai.llm import LLMClient

logger = get_logger(__name__)


async def resolve_paper_references(
    text: str, db: "Database", llm_client: "LLMClient",
) -> tuple[str, str | None]:
    """Use LLM to resolve paper references to explicit IDs.

    Args:
        text: User query that may contain paper references
        db: Database instance to get paper collection
        llm_client: LLM client for resolution

    Returns:
        Tuple of (resolved_query, paper_id_if_found)
    """
    await logger.ainfo("resolve_paper_references_start", query=text)

    papers = db.list_papers(limit=50)  # Get user's paper collection
    await logger.ainfo("papers_fetched", count=len(papers) if papers else 0)

    if not papers:
        await logger.ainfo("no_papers_to_resolve")
        return text, None  # No papers to resolve against

    # First check if it's a paper number (like the notes command does)
    try:
        paper_num = int(text.strip())
        if paper_num >= 1 and paper_num <= len(papers):
            paper = papers[paper_num - 1]
            # Don't replace the query, augment it with paper info
            resolved_query = f"{text} [referring to '{paper.title}' (paper_id: {paper.paper_id})]"
            await logger.ainfo(
                "paper_resolved_by_number",
                paper_num=paper_num,
                paper_id=paper.paper_id,
                title=paper.title,
            )
            return resolved_query, paper.paper_id
        await logger.awarning(
            "invalid_paper_number", paper_num=paper_num, max_papers=len(papers),
        )
        return text, None
    except ValueError:
        # Not a number, continue with LLM resolution
        pass

    # Build context for LLM
    paper_context = "\n".join(
        [
            f"- {p.title} (ID: {p.paper_id}, Authors: {', '.join(p.authors[:2])}, Year: {p.year})"
            for p in papers
        ],
    )

    prompt = f"""You have access to these papers:
{paper_context}

User query: "{text}"

If the query references a specific paper (like "attention paper", "the BERT study", "paper by Vaswani"), return ONLY the paper ID from the list above.

If no papers are referenced or multiple papers are referenced, return "NONE".

Return ONLY the paper ID or the word NONE. Do not include any other text or formatting.
Response:"""

    await logger.ainfo("sending_prompt_to_llm", prompt_length=len(prompt))

    try:
        response = await llm_client.complete(
            prompt,
            model_size="small",
            operation_type="paper_resolution",
        )
        # Extract content from response dict
        paper_id = response.get("content", "").strip()
        await logger.ainfo("llm_response", response=paper_id)

        if paper_id == "NONE":
            await logger.ainfo("llm_returned_none")
            return text, None

        # Verify the paper_id exists and get the paper
        paper = db.get_paper(paper_id)  # type: Paper | None
        if paper is not None:
            # Augment the query with paper information instead of replacing it
            resolved_query = f"{text} [referring to '{paper.title}' (paper_id: {paper_id})]"
            await logger.ainfo("paper_resolved", paper_id=paper_id, title=paper.title)
            return resolved_query, paper_id
        # Invalid paper_id returned, fallback
        await logger.awarning("invalid_paper_id_returned", paper_id=paper_id)
        return text, None

    except Exception as e:
        # If resolution fails, return original query
        await logger.aerror("resolve_paper_references_error", error=str(e))
        return text, None


def extract_context_type(text: str) -> str:
    """
    Extract the context type from natural language.

    Returns one of: full_text, notes, abstract
    """
    text_lower = text.lower()

    if "full" in text_lower or "full text" in text_lower or "entire" in text_lower:
        return "full_text"
    if "note" in text_lower or "key point" in text_lower or "summary" in text_lower:
        return "notes"
    if "abstract" in text_lower or "overview" in text_lower:
        return "abstract"
    # Default to full_text for maximum context
    return "full_text"
