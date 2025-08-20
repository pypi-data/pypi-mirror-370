"""Synthesis command that uses current context."""

import asyncio
from typing import Any

import openai
from rich.console import Console

from litai.config import Config
from litai.context_manager import ContextEntry, SessionContext
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

async def _process_single_paper(
    paper_id: str,
    entry: ContextEntry,
    query: str,
    session_context: SessionContext,
    db: Database,
    config: Config,
    token_tracker: TokenTracker | None,
) -> dict:
    """Process a single paper with the synthesis question."""
    logger.info(
        "sharded_synthesis_processing_paper",
        paper_id=paper_id,
        title=entry.paper_title,
        context_type=entry.context_type,
    )
    
    try:
        # Load paper content
        paper_context = await session_context._load_paper_content(
            db, paper_id, entry.context_type, config,
        )
        
        if not paper_context:
            logger.warning(
                "sharded_synthesis_no_content",
                paper_id=paper_id,
                title=entry.paper_title,
                context_type=entry.context_type,
            )
            return {
                "paper_id": paper_id,
                "title": entry.paper_title,
                "response": "",
                "error": "No content available",
            }
        
        logger.debug(
            "sharded_synthesis_content_loaded",
            paper_id=paper_id,
            content_length=len(paper_context),
        )
        
        prompt = f"""
        Based on this paper, answer the following question:
        
        Question: {query}
        
        Paper: {entry.paper_title}
        Content: {paper_context}
        
        Provide a detailed analysis focusing on how this paper addresses the question.
        """
        
        llm_client = LLMClient(config, token_tracker=token_tracker)
        try:
            response = await llm_client.complete(
                [{"role": "user", "content": prompt}],
                model_size="large",
                operation_type="paper_analysis",
            )
            
            logger.info(
                "sharded_synthesis_paper_completed",
                paper_id=paper_id,
                title=entry.paper_title,
                response_length=len(response.get("content", "")),
            )
            
            return {
                "paper_id": paper_id,
                "title": entry.paper_title,
                "response": response.get("content", ""),
                "error": None,
            }
        finally:
            await llm_client.close()
    except Exception as e:
        logger.error(
            "sharded_synthesis_paper_failed",
            paper_id=paper_id,
            title=entry.paper_title,
            error=str(e),
            error_type=type(e).__name__,
        )
        return {
            "paper_id": paper_id,
            "title": entry.paper_title,
            "response": "",
            "error": str(e),
        }


async def _run_sharded_synthesis(
    query: str,
    session_context: SessionContext,
    db: Database,
    config: Config,
    token_tracker: TokenTracker | None,
    status: Any,
) -> None:
    """Run synthesis in sharded mode - process each paper individually then combine."""
    papers_list = list(session_context.papers.items())
    
    logger.info(
        "sharded_synthesis_started",
        query=query[:100],
        paper_count=len(papers_list),
        papers=[{"id": p[0], "title": p[1].paper_title, "type": p[1].context_type} for p in papers_list],
    )
    
    # Phase 1: Process each paper individually in parallel
    status.update(f"[blue]Processing {len(papers_list)} papers in parallel...[/blue]")
    
    # Create tasks for parallel processing
    tasks = []
    for paper_id, entry in papers_list:
        task = _process_single_paper(
            paper_id, entry, query, session_context, db, config, token_tracker,
        )
        tasks.append(task)
    
    logger.debug("sharded_synthesis_tasks_created", task_count=len(tasks))
    
    # Run all paper analyses in parallel
    paper_responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info(
        "sharded_synthesis_papers_processed",
        total_papers=len(paper_responses),
        successful_papers=sum(1 for r in paper_responses if isinstance(r, dict) and not r.get("error")),
        failed_papers=sum(1 for r in paper_responses if isinstance(r, Exception) or (isinstance(r, dict) and r.get("error"))),
    )
    
    # Phase 2: Combine responses
    status.update("[blue]Synthesizing results...[/blue]")
    
    # Format paper responses
    formatted_responses = []
    for response in paper_responses:
        if isinstance(response, dict) and not response.get("error"):
            formatted_responses.append(f"\nPaper: {response['title']}\n{response['response']}")
            logger.debug(
                "sharded_synthesis_paper_included",
                paper_id=response['paper_id'],
                title=response['title'],
            )
        elif isinstance(response, Exception):
            logger.warning(
                "sharded_synthesis_paper_exception",
                error=str(response),
                error_type=type(response).__name__,
            )
        elif isinstance(response, dict) and response.get("error"):
            logger.warning(
                "sharded_synthesis_paper_error",
                paper_id=response['paper_id'],
                title=response['title'],
                error=response['error'],
            )
    
    if not formatted_responses:
        logger.error("sharded_synthesis_no_valid_responses")
        status.stop()
        console.print("[red]Failed to process any papers. Please check the logs.[/red]")
        return
    
    logger.info(
        "sharded_synthesis_combining",
        valid_responses=len(formatted_responses),
        total_response_chars=sum(len(r) for r in formatted_responses),
    )
    
    # Build combined prompt (internal only - not shown to user)
    responses_text = '\n'.join(formatted_responses)
    combined_prompt = f"""
    Question: {query}
    
    Individual paper analyses:
    {responses_text}
    
    Synthesize these analyses into a comprehensive answer that addresses the original question.
    """
    
    try:
        # Get final synthesis
        llm_client = LLMClient(config, token_tracker=token_tracker)
        try:
            final_response = await llm_client.complete(
                [{"role": "user", "content": combined_prompt}],
                model_size="large",
                operation_type="synthesis",
            )
        
            logger.info(
                "sharded_synthesis_completed",
                final_response_length=len(final_response.get("content", "")),
            )
            
            # Display only the final synthesis to the user
            status.stop()
            console.print("\n[bold cyan]Synthesis Result[/bold cyan]")
            console.print(f"[dim]Based on {len(formatted_responses)} papers successfully processed[/dim]\n")
            console.print(final_response.get("content", ""))
        finally:
            await llm_client.close()
        
    except Exception as e:
        logger.error(
            "sharded_synthesis_final_synthesis_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        status.stop()
        console.print(f"[red]Failed to synthesize results: {str(e)}[/red]")
        raise

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

    except openai.RateLimitError:
        # Just re-raise - let the caller handle the error message
        raise
    except Exception as e:
        logger.error("synthesis_failed", error=str(e))
        raise
    finally:
        status.stop()
        await llm_client.close()




async def handle_synthesize_command(
    args: str,
    db: Database,
    session_context: SessionContext,
    config: Config,
    token_tracker: TokenTracker | None = None,
    sharded: bool = False,
) -> str | None:
    """
    Handle the /synthesize command from CLI.
    
    Returns:
        None on success, error message string on failure
    """
    if not args.strip():
        console.print("[red]Usage: /synthesize <your question>[/red]")
        console.print(
            "\nExample: /synthesize What are the key innovations in transformer architectures?",
        )
        console.print("\nFor example synthesis questions, use: /synthesize --examples")
        return "Usage: /synthesize <your question>"

    # Check for --examples
    if args.strip() == "--examples":
        show_synthesis_examples()
        return None

    # Check if context is empty early
    if not session_context.papers:
        console.print(
            '[yellow]No papers in context. Use /cadd to add papers first.[/yellow]\n\nExample: /cadd "attention is all you need" full_text',
        )
        return "No papers in context. Use /cadd to add papers first."

    # Initialize and start status manager immediately
    from litai.ui.status_manager import get_status_manager

    status = get_status_manager()
    
    paper_count = session_context.get_paper_count()
    status.start(
        f"[blue]Synthesizing insights from {paper_count} paper{'s' if paper_count != 1 else ''}...[/blue]",
    )

    # Run synthesis
    try:
        if sharded:
            logger.info(
                "synthesis_command_sharded_mode",
                query=args[:100],
                paper_count=paper_count,
            )
            result = await _run_sharded_synthesis(args, session_context, db, config, token_tracker, status)
        else:
            logger.info(
                "synthesis_command_regular_mode",
                query=args[:100],
                paper_count=paper_count,
            )
            result = await _run_synthesis(args, session_context, db, config, token_tracker, status)
        # Success - return the synthesis result with instruction
        if result:
            return result + "\n\nIMPORTANT: The user can see the synthesis output directly above. Do NOT re-analyze or summarize it. Simply ask if they have any further questions."
        return result
    except openai.RateLimitError as e:
        logger.error(
            "synthesis_rate_limit_error",
            error=str(e),
            mode="sharded" if sharded else "regular",
            paper_count=paper_count,
        )
        console.print("\n[red]Synthesis failed: Request too large[/red]\n")
        if not sharded:
            console.print("[yellow]The request is too large. Try using sharded mode:[/yellow]")
            console.print(f"[dim]/synthesize --sharded {args}[/dim]")
            console.print("\n[dim]This will process each paper individually then combine the results.[/dim]\n")
            return "Synthesis failed: Request too large. IMPORTANT: Do NOT suggest alternative approaches or create your own plan. Simply tell the user: 'The request exceeds API limits. Please use sharded mode by setting sharded=True in the synthesize command.'"
        console.print("[yellow]Even sharded mode exceeded limits. Try reducing the number of papers or using abstracts instead of full_text.[/yellow]")
        return "Synthesis failed: Even sharded mode exceeded limits. IMPORTANT: Do NOT suggest alternative approaches. Simply tell the user: 'Even sharded mode exceeded limits. Please reduce the number of papers or use abstracts instead of full_text.'"
    except Exception as e:
        logger.error(
            "synthesis_command_failed",
            error=str(e),
            error_type=type(e).__name__,
            mode="sharded" if sharded else "regular",
        )
        console.print(f"[red]Synthesis failed: {str(e)}[/red]")
        return f"Synthesis failed: {str(e)}"


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
