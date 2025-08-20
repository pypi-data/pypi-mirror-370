"""Output formatting utilities for clearer CLI display."""

from rich.console import Console
from rich.text import Text


class OutputFormatter:
    """Handles consistent output formatting with clear section headers."""

    def __init__(self, console: Console):
        self.console = console

    def section(self, title: str, icon: str = "▶", style: str = "bold cyan") -> None:
        """Print a section header with icon and separator."""
        header = Text()
        header.append(f"\n{icon} ", style=style)  # Apply full style to icon
        header.append(title, style=style)
        header.append(" ", style="default")
        header.append(
            "━" * (self.console.width - len(f"{icon} {title} ") - 5), style="cyan",
        )
        self.console.print(header)

    def ai_response(self, content: str) -> None:
        """Format AI/LLM response with clear visual distinction."""
        self.section("LitAI Response", "░▒▓", "bold green")
        self.console.print(content)
        self.console.print()  # Add spacing

    def search_complete(self, count: int) -> None:
        """Format search completion message."""
        self.console.print(f"[green]✓[/green] Found {count} papers\n")

    def command_output(self, title: str, icon: str = "⛯") -> None:
        """Format command output header."""
        self.section(title, icon, "bold yellow")

    def error(self, message: str) -> None:
        """Format error message with clear visual distinction."""
        self.section("Error", "×", "bold red")
        self.console.print(f"[red]{message}[/red]\n")

    def success(self, message: str) -> None:
        """Format success message."""
        self.console.print(f"[green]✓ {message}[/green]\n")

    def processing(self, message: str) -> None:
        """Format processing/status message."""
        self.section("Processing", "~", "bold yellow")
        self.console.print(message)

    def synthesis_result(self, question: str) -> None:
        """Format synthesis result header."""
        self.section("Synthesis Result", "❖", "bold magenta")
        self.console.print(f"[bold]Question:[/bold] {question}\n")

    def tip(self, message: str) -> None:
        """Format tip/suggestion message."""
        self.console.print(f"[yellow]⊹ Tip: {message}[/yellow]\n")

    def divider(self, style: str = "dim") -> None:
        """Print a simple divider line."""
        self.console.print("─" * (self.console.width - 5), style=style)

    def format_tag(self, tag: str) -> str:
        """Format a single tag with color."""
        # Use hash of tag name to get consistent color per tag
        tag_colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
        color = tag_colors[hash(tag) % len(tag_colors)]
        return f"[{color}]#{tag}[/{color}]"

    def format_tags(self, tags: list[str], max_tags: int = 5) -> str:
        """Format a list of tags with colors and overflow handling."""
        if not tags:
            return ""

        formatted_tags = [self.format_tag(tag) for tag in tags[:max_tags]]
        result = " ".join(formatted_tags)

        if len(tags) > max_tags:
            result += f" [dim]+{len(tags) - max_tags} more[/dim]"

        return result
