"""Token usage and cost tracking commands for LitAI."""

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from litai.config import Config
from litai.token_tracker import TokenTracker
from litai.utils.logger import get_logger

logger = get_logger(__name__)

# Custom theme for console output
custom_theme = Theme(
    {
        "primary": "#1f78b4",
        "secondary": "#6a3d9a",
        "success": "#33a02c",
        "warning": "#ff7f00",
        "error": "#e31a1c",
        "info": "#a6cee3",
        "accent": "#b2df8a",
        "number": "#fb9a99",
        "dim_text": "dim",
        "heading": "bold #1f78b4",
        "command": "#1f78b4",
    },
)

console = Console(theme=custom_theme)


def show_command_help(command: str) -> None:
    """Show help for a specific command."""
    if command == "tokens":
        console.print("\n[bold]Token Usage Tracking[/bold]")
        console.print(
            "\nView token usage statistics and cost optimization information.",
        )
        console.print("\n[bold]Usage:[/bold]")
        console.print(
            "  [cyan]/tokens[/cyan]                      Show current session usage",
        )
        console.print(
            "  [cyan]/tokens session[/cyan]              Show current session usage",
        )
        console.print(
            "  [cyan]/tokens all[/cyan]                  Show all-time usage statistics",
        )
        console.print("\n[bold]Examples:[/bold]")
        console.print("  /tokens                    # Quick session summary")
        console.print("  /tokens all                # Detailed all-time statistics")


def format_number(num: int) -> str:
    """Format a number with thousand separators.

    Args:
        num: Number to format

    Returns:
        Formatted number string
    """
    return f"{num:,}"


def handle_tokens_command(
    args: str, config: Config, token_tracker: TokenTracker | None = None,
) -> None:
    """Handle /tokens commands.

    Args:
        args: Command arguments
        config: Configuration instance
        token_tracker: Optional token tracker instance
    """
    if not token_tracker:
        console.print("[yellow]Token tracking not available in this session.[/yellow]")
        console.print("Token tracking is only available during active LitAI usage.")
        return

    args_parts = args.strip().split()
    subcommand = args_parts[0] if args_parts else "session"

    if subcommand == "session":
        _show_session_usage(token_tracker)
    elif subcommand == "all":
        _show_all_time_usage(token_tracker, config)
    else:
        console.print(f"[red]Unknown tokens subcommand: {subcommand}[/red]")
        console.print("Available subcommands:")
        console.print("  [cyan]session[/cyan] - Show current session usage")
        console.print("  [cyan]all[/cyan] - Show all-time usage statistics")


def _show_session_usage(token_tracker: TokenTracker) -> None:
    """Show current session token usage.

    Args:
        token_tracker: Token tracker instance
    """
    session_summary = token_tracker.get_session_summary()

    if session_summary["total"] == 0:
        console.print("\n[dim_text]No tokens used in this session yet.[/dim_text]")
        return

    console.print("\n[bold]Current Session Usage[/bold]")

    # Create summary table
    table = Table(show_header=True)
    table.add_column("Model Type", style="bold")
    table.add_column("Tokens", style="number", justify="right")
    table.add_column("Percentage", style="info", justify="right")

    small_tokens = session_summary["small_model"]
    large_tokens = session_summary["large_model"]
    total_tokens = session_summary["total"]

    # Calculate percentages
    small_pct = (small_tokens / total_tokens * 100) if total_tokens > 0 else 0
    large_pct = (large_tokens / total_tokens * 100) if total_tokens > 0 else 0

    table.add_row(
        "[primary]Small Model[/primary]",
        format_number(small_tokens),
        f"{small_pct:.1f}%",
    )

    table.add_row(
        "[secondary]Large Model[/secondary]",
        format_number(large_tokens),
        f"{large_pct:.1f}%",
    )

    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{format_number(total_tokens)}[/bold]",
        "[bold]100.0%[/bold]",
    )

    console.print(table)
    console.print(
        f"\n[dim_text]Requests made: {session_summary['requests']}[/dim_text]",
    )

    # Show efficiency tip
    if total_tokens > 0:
        efficiency = (small_tokens / total_tokens * 100) if total_tokens > 0 else 0
        if efficiency > 70:
            console.print(
                "[accent]Great! You're using small models efficiently.[/accent]",
            )


def _show_all_time_usage(token_tracker: TokenTracker, config: Config) -> None:
    """Show all-time token usage statistics.

    Args:
        token_tracker: Token tracker instance
        config: Configuration instance
    """
    stats = token_tracker.stats

    if stats.total_tokens == 0:
        console.print("\n[dim_text]No token usage recorded yet.[/dim_text]")
        return

    console.print("\n[bold]All-Time Usage Statistics[/bold]")

    # Create detailed table
    table = Table(show_header=True)
    table.add_column("Model Type", style="bold")
    table.add_column("Input Tokens", style="number", justify="right")
    table.add_column("Output Tokens", style="number", justify="right")
    table.add_column("Total Tokens", style="number", justify="right")
    table.add_column("Percentage", style="info", justify="right")

    small_total = stats.small_model_total
    large_total = stats.large_model_total
    total_tokens = stats.total_tokens

    # Calculate percentages
    small_pct = (small_total / total_tokens * 100) if total_tokens > 0 else 0
    large_pct = (large_total / total_tokens * 100) if total_tokens > 0 else 0

    table.add_row(
        "[primary]Small Model[/primary]",
        format_number(stats.small_model_input),
        format_number(stats.small_model_output),
        format_number(small_total),
        f"{small_pct:.1f}%",
    )

    table.add_row(
        "[secondary]Large Model[/secondary]",
        format_number(stats.large_model_input),
        format_number(stats.large_model_output),
        format_number(large_total),
        f"{large_pct:.1f}%",
    )

    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{format_number(stats.small_model_input + stats.large_model_input)}[/bold]",
        f"[bold]{format_number(stats.small_model_output + stats.large_model_output)}[/bold]",
        f"[bold]{format_number(total_tokens)}[/bold]",
        "[bold]100.0%[/bold]",
    )

    console.print(table)
    console.print(f"\n[dim_text]Total requests: {stats.total_requests}[/dim_text]")
    console.print(
        f"[dim_text]Average tokens per request: {total_tokens // stats.total_requests if stats.total_requests > 0 else 0}[/dim_text]",
    )

    # Show current model configuration
    small_model = config.get_small_model()
    large_model = config.get_large_model()
    console.print(
        f"\n[dim_text]Current models: {small_model} (small), {large_model} (large)[/dim_text]",
    )

    # Show efficiency insights
    if total_tokens > 1000:  # Only show insights for meaningful usage
        efficiency = (small_total / total_tokens * 100) if total_tokens > 0 else 0
        if efficiency > 80:
            console.print(
                "[accent]Excellent efficiency! You're maximizing small model usage.[/accent]",
            )
        elif efficiency > 60:
            console.print(
                "[success]Good efficiency. You're balancing model usage well.[/success]",
            )
        elif efficiency < 40:
            console.print(
                "[warning]Consider using small models more often for better efficiency.[/warning]",
            )


def format_session_summary_compact(session_summary: dict[str, int]) -> str:
    """Format session summary for compact display.

    Args:
        session_summary: Session summary dictionary

    Returns:
        Formatted summary string
    """
    total = session_summary.get("total", 0)
    small = session_summary.get("small_model", 0)
    large = session_summary.get("large_model", 0)

    if total == 0:
        return "Session: 0 tokens"

    return f"Session: {format_number(total)} tokens ({format_number(small)} small, {format_number(large)} large)"
