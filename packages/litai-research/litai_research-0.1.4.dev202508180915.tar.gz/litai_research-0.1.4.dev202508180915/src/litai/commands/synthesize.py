"""Synthesis command that uses current context."""

from typing import Any

from rich.console import Console

from litai.config import Config
from litai.context_manager import SessionContext
from litai.database import Database
from litai.llm import LLMClient
from litai.token_tracker import TokenTracker
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


async def _check_and_show_content_status(
    session_context: SessionContext,
    db: Database,
    config: Config,
    status: Any,
) -> None:
    """Check content status and show progress for papers requiring processing."""
    papers_with_full_text = []

    # Find papers that need full_text content
    for paper_id, entry in session_context.papers.items():
        if entry.context_type == "full_text":
            papers_with_full_text.append((paper_id, entry))

    if not papers_with_full_text:
        return

    # Check which papers need downloading/processing
    for i, (paper_id, entry) in enumerate(papers_with_full_text, 1):
        status.update(
            f"[blue]Loading content for {entry.paper_title} ({i}/{len(papers_with_full_text)})...[/blue]",
        )

        # Check if content is already cached
        md_path = config.base_dir / "pdfs" / f"{paper_id}.md"
        if md_path.exists():
            status.update(f"[blue]Using cached content for {entry.paper_title}[/blue]")
        else:
            # PDFProcessor will handle download/extraction during context loading
            # Just show appropriate progress messages
            pdf_path = config.base_dir / "pdfs" / f"{paper_id}.pdf"
            if pdf_path.exists():
                status.update(
                    f"[blue]Extracting text from {entry.paper_title}...[/blue]",
                )
            else:
                status.update(
                    f"[blue]Downloading PDF for {entry.paper_title}...[/blue]",
                )


async def _run_synthesis(
    query: str,
    session_context: SessionContext,
    db: Database,
    config: Config,
    token_tracker: TokenTracker | None,
    status: Any,
) -> None:
    """
    Internal async function to run synthesis.
    Status manager is already started by caller.
    """
    logger.info("synthesize_command", query=query[:100])

    try:
        # Show progress for content loading
        await _check_and_show_content_status(session_context, db, config, status)

        # Update status to indicate we're now loading context
        status.update("[blue]Preparing context for synthesis...[/blue]")

        # Get all context with loaded content (PDFProcessor integration happens here)
        combined_context = await session_context.get_all_context(db, config)

        # Build synthesis prompt
        prompt = f"""Based on the following papers and their content, please synthesize an answer to this question:

Question: {query}

Papers in Context ({session_context.get_paper_count()} papers):
{combined_context}

Please provide a comprehensive synthesis that:
1. Addresses the question directly
2. Draws from all relevant papers
3. Highlights key insights and connections
4. Notes any contradictions or debates
"""

        # Update status for LLM processing
        status.update("[blue]Generating synthesis...[/blue]")

        # Initialize LLM client
        llm_client = LLMClient(config, token_tracker=token_tracker)

        try:
            # Get synthesis from LLM (use large model for synthesis)
            response = await llm_client.complete(
                [
                    {
                        "role": "system",
                        "content": "You are an expert at synthesizing academic papers.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model_size="large",
                operation_type="synthesis",
            )

            synthesis_result = response.get("content", "")

            # Stop status before printing results
            status.stop()

            # Format output
            console.print("\n[bold cyan]Synthesis Result[/bold cyan]")
            console.print(
                f"[dim]Based on {session_context.get_paper_count()} papers in context[/dim]\n",
            )
            console.print(synthesis_result)

        except Exception as e:
            status.stop()
            logger.error("synthesis_failed", error=str(e))
            console.print(f"[red]Synthesis failed: {str(e)}[/red]")
        finally:
            await llm_client.close()
    except Exception as e:
        status.stop()
        logger.error("synthesis_failed", error=str(e))
        console.print(f"[red]Synthesis failed: {str(e)}[/red]")


async def handle_synthesize(
    query: str,
    session_context: SessionContext,
    db: Database,
    config: Config,
    token_tracker: TokenTracker | None = None,
) -> str:
    """
    Handle /synthesize command using papers in current context.
    This is the version called by the NL handler.

    IMPORTANT: Uses ALL context types for ALL papers in context.
    """
    logger.info("synthesize_nl_command", query=query[:100])

    # Check if context is empty
    if not session_context.papers:
        return '[yellow]No papers in context. Use /cadd to add papers first.[/yellow]\n\nExample: /cadd "attention is all you need" full_text'

    # Initialize status manager
    from litai.ui.status_manager import get_status_manager

    status = get_status_manager()

    # Start status indicator
    paper_count = session_context.get_paper_count()
    status.start(
        f"[blue]Synthesizing insights from {paper_count} paper{'s' if paper_count != 1 else ''}...[/blue]",
    )

    await _run_synthesis(query, session_context, db, config, token_tracker, status)
    return ""  # Already printed


def handle_synthesize_command(
    args: str,
    db: Database,
    session_context: SessionContext,
    config: Config,
    token_tracker: TokenTracker | None = None,
) -> None:
    """
    Handle the /synthesize command from CLI.
    """
    if not args.strip():
        console.print("[red]Usage: /synthesize <your question>[/red]")
        console.print(
            "\nExample: /synthesize What are the key innovations in transformer architectures?",
        )
        console.print("\nFor example synthesis questions, use: /synthesize --examples")
        return

    # Check for --examples
    if args.strip() == "--examples":
        show_synthesis_examples()
        return

    # Check if context is empty early
    if not session_context.papers:
        console.print(
            '[yellow]No papers in context. Use /cadd to add papers first.[/yellow]\n\nExample: /cadd "attention is all you need" full_text',
        )
        return

    # Initialize and start status manager immediately
    from litai.ui.status_manager import get_status_manager

    status = get_status_manager()

    paper_count = session_context.get_paper_count()
    status.start(
        f"[blue]Synthesizing insights from {paper_count} paper{'s' if paper_count != 1 else ''}...[/blue]",
    )

    # Run synthesis
    import asyncio

    try:
        asyncio.run(
            _run_synthesis(args, session_context, db, config, token_tracker, status),
        )
    except Exception as e:
        status.stop()
        logger.error("synthesis_command_failed", error=str(e))
        console.print(f"[red]Synthesis failed: {str(e)}[/red]")


def show_synthesis_examples() -> None:
    """Display synthesis example questions that users can ask with LitAI."""
    from litai.output_formatter import OutputFormatter

    output = OutputFormatter(console)

    console.print("\n[bold heading]SYNTHESIS EXAMPLE QUESTIONS[/bold heading]")
    console.print("[dim_text]Learn to ask better synthesis questions[/dim_text]\n")

    # Experimental Troubleshooting
    output.section("Debugging Experiments", "🔧", "bold cyan")
    console.print("• Why does this baseline perform differently than reported?")
    console.print("• What hyperparameters do papers actually use vs report?")
    console.print('• Which "standard" preprocessing steps vary wildly across papers?')
    console.print("• What's the actual variance in this metric across the literature?")
    console.print("• Do others see this instability/artifact? How do they handle it?\n")

    # Methods & Analysis
    output.section("Methods & Analysis", "📊", "bold cyan")
    console.print("• What statistical tests does this subfield actually use/trust?")
    console.print("• How do people typically visualize this type of data?")
    console.print("• What's the standard ablation set for this method?")
    console.print("• Which evaluation metrics correlate with downstream performance?")
    console.print("• What dataset splits/versions are people actually using?\n")

    # Contextualizing Results
    output.section("Contextualizing Results", "📈", "bold cyan")
    console.print("• Is my improvement within noise bounds of prior work?")
    console.print("• What explains the gap between my results and theirs?")
    console.print("• Which prior results are suspicious outliers?")
    console.print("• Have others tried and failed at this approach?")
    console.print(
        "• What's the real SOTA when you account for compute/data differences?\n",
    )

    # Technical Details
    output.section("Technical Details", "🎯", "bold cyan")
    console.print("• What batch size/learning rate scaling laws apply here?")
    console.print("• Which optimizer quirks matter for this problem?")
    console.print("• What numerical precision issues arise at this scale?")
    console.print("• How long do people actually train these models?")
    console.print("• What early stopping criteria work in practice?\n")

    # Common Research Questions
    output.section("Common Research Questions", "🔍", "bold cyan")
    console.print("• Has someone done this research already?")
    console.print("• What methods do other people use to analyze this problem?")
    console.print("• What are typical issues people run into?")
    console.print("• How do people typically do these analyses?")
    console.print("• Is our result consistent or contradictory with the literature?")
    console.print("• What are known open problems in the field?")
    console.print("• Any key papers I forgot to cite?\n")
