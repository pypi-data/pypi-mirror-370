"""Configuration management commands for LitAI."""

import asyncio
from typing import Any

from rich.console import Console
from rich.theme import Theme

from litai.config import Config
from litai.llm import LLMClient
from litai.utils.confirmation import get_user_confirmation
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


def _handle_show_editors() -> None:
    """Show available editors on the system."""
    from litai.editor import EDITOR_CONFIGS, detect_available_editors

    available_editors = detect_available_editors()

    console.print("\n[bold]Available Editors:[/bold]")
    if not available_editors:
        console.print("[yellow]No supported editors found on this system[/yellow]")
        console.print("\nTo install a popular editor:")
        console.print("  • VS Code: https://code.visualstudio.com/")
        console.print("  • Vim: usually pre-installed on Unix systems")
        console.print("  • Nano: usually pre-installed on Unix systems")
        return

    # Group by type
    gui_editors = []
    terminal_editors = []

    for editor in available_editors:
        config = EDITOR_CONFIGS[editor]
        if config["type"] == "gui":
            gui_editors.append(editor)
        else:
            terminal_editors.append(editor)

    if gui_editors:
        console.print("\n[cyan]GUI Editors:[/cyan]")
        for editor in sorted(gui_editors):
            console.print(f"  • {editor}")

    if terminal_editors:
        console.print("\n[cyan]Terminal Editors:[/cyan]")
        for editor in sorted(terminal_editors):
            console.print(f"  • {editor}")

    console.print(f"\n[dim]Found {len(available_editors)} available editors[/dim]")
    console.print(
        "[dim]Use '/config set editor <name>' to configure your preferred editor[/dim]",
    )


def validate_model_name(model: str) -> bool:
    """Validate that a model name is reasonable.

    Args:
        model: Model name to validate

    Returns:
        True if valid, False otherwise
    """
    if not model or not model.strip():
        return False

    # Basic validation - model names should be alphanumeric with hyphens/dots
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._",
    )
    return all(c in allowed_chars for c in model) and len(model) <= 100


def handle_config_command(args: str, config: Config) -> None:
    """Handle /config commands with support for small/large models.

    Args:
        args: Command arguments
        config: Configuration instance
    """
    args_parts = args.strip().split(maxsplit=1)
    subcommand = args_parts[0] if args_parts else "show"

    if subcommand == "show":
        # Check for special show commands
        if len(args_parts) > 1 and args_parts[1].strip() == "editors":
            _handle_show_editors()
        else:
            _handle_config_show(config)
    elif subcommand == "set":
        if len(args_parts) < 2:
            _show_config_set_usage()
            return
        _handle_config_set(args_parts[1], config)
    elif subcommand == "reset":
        key = args_parts[1].strip() if len(args_parts) > 1 else None
        _handle_config_reset(key, config)
    else:
        console.print(f"[red]Unknown config subcommand: {subcommand}[/red]")
        console.print("Available subcommands:")
        console.print("  [cyan]show[/cyan] - Display current configuration")
        console.print("  [cyan]set <key> <value>[/cyan] - Set a configuration value")
        console.print(
            "  [cyan]reset [key][/cyan] - Reset all config or specific key to default",
        )


def _handle_config_show(config: Config) -> None:
    """Handle config show subcommand.

    Args:
        config: Configuration instance
    """
    config_data = config.load_config()
    if not config_data:
        console.print("\n[yellow]No configuration file found.[/yellow]")
        console.print("Using auto-detection based on environment variables.\n")

        # Show current runtime config
        try:
            temp_client = LLMClient(config)
            console.print("[bold]Current Runtime Configuration:[/bold]")
            console.print(f"  Provider: {temp_client.provider}")
            console.print(f"  Small Model: {config.get_small_model()}")
            console.print(f"  Large Model: {config.get_large_model()}")
            console.print(f"  Editor: {config.get_editor()}")
            console.print(f"  Vi Mode: {config.get_vi_mode()}")
            asyncio.run(temp_client.close())
        except Exception as e:
            console.print(f"[red]Error loading LLM client: {e}[/red]")
            console.print(f"  Small Model: {config.get_small_model()}")
            console.print(f"  Large Model: {config.get_large_model()}")
            console.print(f"  Editor: {config.get_editor()}")
            console.print(f"  Vi Mode: {config.get_vi_mode()}")
    else:
        console.print("\n[bold]Current Configuration:[/bold]")
        llm_config = config_data.get("llm", {})
        console.print(f"  Provider: {llm_config.get('provider', 'auto')}")

        # Show small and large models prominently
        small_model = config.get_small_model()
        large_model = config.get_large_model()
        console.print(f"  [primary]Small Model: {small_model}[/primary]")
        console.print(f"  [secondary]Large Model: {large_model}[/secondary]")

        if llm_config.get("api_key_env"):
            console.print(f"  API Key Env: {llm_config['api_key_env']}")
        console.print(f"  Editor: {config.get_editor()}")
        console.print(f"  Vi Mode: {config.get_vi_mode()}")

        # Show tool approval configuration
        tool_approval = config_data.get("tool_approval")
        if tool_approval is None:
            synthesis_config = config_data.get("synthesis", {})
            tool_approval = synthesis_config.get("tool_approval", True)
        console.print(f"  Tool Approval: {tool_approval}")

        # Show list columns configuration
        display_config = config_data.get("display", {})
        list_columns = display_config.get("list_columns", "")
        if list_columns:
            console.print(f"  List Columns: {list_columns}")
        else:
            console.print("  List Columns: [dim](using defaults)[/dim]")


def _show_config_set_usage() -> None:
    """Show usage information for config set command."""
    console.print("[red]Usage: /config set <key> <value>[/red]")
    console.print("\n[bold]Model Configuration:[/bold]")
    console.print("\n[cyan]Quick Setup (Uses GPT-5 by default):[/cyan]")
    console.print(
        "  /config set llm.provider openai         [dim]# Uses GPT-5 automatically[/dim]",
    )
    console.print("\n[cyan]Small/Large Model Configuration:[/cyan]")
    console.print(
        "  /config set llm.small_model gpt-5-nano  [dim]# Quick responses, low cost[/dim]",
    )
    console.print(
        "  /config set llm.small_model gpt-5-mini  [dim]# Balanced speed and quality[/dim]",
    )
    console.print(
        "  /config set llm.large_model gpt-5       [dim]# High quality, detailed responses[/dim]",
    )
    console.print("\n[dim]Before using, set your API key:[/dim]")
    console.print(
        "  [dim]export OPENAI_API_KEY=sk-...    # Get from platform.openai.com/api-keys[/dim]",
    )
    console.print("\n[bold]Other Settings:[/bold]")
    console.print(
        "  /config set editor vscode              [dim]# Use VS Code as editor[/dim]",
    )
    console.print(
        "  /config set editor vim                 [dim]# Use vim as editor[/dim]",
    )
    console.print(
        "  /config set editor.vi_mode true         [dim]# Enable vi keybindings[/dim]",
    )
    console.print(
        "  /config set editor.vi_mode false        [dim]# Use default keybindings[/dim]",
    )
    console.print("\n[bold]Tool Approval Configuration:[/bold]")
    console.print(
        "  /config set tool_approval true   [dim]# Enable tool approval prompts (all modes)[/dim]",
    )
    console.print(
        "  /config set tool_approval false  [dim]# Auto-approve all tools (all modes)[/dim]",
    )
    console.print("\n[bold]Display Configuration:[/bold]")
    console.print("  /config set display.list_columns no,title,authors,year,venue")
    console.print("  /config set display.list_columns title,tldr,tags,notes")
    console.print("\n[cyan]Available columns for list_columns:[/cyan]")
    console.print("  • [bold]no[/bold] - Paper number")
    console.print("  • [bold]title[/bold] - Paper title")
    console.print("  • [bold]authors[/bold] - Author names")
    console.print("  • [bold]year[/bold] - Publication year")
    console.print("  • [bold]citations[/bold] - Citation count")
    console.print("  • [bold]notes[/bold] - Whether paper has user notes (✓)")
    console.print("  • [bold]tags[/bold] - Paper tags")
    console.print("  • [bold]venue[/bold] - Publication venue")
    console.print("  • [bold]abstract[/bold] - Paper abstract (truncated)")
    console.print("  • [bold]tldr[/bold] - TL;DR summary")
    console.print("  • [bold]doi[/bold] - DOI identifier")
    console.print("  • [bold]arxiv_id[/bold] - ArXiv ID")
    console.print("  • [bold]citation_key[/bold] - BibTeX citation key")
    console.print("  • [bold]added_at[/bold] - Date added to collection")
    console.print(
        "\n[dim]Default columns: no,title,authors,year,citations,notes,tags,venue[/dim]",
    )
    console.print("[dim]Reset to default: /config reset display.list_columns[/dim]")


def _handle_config_set(key_value_str: str, config: Config) -> None:
    """Handle config set subcommand.

    Args:
        key_value_str: Key and value string to parse
        config: Configuration instance
    """
    key_value = key_value_str.split(maxsplit=1)
    if len(key_value) != 2:
        console.print("[red]Usage: /config set <key> <value>[/red]")
        return

    key, value = key_value

    # Validate key
    if not any(
        key.startswith(prefix)
        for prefix in ["llm.", "editor.", "display.", "synthesis."]
    ) and key not in ["tool_approval", "editor"]:
        console.print(f"[red]Invalid configuration key: {key}[/red]")
        console.print(
            "Supported keys: llm.provider, llm.small_model, llm.large_model, ",
        )
        console.print(
            "                llm.api_key_env, editor, editor.vi_mode, display.list_columns, tool_approval",
        )
        return

    # Validate provider
    if key == "llm.provider" and value not in ["openai", "anthropic", "auto"]:
        console.print(f"[red]Invalid provider: {value}[/red]")
        console.print("Supported providers: openai, anthropic, auto")
        return

    # Validate model names
    if key in [
        "llm.small_model",
        "llm.large_model",
    ] and not validate_model_name(value):
        console.print(f"[red]Invalid model name: {value}[/red]")
        console.print(
            "Model names should contain only alphanumeric characters, hyphens, dots, and underscores",
        )
        return

    # Validate editor
    if key == "editor":
        from litai.editor import validate_editor

        if not validate_editor(value):
            console.print(
                f"[red]Editor '{value}' is not supported or not available on this system[/red]",
            )
            console.print("Run '/config show editors' to see available editors")
            return

    # Validate and convert boolean values
    config_value: Any = value
    if key in ["editor.vi_mode", "tool_approval", "synthesis.tool_approval"]:
        if value.lower() in ["true", "yes", "1", "on"]:
            config_value = True
        elif value.lower() in ["false", "no", "0", "off"]:
            config_value = False
        else:
            console.print(f"[red]Invalid boolean value: {value}[/red]")
            console.print("Use: true, false, yes, no, 1, 0, on, or off")
            return

    # Special handling for small/large model configuration and editor
    try:
        if key == "llm.small_model":
            config.set_small_model(value)
            console.print(f"[green]Small model updated: {value}[/green]")
        elif key == "llm.large_model":
            config.set_large_model(value)
            console.print(f"[green]Large model updated: {value}[/green]")
        elif key == "editor":
            config.set_editor(value)
            console.print(f"[green]Editor updated: {value}[/green]")
        else:
            # Update configuration using generic method
            config.update_config(key, config_value)
            console.print(f"[green]Configuration updated: {key} = {value}[/green]")

        console.print(
            "\n[yellow]Note: Restart LitAI for changes to take effect.[/yellow]",
        )

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Failed to update configuration: {e}[/red]")
        logger.error("config_update_failed", key=key, value=value, error=str(e))


def _handle_config_reset(key: str | None, config: Config) -> None:
    """Handle config reset subcommand.

    Args:
        key: Optional specific key to reset, or None to reset all
        config: Configuration instance
    """
    if key:
        # Reset specific key
        defaults = {
            "display.list_columns": "no,title,authors,year,citations,notes,tags,venue",
            "llm.small_model": "gpt-5-nano",
            "llm.large_model": "gpt-5",
        }

        if key in defaults:
            if key == "llm.small_model":
                config.set_small_model(defaults[key])
                console.print(
                    f"[green]Reset small model to default: {defaults[key]}[/green]",
                )
            elif key == "llm.large_model":
                config.set_large_model(defaults[key])
                console.print(
                    f"[green]Reset large model to default: {defaults[key]}[/green]",
                )
            else:
                config.update_config(key, defaults[key])
                console.print(f"[green]Reset {key} to default: {defaults[key]}[/green]")
        elif key in [
            "llm.provider",
            "llm.api_key_env",
            "editor",
            "editor.vi_mode",
            "tool_approval",
        ]:
            # Remove these keys to use auto-detection/defaults
            config_data = config.load_config()
            if config_data:
                keys = key.split(".")
                if (
                    len(keys) == 2
                    and keys[0] in config_data
                    and keys[1] in config_data[keys[0]]
                ):
                    del config_data[keys[0]][keys[1]]
                    if not config_data[keys[0]]:  # Remove empty section
                        del config_data[keys[0]]
                    config.save_config(config_data)
                    console.print(f"[green]Reset {key} to default[/green]")
                elif len(keys) == 1 and key in config_data:
                    del config_data[key]
                    config.save_config(config_data)
                    console.print(f"[green]Reset {key} to default[/green]")
                else:
                    console.print(f"[yellow]Key {key} not currently set[/yellow]")
            else:
                console.print("[yellow]No configuration to reset[/yellow]")
        else:
            console.print(f"[red]Unknown configuration key: {key}[/red]")
            console.print(
                "Resettable keys: llm.provider, llm.small_model, llm.large_model, ",
            )
            console.print(
                "                 editor, editor.vi_mode, display.list_columns, tool_approval",
            )
    else:
        # Reset entire configuration
        config_path = config.config_path
        if config_path.exists():
            console.print(
                "[yellow]This will reset ALL configuration settings to defaults.[/yellow]",
            )
            if not get_user_confirmation(console, "Proceed with reset?", style="rich"):
                console.print("[red]Cancelled[/red]")
                return

            config_path.unlink()
            console.print("[green]Configuration reset to defaults.[/green]")
            console.print("Will use auto-detection based on environment variables.")
        else:
            console.print("[yellow]No configuration file to reset.[/yellow]")
