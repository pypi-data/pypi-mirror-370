"""Unified help system for all CLI commands."""
from rich.console import Console


class CommandHelp:
    """Builder class for consistent command help formatting."""
    
    def __init__(self, command_name: str, title: str | None = None):
        """Initialize CommandHelp builder.
        
        Args:
            command_name: The command name (e.g., "cadd")
            title: Optional custom title (defaults to "{Command} Command Help")
        """
        self.command_name = command_name
        self.title = title or f"{command_name.capitalize()} Command Help"
        self.usage_patterns = []
        self.description_lines = []
        self.arguments = []
        self.custom_sections = []  # For context-specific sections
        self.examples = []
        self.tips = []
    
    def usage(self, pattern: str) -> "CommandHelp":
        """Add a usage pattern."""
        self.usage_patterns.append(pattern)
        return self
    
    def description(self, *lines: str) -> "CommandHelp":
        """Add description lines."""
        self.description_lines.extend(lines)
        return self
    
    def argument(self, name: str, desc: str, is_flag: bool = False) -> "CommandHelp":
        """Add an argument or flag."""
        self.arguments.append((name, desc, is_flag))
        return self
    
    def section(self, title: str, items: list[tuple[str, str]], 
                style: str = "green") -> "CommandHelp":
        """Add a custom section (e.g., Context Types, Options)."""
        self.custom_sections.append((title, items, style))
        return self
    
    def example(self, command: str, comment: str = "") -> "CommandHelp":
        """Add an example with optional comment."""
        self.examples.append((command, comment))
        return self
    
    def tip(self, text: str) -> "CommandHelp":
        """Add a tip."""
        self.tips.append(text)
        return self
    
    def render(self) -> str:
        """Render the help text with Rich formatting."""
        lines = [""]  # Start with blank line
        
        # Title
        lines.append(f"[bold cyan]{self.title}[/bold cyan]")
        lines.append("")
        
        # Usage
        if self.usage_patterns:
            lines.append("[bold]Usage:[/bold]")
            for pattern in self.usage_patterns:
                lines.append(f"  {pattern}")
            lines.append("")
        
        # Description
        if self.description_lines:
            lines.append("[bold]Description:[/bold]")
            for line in self.description_lines:
                lines.append(f"  {line}")
            lines.append("")
        
        # Arguments
        if self.arguments:
            lines.append("[bold]Arguments:[/bold]")
            for name, desc, is_flag in self.arguments:
                formatted_name = f"[command]{name}[/command]"
                lines.append(f"  {formatted_name}  {desc}")
            lines.append("")
        
        # Custom sections
        for section_title, items, style in self.custom_sections:
            lines.append(f"[bold]{section_title}:[/bold]")
            for item_name, item_desc in items:
                if item_desc:  # If there's a description
                    formatted_name = f"[{style}]{item_name}[/{style}]"
                    # Calculate spacing for alignment
                    spacing = " " * (max(12, len(item_name) + 4) - len(item_name))
                    lines.append(f"  {formatted_name}{spacing}{item_desc}")
                else:  # For items without description (like bullet points)
                    lines.append(f"  {item_name}")
            lines.append("")
        
        # Examples
        if self.examples:
            lines.append("[bold]Examples:[/bold]")
            for cmd, comment in self.examples:
                formatted_cmd = f"[command]{cmd}[/command]"
                if comment:
                    # Align comments
                    padding = " " * max(1, 50 - len(cmd))
                    lines.append(f"  {formatted_cmd}{padding}# {comment}")
                else:
                    lines.append(f"  {formatted_cmd}")
            lines.append("")
        
        # Tips
        if self.tips:
            lines.append("[bold]Tips:[/bold]")
            for tip in self.tips:
                lines.append(f"  • {tip}")
            lines.append("")
        
        return "\n".join(lines)


class HelpRegistry:
    """Central registry for all command help."""
    
    def __init__(self):
        self._registry = {}
        self._initialize_help()
    
    def register(self, command: str, help_obj: CommandHelp) -> None:
        """Register a command's help."""
        self._registry[command] = help_obj
    
    def get(self, command: str) -> CommandHelp | None:
        """Get help for a command."""
        return self._registry.get(command)
    
    def show(self, command: str, console: Console) -> None:
        """Display help for a command."""
        help_obj = self.get(command)
        if help_obj:
            console.print(help_obj.render())
        else:
            console.print(f"[red]No help available for '{command}'[/red]")
    
    def _initialize_help(self):
        """Initialize all command help definitions."""
        # Context commands (already well-defined)
        self._init_context_commands()
        # Core commands
        self._init_core_commands()
        # Collection commands
        self._init_collection_commands()
        # System commands
        self._init_system_commands()
    
    def _init_context_commands(self):
        """Initialize help for context commands."""
        # /cadd - The gold standard
        self.register("cadd", CommandHelp("cadd", "Context Add Command Help")
            .usage("/cadd")
            .usage("/cadd <paper reference> [context_type]")
            .usage("/cadd --tag <tag_name> [context_type]")
            .description(
                "Add papers to your working context for synthesis.",
                "Papers in context are used by /synthesize for analysis.",
                "Can add all papers, individual papers, or papers with a specific tag.",
            )
            .argument("(empty)", "Add all papers from collection as full-text")
            .argument("paper reference", "Paper number from /collection or natural language reference")
            .argument("--tag <tag_name>", "Add all papers with the specified tag", is_flag=True)
            .argument("context_type", "Type of content to add (default: full-text for all cases)")
            .section("Context Types", [
                ("full-text", "Complete paper content (most detailed)"),
                ("abstract", "Just the abstract (fastest)"),
                ("notes", "Your personal notes on the paper"),
            ])
            .example("/cadd", "Add all papers from collection as full-text")
            .example("/cadd 1", "Add paper 1 with full text")
            .example("/cadd 3 abstract", "Add paper 3's abstract only")
            .example('/cadd "BERT paper" notes', "Add BERT paper's notes")
            .example("/cadd --tag inference", "Add all inference papers as full-text")
            .example("/cadd --tag GPT full-text", "Add all GPT papers with full text")
            .example("/cadd --tag theory_lm notes", "Add all theory_lm papers with notes")
            .tip("Use /cshow to see papers currently in context")
            .tip("Each paper has ONE context type at a time (replaces existing)")
            .tip("Natural language references are matched using AI")
            .tip("Use /tags to see available tags and paper counts"),
        )
        
        # /cremove
        self.register("cremove", CommandHelp("cremove", "Context Remove Command Help")
            .usage("/cremove <paper reference>")
            .usage("/cremove --tag <tag_name>")
            .description(
                "Remove papers from your working context.",
                "Can remove individual papers or all papers with a specific tag.",
            )
            .argument("paper reference", "Paper number from /collection or natural language reference")
            .argument("--tag <tag_name>", "Remove all papers with the specified tag", is_flag=True)
            .example("/cremove 1", "Remove paper 1 from context")
            .example('/cremove "BERT paper"', "Remove BERT paper from context")
            .example("/cremove --tag inference", "Remove all inference papers")
            .example("/cremove --tag GPT", "Remove all GPT papers")
            .tip("Use /cshow to see what's in context first")
            .tip("Use /cclear to remove all papers at once")
            .tip("Only removes papers that are actually in context"),
        )
        
        # /cshow
        self.register("cshow", CommandHelp("cshow", "Context Show Command Help")
            .usage("/cshow")
            .description(
                "Display all papers currently in your working context.",
                "Shows which context types are loaded for each paper.",
            )
            .section("Output", [
                ("Table showing:", ""),
                ("• Paper titles", ""),
                ("• Context type loaded (full_text, abstract, or notes)", ""),
                ("• Total paper count", ""),
            ], style="dim")
            .example("/cshow", "Display current context")
            .tip("Empty context shows helpful message")
            .tip("Use before /synthesize to verify context")
            .tip("Context persists across synthesis sessions"),
        )
        
        # /cclear
        self.register("cclear", CommandHelp("cclear", "Context Clear Command Help")
            .usage("/cclear")
            .description(
                "Clear all papers from your working context.",
                "Useful for starting fresh synthesis sessions.",
            )
            .example("/cclear", "Remove all papers from context")
            .tip("Use /cshow first to see what will be cleared")
            .tip("Context is not permanently deleted, just cleared")
            .tip("Papers remain in your collection (/collection)"),
        )
        
        # /cmodify
        self.register("cmodify", CommandHelp("cmodify", "Context Modify Command Help")
            .usage("/cmodify <new_type>")
            .usage("/cmodify <paper reference> <new_type>")
            .usage("/cmodify --tag <tag_name> <new_type>")
            .description(
                "Change the context type for papers.",
                "Useful for switching between detail levels.",
                "Can modify all papers, individual papers, or papers with a specific tag.",
            )
            .argument("new_type", "Context type alone modifies ALL papers in context")
            .argument("paper reference", "Paper number or natural language reference")
            .argument("--tag <tag_name>", "Modify all papers with the specified tag", is_flag=True)
            .section("Context Types", [
                ("full_text or full-text", "Complete paper content"),
                ("abstract", "Just the abstract"),
                ("notes", "Your personal notes"),
            ])
            .example("/cmodify full-text", "Switch ALL papers to full-text")
            .example("/cmodify abstract", "Switch ALL papers to abstract")
            .example("/cmodify notes", "Switch ALL papers to notes")
            .example("/cmodify 1 abstract", "Switch paper 1 to abstract")
            .example('/cmodify "BERT" notes', "Switch BERT to notes")
            .example("/cmodify --tag inference full-text", "Switch all inference papers to full-text")
            .example("/cmodify --tag GPT abstract", "Switch all GPT papers to abstract")
            .tip("Single context type argument modifies ALL papers")
            .tip("Use /cshow to see current context types")
            .tip("Both full_text and full-text are accepted")
            .tip("Only modifies papers that are in context"),
        )
    
    def _init_core_commands(self):
        """Initialize help for core commands."""
        # /find
        self.register("find", CommandHelp("find", "Find Command Help")
            .usage("/find <search query>")
            .usage("/find <query> --append")
            .usage("/find --recent")
            .usage("/find --clear")
            .description(
                "Search for academic papers using Semantic Scholar.",
                "Results are cached and can be added to your collection.",
            )
            .argument("query", "Search terms to find relevant papers")
            .section("Flags", [
                ("--append", "Add results to existing search results"),
                ("--recent", "Show cached search results"),
                ("--clear", "Clear all cached search results"),
                ("--help", "Show this help message"),
            ])
            .example("/find transformers", "Search for transformer papers")
            .example('/find "attention is all you need"', "Search exact phrase")
            .example("/find GAN --append", "Add GAN papers to existing results")
            .example("/find --recent", "View your recent search results")
            .tip("Natural language queries support bulk search (e.g., 'find transformers, flash attention, and distributed training')")
            .tip("Use quotes for exact phrase matching")
            .tip("To build on existing results, use --append for each subsequent search")
            .tip("Results are numbered for easy addition with /add")
            .tip("Maximum 100 papers can be cached at once"),
        )
        
        # /add
        self.register("add", CommandHelp("add", "Add Command Help")
            .usage("/add <paper numbers>")
            .usage("/add <range>")
            .description(
                "Add papers from search results to your collection.",
                "Papers must be found with /find first.",
            )
            .argument("paper numbers", "Space-separated numbers from search results")
            .argument("range", "Range of papers (e.g., 1-5)")
            .argument("--all", "Add all papers from search results", is_flag=True)
            .example("/add 1 3 5", "Add papers 1, 3, and 5")
            .example("/add 1-10", "Add papers 1 through 10")
            .example("/add ", "Add all search results")
            .tip("Use /find first to search for papers")
            .tip("View your collection with /collection")
            .tip("Papers are deduplicated automatically"),
        )
        
        # /collection
        self.register("collection", CommandHelp("collection", "Collection Command Help")
            .usage("/collection [page_number]")
            .usage("/collection --tags")
            .usage("/collection --notes")
            .usage("/collection --tag <name>")
            .description(
                "List and manage papers in your collection with various filters.",
                "Shows all papers you've added from searches.",
            )
            .argument("page_number", "Page number for pagination (default: 1)")
            .argument("--tags", "Show all tags with paper counts", is_flag=True)
            .argument("--notes", "Show papers that have notes", is_flag=True)
            .argument("--tag <name>", "Filter papers by specific tag", is_flag=True)
            .argument("--help", "Show this help message", is_flag=True)
            .example("/collection", "List first page of papers")
            .example("/collection 2", "Show page 2 of papers")
            .example("/collection --tags", "Show all tags")
            .example("/collection --notes", "Show papers with notes")
            .example("/collection --tag inference", "Show papers tagged 'inference'")
            .tip("Papers are numbered for easy reference")
            .tip("Use /remove to delete papers")
            .tip("Use /tag to organize papers"),
        )
        
        # /synthesize
        self.register("synthesize", CommandHelp("synthesize", "Synthesize Command Help")
            .usage("/synthesize <question>")
            .usage("/synthesize --examples")
            .usage("/synthesize --help")
            .description(
                "Synthesize insights from papers in your context.",
                "Uses papers added with /cadd to generate analysis.",
            )
            .argument("question", "Ask a synthesis question")
            .argument("--examples", "Show example synthesis questions", is_flag=True)
            .argument("--help", "Show this help message", is_flag=True)
            .section("Usage Notes", [
                ("• First add papers to context with /cadd", ""),
                ("• Then ask synthesis questions about them", ""),
                ("• Use --examples to see common research questions", ""),
            ], style="dim")
            .example("/synthesize How do these models handle context?", "Ask synthesis question")
            .example("/synthesize --examples", "Show example questions")
            .tip("Add papers to context first with /cadd")
            .tip("Use /cshow to verify context before synthesis")
            .tip("More papers in context = more comprehensive analysis"),
        )
    
    def _init_collection_commands(self):
        """Initialize help for collection management commands."""
        # /remove
        self.register("remove", CommandHelp("remove", "Remove Command Help")
            .usage("/remove <paper numbers>")
            .usage("/remove <range>")
            .usage("/remove --tag <tag_name>")
            .description(
                "Remove papers from your collection.",
                "Permanently deletes papers and their notes.",
            )
            .argument("paper numbers", "Space-separated numbers from /collection")
            .argument("range", "Range of papers (e.g., 1-5)")
            .argument("--tag <tag_name>", "Remove all papers with specified tag", is_flag=True)
            .example("/remove 1 3 5", "Remove papers 1, 3, and 5")
            .example("/remove 10-15", "Remove papers 10 through 15")
            .example("/remove --tag old", "Remove all papers tagged 'old'")
            .tip("Use /collection first to see paper numbers")
            .tip("Removal is permanent - notes are also deleted")
            .tip("Papers in context are also removed"),
        )
        
        # /note
        self.register("note", CommandHelp("note", "Note Command Help")
            .usage("/note <paper reference>")
            .usage("/note <paper reference> view")
            .usage("/note <paper reference> append <text>")
            .usage("/note <paper reference> clear")
            .description(
                "Manage personal notes for papers.",
                "Opens editor for detailed note-taking or performs note operations.",
            )
            .argument("paper reference", "Paper number or fuzzy paper reference (in quotes)")
            .argument("view", "Display note in terminal")
            .argument("append <text>", "Append text to existing note")
            .argument("clear", "Delete note (asks for confirmation)")
            .example("/note 1", "Open note for paper 1 in your editor")
            .example('/note "attention is all"', "Open note using fuzzy paper reference")
            .example("/note 1 view", "Display note in terminal")
            .example('/note 1 append "TODO: Implement algorithm from section 3"', "Append to note")
            .example("/note 1 clear", "Delete note (asks for confirmation)")
            .tip("Notes are written in Markdown format")
            .tip("Set your preferred editor with /config set editor <name> (see /config --help)")
            .tip("Use /collection --notes to see all papers with notes"),
        )
        
        # /tag
        self.register("tag", CommandHelp("tag", "Tag Command Help")
            .usage("/tag <paper reference>")
            .usage("/tag <paper reference> -a <tags>")
            .usage("/tag <paper reference> -r <tags>")
            .usage("/tag <paper reference> -l")
            .description(
                "Manage tags for papers in your collection.",
                "Tags help organize and batch-process papers.",
                "Supports ranges and multiple papers like /add command.",
            )
            .argument("paper reference", "Paper number(s), ranges, or natural language reference (in quotes)")
            .argument("-a <tags>", "Add tags (comma-separated)", is_flag=True)
            .argument("-r <tags>", "Remove tags (comma-separated)", is_flag=True)
            .argument("-l", "List tags for paper(s)", is_flag=True)
            .example("/tag 1 -a ml,deep-learning", "Add tags to paper 1")
            .example("/tag 1,3,5 -a review", "Add tag to papers 1, 3, and 5")
            .example("/tag 1-5 -a important", "Add tag to papers 1 through 5")
            .example("/tag 2-10,15 -a needs-review", "Add tag to papers 2-10 and 15")
            .example('/tag "attention paper" -a transformers', "Add tag using fuzzy paper reference")
            .example("/tag 2 -r outdated", "Remove tag from paper 2")
            .example("/tag 1-3 -r draft", "Remove tag from papers 1-3")
            .example('/tag "BERT paper" -r old', "Remove tag using fuzzy paper reference")
            .example("/tag 3 -l", "List tags for paper 3")
            .example("/tag 1-5 -l", "List tags for papers 1-5")
            .example("/tag 1", "View tags for paper 1")
            .example('/tag "transformer paper"', "View tags using paper reference")
            .tip("Use paper numbers, ranges (1-5), or comma-separated lists (1,3,5)")
            .tip("Tags help organize your collection")
            .tip("Use /collection --tags to see all tags")
            .tip("Tags are case-insensitive and normalized"),
        )
        
        # /import
        self.register("import", CommandHelp("import", "Import Command Help")
            .usage("/import <file_path>")
            .description(
                "Import papers from BibTeX files.",
                "Currently supports BibTeX format only.",
            )
            .argument("file_path", "Path to BibTeX file (.bib)")
            .section("Supported Format", [
                ("bibtex", "BibTeX bibliography files (.bib)"),
            ])
            .example("/import papers.bib", "Import BibTeX file")
            .example("/import references.bib", "Import another BibTeX file")
            .tip("Only .bib files are currently supported")
            .tip("Duplicates are skipped automatically")
            .tip("Large imports may take time to process"),
        )
        
        # /tags
        self.register("tags", CommandHelp("tags", "Tags Command Help")
            .usage("/tags")
            .description(
                "View all tags and their paper counts.",
                "Shows overview of your tag organization.",
            )
            .example("/tags", "List all tags with counts")
            .tip("Use tags to organize papers by topic")
            .tip("Tags enable batch context operations")
            .tip("Empty tags are not shown"),
        )
        
    
    def _init_system_commands(self):
        """Initialize help for system commands."""
        # /config
        self.register("config", CommandHelp("config", "Configuration Management")
            .usage("/config")
            .usage("/config show")
            .usage("/config set <key> <value>")
            .usage("/config reset [key]")
            .usage("/config show editors")
            .description(
                "Manage LitAI settings including model configuration and preferences.",
                "Controls LLM models, editor settings, display options, and tool behavior.",
            )
            .argument("key", "Configuration key to set")
            .argument("value", "New value for the key")
            .argument("--help", "Show this help message", is_flag=True)
            .section("Model Configuration", [
                ("Quick Setup", ""),
                ("  llm.provider openai", "Uses GPT-5 automatically"),
                ("", ""),
                ("Small/Large Models", ""),
                ("  llm.small_model gpt-5-nano", "Fast model for quick tasks"),
                ("  llm.large_model gpt-5", "Powerful model for complex tasks"),
            ])
            .section("Display Settings", [
                ("display.list_columns", "Customize paper list columns"),
                ("", ""),
                ("Available columns", ""),
                ("  • no, title, authors, year", ""),
                ("  • citations, notes, tags, venue", ""),
                ("  • abstract, tldr, doi, arxiv_id", ""),
                ("  • citation_key, added_at", ""),
                ("", ""),
                ("Default columns", ""),
                ("  no,title,authors,year,citations,notes,tags,venue", ""),
            ])
            .section("Tool Approval Settings", [
                ("tool_approval true", "Enable tool approval prompts"),
                ("tool_approval false", "Auto-approve all tools"),
            ])
            .section("Editor Settings", [
                ("editor vscode", "Use VS Code as editor"),
                ("editor vim", "Use vim as editor"),
                ("editor.vi_mode true", "Enable vi keybindings in litai cli"),
                ("editor.vi_mode false", "Use default keybindings"),
                ("show editors", "Show available editors on system"),
            ])
            .example("/config", "Show current configuration")
            .example("/config set llm.provider openai", "Set provider to OpenAI")
            .example("/config set llm.small_model gpt-5-nano", "Set small model")
            .example("/config set llm.large_model gpt-5", "Set large model")
            .example("/config set display.list_columns title,authors,tags,notes", "Customize columns")
            .example("/config reset display.list_columns", "Reset columns to default")
            .example("/config reset", "Reset all configuration")
            .example("/config show editors", "Show available editors")
            .tip("Set your OpenAI API key: export OPENAI_API_KEY=sk-...")
            .tip("Get API key from platform.openai.com/api-keys")
            .tip("After changing model, restart LitAI for changes to take effect")
            .tip("Use /config show to verify current settings"),
        )
        
        # /tokens
        self.register("tokens", CommandHelp("tokens", "Tokens Command Help")
            .usage("/tokens")
            .usage("/tokens --reset")
            .usage("/tokens --detailed")
            .description(
                "View token usage statistics.",
                "Tracks API usage and costs.",
            )
            .section("Flags", [
                ("--reset", "Reset token counters"),
                ("--detailed", "Show breakdown by operation"),
                ("--help", "Show this help message"),
            ])
            .example("/tokens", "View current usage")
            .example("/tokens --detailed", "View detailed breakdown")
            .example("/tokens --reset", "Reset counters")
            .tip("Tokens are counted per API call")
            .tip("Costs are estimated based on model pricing")
            .tip("Use /config to change model for cost control"),
        )
        
        # /prompt
        self.register("prompt", CommandHelp("prompt", "Prompt Command Help")
            .usage("/prompt")
            .usage("/prompt view")
            .usage("/prompt append <text>")
            .usage("/prompt clear")
            .description(
                "Manage your system prompt.",
                "Customize how LitAI understands your needs.",
            )
            .argument("view", "Display your current system prompt")
            .argument("append <text>", "Add text to your system prompt")
            .argument("clear", "Delete your system prompt (asks for confirmation)")
            .section("Your system prompt helps LitAI", [
                ("• Understand your expertise level", ""),
                ("• Focus on relevant aspects of papers", ""),
                ("• Tailor synthesis to your interests", ""),
                ("• Remember your preferences", ""),
            ], style="dim")
            .example("/prompt", "Edit your system prompt (opens in editor)")
            .example("/prompt view", "Display your current system prompt")
            .example('/prompt append "Also interested in hardware-aware NAS"', "Add to prompt")
            .example("/prompt clear", "Delete your system prompt")
            .tip("Set your preferred editor with /config set editor <name> (see /config --help)")
            .tip("System prompts are stored as plain text")
            .tip("Changes persist across sessions"),
        )
        
        # /clear
        self.register("clear", CommandHelp("clear", "Clear Command Help")
            .usage("/clear")
            .usage("/clear search")
            .usage("/clear context")
            .usage("/clear all")
            .description(
                "Clear various data or the terminal screen.",
                "Remove search results, context, or clean display.",
            )
            .argument("search", "Clear cached search results")
            .argument("context", "Clear synthesis context (same as /cclear)")
            .argument("all", "Clear both search and context")
            .example("/clear", "Clear the terminal screen")
            .example("/clear search", "Clear search results")
            .example("/clear context", "Clear synthesis context")
            .example("/clear all", "Clear everything")
            .tip("Without arguments, clears terminal screen")
            .tip("Does not affect your paper collection")
            .tip("Keyboard shortcut for screen clear: Ctrl+L"),
        )
        
        # /help
        self.register("help", CommandHelp("help", "Help Command Help")
            .usage("/help")
            .usage("/help <command>")
            .description(
                "Show help for commands.",
                "Get detailed information about any command.",
            )
            .argument("command", "Specific command to get help for")
            .example("/help", "Show all commands")
            .example("/help find", "Show help for /find")
            .example("/help synthesize", "Show help for /synthesize")
            .tip("All commands support --help flag")
            .tip("Use Tab for command completion"),
        )


# Create singleton instance
help_registry = HelpRegistry()
