"""Tool call approval system for user control over AI actions."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from litai.config import Config
from litai.utils.logger import get_logger

if TYPE_CHECKING:
    from litai.ui.status_manager import StatusManager

logger = get_logger(__name__)
console = Console()


@dataclass
class ToolCall:
    """Represents a pending tool call."""

    id: str
    name: str
    description: str  # Human-readable explanation
    arguments: dict
    user_command: str | None = None  # Formatted command for display


@dataclass
class ApprovalResponse:
    """User's response to a tool call."""

    approved: bool
    cancel_all: bool = False


# Mapping from internal tool names to user commands
TOOL_TO_COMMAND_MAP = {
    "find_papers": "/find",
    "add_paper": "/add",
    "papers_command": "/collection",
    "remove_paper": "/remove",
    "manage_paper_tags": "/tag",
    "synthesize": "/synthesize",
    "note": "/note",
    "prompt": "/prompt",
    "context_show": "/cshow",
    "resolve_paper": "/resolve",
    "handle_context_add": "/cadd",
    "handle_context_remove": "/cremove",
    "handle_context_modify": "/cmodify",
}


def format_tool_as_command(call: ToolCall) -> str:
    """Format a tool call as the user command.

    Args:
        call: The tool call to format

    Returns:
        Formatted command string that user would type
    """
    base_cmd = TOOL_TO_COMMAND_MAP.get(call.name, f"/{call.name}")

    # Format based on specific tool and its arguments
    if call.name == "find_papers":
        if "query" in call.arguments and call.arguments["query"]:
            return f"{base_cmd} {call.arguments['query']}"
        if call.arguments.get("show_recent"):
            return base_cmd
        return base_cmd

    if call.name == "add_paper":
        if "paper_numbers" in call.arguments:
            nums = call.arguments["paper_numbers"]
            if isinstance(nums, str) and nums:
                return f"{base_cmd} {nums}"
            if isinstance(nums, list):
                return f"{base_cmd} {','.join(map(str, nums))}"
        return base_cmd  # Add all

    if call.name == "remove_paper":
        if "paper_numbers" in call.arguments:
            nums = call.arguments["paper_numbers"]
            if isinstance(nums, str) and nums:
                return f"{base_cmd} {nums}"
            if isinstance(nums, list):
                return f"{base_cmd} {','.join(map(str, nums))}"
        return base_cmd  # Remove all

    if call.name == "papers_command":
        args = []
        if call.arguments.get("show_tags"):
            args.append("--tags")
        if call.arguments.get("show_notes"):
            args.append("--notes")
        if "filter_tags" in call.arguments:
            tags = call.arguments["filter_tags"]
            if isinstance(tags, list):
                args.append(f"--filter {','.join(tags)}")
            else:
                args.append(f"--filter {tags}")
        if "page" in call.arguments and call.arguments["page"] != 1:
            args.append(f"--page {call.arguments['page']}")

        if args:
            return f"{base_cmd} {' '.join(args)}"
        return base_cmd

    if call.name == "manage_paper_tags":
        paper_num = call.arguments.get("paper_number", "")
        add_tags = call.arguments.get("add_tags", "")
        remove_tags = call.arguments.get("remove_tags", "")

        if add_tags:
            return f"{base_cmd} {paper_num} -a {add_tags}"
        if remove_tags:
            return f"{base_cmd} {paper_num} -r {remove_tags}"
        return f"{base_cmd} {paper_num}"

    if call.name == "resolve_paper":
        if "reference" in call.arguments:
            return f"{base_cmd} {call.arguments['reference']}"
        return base_cmd

    if call.name == "handle_context_add":
        paper_ref = call.arguments.get("paper_ref", "")
        context_type = call.arguments.get("context_type", "")
        if context_type:
            return f"{base_cmd} {paper_ref} {context_type}"
        return f"{base_cmd} {paper_ref}"

    if call.name == "handle_context_remove":
        paper_ref = call.arguments.get("paper_ref", "")
        return f"{base_cmd} {paper_ref}"

    if call.name == "handle_context_modify":
        paper_ref = call.arguments.get("paper_ref", "")
        action = call.arguments.get("action", "")
        if action:
            return f"{base_cmd} {paper_ref} --{action}"
        return f"{base_cmd} {paper_ref}"

    if call.name == "synthesize":
        query = call.arguments.get("query", "")
        if query:
            return f"{base_cmd} {query}"
        return base_cmd

    if call.name == "note":
        paper_number = call.arguments.get("paper_number", "")
        operation = call.arguments.get("operation", "")
        content = call.arguments.get("content", "")
        
        if operation == "view":
            return f"{base_cmd} {paper_number} view"
        if operation == "append" and content:
            return f"{base_cmd} {paper_number} append \"{content}\""
        return f"{base_cmd} {paper_number}"

    if call.name == "prompt":
        operation = call.arguments.get("operation", "")
        content = call.arguments.get("content", "")
        
        if operation == "view":
            return f"{base_cmd} view"
        if operation == "append" and content:
            return f"{base_cmd} append \"{content}\""
        return base_cmd

    if call.name == "context_show":
        return base_cmd

    # Default: show command with first string argument if available
    if call.arguments:
        for value in call.arguments.values():
            if isinstance(value, str) and value:
                return f"{base_cmd} {value}"
                break

    return base_cmd


class ToolApprovalManager:
    """Manages interactive approval of tool calls during synthesis."""

    def __init__(self, config: Config, status_manager: "StatusManager | None" = None):
        """Initialize with configuration.

        Args:
            config: Configuration instance
            status_manager: Optional StatusManager for animation control
        """
        self.config = config
        self.enabled = self._get_approval_setting()
        self.status_manager = status_manager

    def _get_approval_setting(self) -> bool:
        """Read tool_approval setting from config.

        Returns:
            True if tool approval is enabled (default), False otherwise
        """
        config_data = self.config.load_config()

        # First check for root-level tool_approval setting
        if "tool_approval" in config_data:
            return bool(config_data["tool_approval"])

        # Default to True (approval enabled)
        return True

    async def get_approval(self, tool_calls: list[ToolCall]) -> list[ToolCall]:
        """Get user approval for tool calls.

        Args:
            tool_calls: List of pending tool calls

        Returns:
            List of approved (possibly modified) tool calls
        """
        if not self.enabled:
            logger.info("Tool approval disabled, auto-approving all tools")
            return tool_calls

        return await self.interactive_approval(tool_calls)

    async def interactive_approval(self, tool_calls: list[ToolCall]) -> list[ToolCall]:
        """Show each tool call and get user response.

        Args:
            tool_calls: List of pending tool calls

        Returns:
            List of approved tool calls
        """
        approved = []

        for i, call in enumerate(tool_calls, 1):
            response = await self.show_and_get_response(call, i, len(tool_calls))

            if response.cancel_all:
                logger.info("User cancelled all remaining tool calls")
                break

            if response.approved:
                approved.append(call)
                logger.info(f"Tool approved: {call.name}")

        return approved

    async def show_and_get_response(
        self,
        call: ToolCall,
        index: int,
        total: int,
    ) -> ApprovalResponse:
        """Display tool call and get user input.

        Args:
            call: Tool call to display
            index: Current tool index (1-based)
            total: Total number of tools

        Returns:
            User's response to the tool call
        """
        # Pause any active animation before prompting
        if self.status_manager:
            await self.status_manager.pause()

        try:
            # Format as user command
            user_command = format_tool_as_command(call)

            # Create the display panel with command format
            panel_content = f"""[bold]Command:[/bold] [cyan]{user_command}[/cyan]
[dim]Description:[/dim] {call.description}

[dim]Parameters:[/dim]
{self._format_params(call.arguments)}"""

            panel = Panel(
                panel_content,
                title=f"Tool Call Recommended ({index}/{total})",
                border_style="cyan",
            )
            console.print(panel)

            # Show options
            console.print("[green]→[/green] \\[Enter] Approve")
            console.print(
                "[yellow]→[/yellow] \\[q] Cancel (tell the model to do something different)",
            )
            console.print()

            # Get user input
            response = Prompt.ask("> ", default="")

            # Parse response
            if response == "":  # Enter pressed
                return ApprovalResponse(approved=True)
            # Any other input cancels
            return ApprovalResponse(approved=False, cancel_all=True)
        finally:
            # Resume animation after prompt
            if self.status_manager:
                await self.status_manager.resume()

    def _format_params(self, params: dict) -> str:
        """Format parameters for display.

        Args:
            params: Parameters dictionary

        Returns:
            Formatted string for display
        """
        if not params:
            return "  (no parameters)"

        lines = []
        for key, value in params.items():
            if isinstance(value, list):
                if len(value) > 3:
                    value_str = f"[{', '.join(str(v) for v in value[:3])}...]"
                else:
                    value_str = str(value)
            elif isinstance(value, dict):
                value_str = "{...}"
            elif isinstance(value, str) and len(value) > 50:
                value_str = f'"{value[:47]}..."'
            else:
                value_str = str(value)
            lines.append(f"  {key}: {value_str}")

        return "\n".join(lines)
