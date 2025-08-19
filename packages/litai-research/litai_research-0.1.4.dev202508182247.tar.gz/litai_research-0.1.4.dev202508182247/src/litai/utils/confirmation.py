"""Unified confirmation utilities for CLI commands."""

from rich.console import Console
from rich.prompt import Prompt


def get_user_confirmation(console: Console, message: str, style: str = "simple") -> bool:
    """Get user confirmation with unified interface.
    
    Args:
        console: Rich console instance
        message: The confirmation message to display
        style: Either "simple" (yes/no) or "rich" (yes/y/no/n with default no)
    
    Returns:
        True if user confirmed, False otherwise
    """
    if style == "rich":
        confirmation = Prompt.ask(
            f"\n{message}",
            choices=["yes", "y", "no", "n"], 
            default="no"
        )
        return confirmation in ["yes", "y"]
    else:
        # Simple style - just needs "yes" to confirm
        confirm = console.input(f"[yellow]{message} Type 'yes' to confirm: [/yellow]")
        return confirm.lower() == "yes"