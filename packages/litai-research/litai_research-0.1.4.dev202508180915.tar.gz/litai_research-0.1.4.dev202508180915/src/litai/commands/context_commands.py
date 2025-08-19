"""Context management commands for LitAI."""

from rich.console import Console
from rich.table import Table

from litai.commands.help_system import help_registry
from litai.context_manager import SessionContext
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.paper_resolver import resolve_paper_references
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


async def handle_context_add(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """
    Handle /cadd command.
    Usage:
        /cadd  (add all papers from collection)
        /cadd <paper reference> [full-text|abstract|notes]
        /cadd --tag <tag_name> [full-text|abstract|notes]

    Examples:
        /cadd  (add all papers as abstracts)
        /cadd 1 full-text
        /cadd "BERT paper" notes
        /cadd "attention is all you need" abstract
        /cadd --tag inference abstract
        /cadd --tag GPT full-text
    """
    logger.info("context_add_command", args=args)

    if not args:
        # Add all papers from collection (similar to /add empty)
        papers = db.list_papers(limit=1000)
        if not papers:
            return "[yellow]No papers in your collection to add. Use /find first.[/yellow]"
        
        # Default to abstract for bulk add
        context_type = "abstract"
        
        # Track results
        added_count = 0
        skipped_count = 0
        
        for paper in papers:
            # Check if already in context with same type
            if session_context.has_paper(paper.paper_id):
                entry = session_context.papers[paper.paper_id]
                if context_type == entry.context_type:
                    skipped_count += 1
                    continue
            
            # Add to session context (metadata only)
            session_context.add_paper(
                paper_id=paper.paper_id,
                paper_title=paper.title,
                context_type=context_type,
            )
            added_count += 1
        
        # Report results
        result_msg = f"[green]✓ Added {added_count} papers from collection ({context_type})[/green]"
        if skipped_count > 0:
            result_msg += f"\n[yellow]Skipped {skipped_count} papers already in context with same type[/yellow]"
        console.print(result_msg)
        return ""

    # Check if using --tag parameter
    if "--tag" in args:
        # Parse tag name and optional context type
        parts = args.split()
        try:
            tag_idx = parts.index("--tag")
            if tag_idx + 1 >= len(parts):
                return "[red]Usage: /cadd --tag <tag_name> [full-text|abstract|notes][/red]"
            tag_name = parts[tag_idx + 1]

            # Determine context type (default: abstract)
            context_type = "abstract"
            for ct in ["full-text", "full_text", "abstract", "notes"]:
                if ct in parts[tag_idx + 2 :]:
                    context_type = ct.replace("-", "_")
                    break

            # Get papers with tag
            papers = db.list_papers(tag=tag_name)
            if not papers:
                return f"[yellow]No papers found with tag '{tag_name}'[/yellow]"

            # Track results
            added_count = 0
            skipped_count = 0

            # Add each paper to context
            for tag_paper in papers:
                # Check if already in context with same type
                if session_context.has_paper(tag_paper.paper_id):
                    entry = session_context.papers[tag_paper.paper_id]
                    if context_type == entry.context_type:
                        skipped_count += 1
                        continue

                # Add to session context (metadata only)
                session_context.add_paper(
                    paper_id=tag_paper.paper_id,
                    paper_title=tag_paper.title,
                    context_type=context_type,
                )
                added_count += 1

            # Report results
            result_msg = f"[green]✓ Added {added_count} papers with tag '{tag_name}' ({context_type})[/green]"
            if skipped_count > 0:
                result_msg += f"\n[yellow]Skipped {skipped_count} papers already in context with same type[/yellow]"
            console.print(result_msg)
            return ""

        except (ValueError, IndexError):
            return "[red]Usage: /cadd --tag <tag_name> [full-text|abstract|notes][/red]"

    # Original single paper logic
    # Parse context type if provided (default to full-text)
    context_type = "full_text"
    paper_ref = args

    # Check if context type is specified
    for ct in ["full-text", "full_text", "abstract", "notes"]:
        if args.endswith(f" {ct}"):
            context_type = ct.replace("-", "_")
            paper_ref = args[: -len(f" {ct}")].strip()
            break

    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)

    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"

    # Get the paper
    paper: Paper | None = db.get_paper(paper_id)
    if not paper:
        return f"[red]Paper not found in database: {paper_id}[/red]"

    # Check if already in context
    if session_context.has_paper(paper_id):
        # Paper already in context, will replace with new context type
        entry = session_context.papers[paper_id]
        if context_type == entry.context_type:
            return f"[yellow]Paper already has {context_type} in context[/yellow]"

    # Add to session context (metadata only)
    session_context.add_paper(
        paper_id=paper_id,
        paper_title=paper.title,
        context_type=context_type,
    )

    console.print(f"[green]✓ Added '{paper.title[:60]}...' ({context_type})[/green]")
    return ""


async def handle_context_remove(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """
    Handle /cremove command.
    Usage:
        /cremove <paper reference>
        /cremove --tag <tag_name>

    Examples:
        /cremove 1
        /cremove "BERT paper"
        /cremove "attention paper"
        /cremove --tag inference
        /cremove --tag GPT
    """
    logger.info("context_remove_command", args=args)

    if not args:
        return (
            "[red]Usage: /cremove <paper reference> OR /cremove --tag <tag_name>[/red]"
        )

    # Check if using --tag parameter
    if "--tag" in args:
        # Parse tag name
        parts = args.split()
        try:
            tag_idx = parts.index("--tag")
            if tag_idx + 1 >= len(parts):
                return "[red]Usage: /cremove --tag <tag_name>[/red]"
            tag_name = parts[tag_idx + 1]

            # Get papers with tag that are in context
            papers = db.list_papers(tag=tag_name)
            if not papers:
                return f"[yellow]No papers found with tag '{tag_name}'[/yellow]"

            # Track results
            removed_count = 0
            not_in_context_count = 0

            # Remove each paper from context
            for tag_paper in papers:
                if session_context.has_paper(tag_paper.paper_id):
                    session_context.remove_paper(tag_paper.paper_id)
                    removed_count += 1
                else:
                    not_in_context_count += 1

            # Report results
            if removed_count == 0:
                return (
                    f"[yellow]No papers with tag '{tag_name}' were in context[/yellow]"
                )

            result_msg = f"[yellow]✓ Removed {removed_count} papers with tag '{tag_name}' from context[/yellow]"
            if not_in_context_count > 0:
                result_msg += (
                    f"\n[dim]({not_in_context_count} papers were not in context)[/dim]"
                )
            console.print(result_msg)
            return ""

        except (ValueError, IndexError):
            return "[red]Usage: /cremove --tag <tag_name>[/red]"

    # Original single paper logic
    paper_ref = args

    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)

    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"

    # Check if paper is in context
    if not session_context.has_paper(paper_id):
        return f"[yellow]Paper not in context: {paper_ref}[/yellow]"

    # Get paper title for display
    paper: Paper | None = db.get_paper(paper_id)
    paper_title = paper.title if paper else paper_id

    # Remove from context
    session_context.remove_paper(paper_id)

    console.print(f"[yellow]✓ Removed '{paper_title[:60]}...' from context[/yellow]")

    return ""


def handle_context_show(session_context: SessionContext, args: str = "") -> str:
    """
    Handle /cshow command.
    Displays current context as a table.
    """
    from litai.output_formatter import OutputFormatter

    output = OutputFormatter(console)

    logger.info("context_show_command_start")

    # Check for --help flag
    if args and args.strip() == "--help":
        help_text = help_registry.get("cshow")
        if help_text:
            return help_text.render()
        return "[red]Help not available[/red]"

    if not session_context.papers:
        logger.info("context_show_empty")
        return "[info]No papers in context. Use /cadd to add papers.[/info]"

    # Create table
    paper_count = session_context.get_paper_count()
    logger.info("context_show_displaying", paper_count=paper_count)

    # Use output.section for consistent formatting
    output.section(f"Current Context ({paper_count} papers)", "📋", "bold cyan")

    table = Table(show_header=True)
    table.add_column("Paper", style="bold")
    table.add_column("Context Type", style="cyan")

    # Build list for LLM context
    paper_summaries = []

    for _paper_id, entry in session_context.papers.items():
        title = (
            entry.paper_title[:80] + "..."
            if len(entry.paper_title) > 80
            else entry.paper_title
        )
        context_type = entry.context_type
        table.add_row(title, context_type)

        # Add to summary for LLM
        paper_summaries.append(f'"{entry.paper_title}" ({context_type})')

    console.print(table)
    logger.info("context_show_success", paper_count=paper_count)

    # Return summary for LLM context
    if paper_summaries:
        return f"Current context has {paper_count} papers:\n" + "\n".join(
            paper_summaries,
        )
    return ""


def handle_context_clear(session_context: SessionContext, args: str = "") -> str:
    """
    Handle /cclear command.
    Clears all context.
    """
    logger.info("context_clear_command_start")

    # Check for --help flag
    if args and args.strip() == "--help":
        help_text = help_registry.get("cclear")
        if help_text:
            return help_text.render()
        return "[red]Help not available[/red]"

    if not session_context.papers:
        logger.info("context_clear_already_empty")
        return "[info]Context is already empty.[/info]"

    paper_count = session_context.get_paper_count()
    logger.info("context_clear_clearing", paper_count=paper_count)
    session_context.clear()

    logger.info("context_clear_success", cleared_count=paper_count)
    return f"[green]✓ Cleared {paper_count} papers from context[/green]"


async def handle_context_modify(
    args: str,
    db: Database,
    session_context: SessionContext,
    llm_client: LLMClient,
) -> str:
    """
    Handle /cmodify command.
    Changes the context type for a paper or papers with a tag.
    Usage:
        /cmodify <new_context_type>  (modify all papers in context)
        /cmodify <paper reference> <new_context_type>
        /cmodify --tag <tag_name> <new_context_type>

    Examples:
        /cmodify full-text  (modify all papers to full-text)
        /cmodify abstract  (modify all papers to abstract)
        /cmodify 1 abstract
        /cmodify "BERT paper" notes
        /cmodify --tag inference full-text
        /cmodify --tag GPT notes
    """
    logger.info("context_modify_command", args=args)

    if not args:
        return "[red]Usage: /cmodify <new_context_type> OR /cmodify <paper reference> <new_context_type> OR /cmodify --tag <tag_name> <new_context_type>[/red]"

    # Smart detection: Check if single argument is a valid context type (modify all)
    args_normalized = args.strip().replace("-", "_")
    valid_types = ["full_text", "abstract", "notes"]
    
    if args_normalized in valid_types:
        # Modify ALL papers in context
        new_context_type = args_normalized
        
        if not session_context.papers:
            return "[yellow]No papers in context to modify. Use /cadd to add papers first.[/yellow]"
        
        # Track results
        modified_count = 0
        already_has_type_count = 0
        
        # Modify each paper in context
        for paper_id, entry in session_context.papers.items():
            old_context_type = entry.context_type
            
            # Check if already has this context type
            if new_context_type == old_context_type:
                already_has_type_count += 1
                continue
            
            # Get paper for title
            paper = db.get_paper(paper_id)
            if not paper:
                continue
                
            # Replace with new context type (metadata only)
            session_context.add_paper(
                paper_id=paper_id,
                paper_title=paper.title,
                context_type=new_context_type,
            )
            modified_count += 1
        
        # Report results
        if modified_count == 0:
            if already_has_type_count > 0:
                return f"[yellow]All {already_has_type_count} papers already have {new_context_type} context type[/yellow]"
            return "[yellow]No papers to modify[/yellow]"
        
        result_msg = f"[green]✓ Modified {modified_count} papers to {new_context_type}[/green]"
        if already_has_type_count > 0:
            result_msg += f"\n[dim]({already_has_type_count} papers already had {new_context_type})[/dim]"
        console.print(result_msg)
        return ""

    # Check if using --tag parameter
    if "--tag" in args:
        # Parse tag name and new context type
        parts = args.split()
        try:
            tag_idx = parts.index("--tag")
            if tag_idx + 2 >= len(parts):
                return "[red]Usage: /cmodify --tag <tag_name> <new_context_type>[/red]"
            tag_name = parts[tag_idx + 1]
            new_context_type = parts[tag_idx + 2].replace("-", "_")

            # Validate context type
            valid_types = ["full_text", "abstract", "notes"]
            if new_context_type not in valid_types:
                return f"[red]Invalid context type: {new_context_type}. Must be: {', '.join(valid_types)}[/red]"

            # Get papers with tag that are in context
            papers = db.list_papers(tag=tag_name)
            if not papers:
                return f"[yellow]No papers found with tag '{tag_name}'[/yellow]"

            # Track results
            modified_count = 0
            not_in_context_count = 0
            already_has_type_count = 0

            # Modify each paper in context
            for tag_paper in papers:
                if not session_context.has_paper(tag_paper.paper_id):
                    not_in_context_count += 1
                    continue

                # Get current context type
                entry = session_context.papers[tag_paper.paper_id]
                old_context_type = entry.context_type

                # Check if already has this context type
                if new_context_type == old_context_type:
                    already_has_type_count += 1
                    continue

                # Replace with new context type (metadata only)
                session_context.add_paper(
                    paper_id=tag_paper.paper_id,
                    paper_title=tag_paper.title,
                    context_type=new_context_type,
                )
                modified_count += 1

            # Report results
            if modified_count == 0:
                if not_in_context_count > 0:
                    return f"[yellow]No papers with tag '{tag_name}' were in context[/yellow]"
                if already_has_type_count > 0:
                    return f"[yellow]All papers with tag '{tag_name}' already have {new_context_type} context type[/yellow]"
                return "[yellow]No papers to modify[/yellow]"

            result_msg = f"[green]✓ Modified {modified_count} papers with tag '{tag_name}' to {new_context_type}[/green]"
            if not_in_context_count > 0:
                result_msg += (
                    f"\n[dim]({not_in_context_count} papers were not in context)[/dim]"
                )
            if already_has_type_count > 0:
                result_msg += f"\n[dim]({already_has_type_count} papers already had {new_context_type})[/dim]"
            console.print(result_msg)
            return ""

        except (ValueError, IndexError):
            return "[red]Usage: /cmodify --tag <tag_name> <new_context_type>[/red]"

    # Original single paper logic
    # Parse arguments: paper_ref new_type
    parts = args.strip().split()
    if len(parts) < 2:
        return "[red]Usage: /cmodify <paper reference> <new_context_type>[/red]"

    # Handle quoted paper references
    if args.startswith('"'):
        # Find the closing quote
        end_quote = args.find('"', 1)
        if end_quote == -1:
            return "[red]Missing closing quote for paper reference[/red]"
        paper_ref = args[1:end_quote]
        remaining = args[end_quote + 1 :].strip().split()
        if len(remaining) < 1:
            return "[red]Must specify new context type[/red]"
        new_context_type = remaining[0].replace("-", "_")
    else:
        # Last part is context type, everything else is paper ref
        paper_ref = " ".join(parts[:-1])
        new_context_type = parts[-1].replace("-", "_")

    # Validate context type
    valid_types = ["full_text", "abstract", "notes"]
    if new_context_type not in valid_types:
        return f"[red]Invalid context type: {new_context_type}. Must be: {', '.join(valid_types)}[/red]"

    # Resolve paper reference to a single paper ID
    resolved_query, paper_id = await resolve_paper_references(paper_ref, db, llm_client)

    if not paper_id:
        return f"[yellow]No paper found matching '{paper_ref}'[/yellow]"

    if not session_context.has_paper(paper_id):
        return f"[yellow]Paper not in context: {paper_ref}[/yellow]"

    # Get current context type
    entry = session_context.papers[paper_id]
    old_context_type = entry.context_type

    # Check if already has this context type
    if new_context_type == old_context_type:
        return f"[yellow]Paper already has {new_context_type} context type[/yellow]"

    # Get the paper
    paper: Paper | None = db.get_paper(paper_id)
    if not paper:
        return "[red]Paper not found in database[/red]"

    # Replace with new context type (metadata only)
    session_context.add_paper(
        paper_id=paper_id,
        paper_title=paper.title,
        context_type=new_context_type,
    )

    console.print(
        f"[green]✓ Modified '{paper.title[:60]}...' from {old_context_type} to {new_context_type}[/green]",
    )
    return ""

