"""Natural language handler for LitAI."""

import json
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.table import Table

from litai.config import Config
from litai.context_manager import SessionContext
from litai.conversation import ConversationManager
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.output_formatter import OutputFormatter
from litai.paper_resolver import resolve_paper_references
from litai.token_tracker import TokenTracker
from litai.tool_approval import ToolApprovalManager, ToolCall
from litai.tools import get_anthropic_tools, get_openai_tools
from litai.ui.status_manager import get_status_manager
from litai.utils.log_context import operation_context
from litai.utils.log_events import Events
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()
output = OutputFormatter(console)


class NaturalLanguageHandler:
    """Handles natural language queries and tool execution."""

    def __init__(
        self,
        db: Database,
        command_handlers: dict[str, Callable],
        search_results_ref: list[Paper],
        config: Config,
        session_context: SessionContext,
        token_tracker: TokenTracker | None = None,
    ):
        """Initialize the natural language handler.

        Args:
            db: Database instance
            command_handlers: Dictionary mapping tool names to handler functions
            search_results_ref: Reference to the global search results list
            config: Configuration instance
            session_context: SessionContext instance for managing paper context
            token_tracker: Optional shared TokenTracker instance
        """
        self.db = db
        self.config = config
        self.llm_client = LLMClient(config, token_tracker=token_tracker)
        self.conversation = ConversationManager(config)
        self.command_handlers = command_handlers
        self.search_results_ref = search_results_ref
        self.status_manager = get_status_manager()
        self.approval_manager = ToolApprovalManager(
            config, status_manager=self.status_manager,
        )
        self.session_context = session_context

    def reset_conversation(self) -> None:
        """Reset the conversation history to start fresh."""
        self.conversation.reset()
        logger.info("conversation_reset")

    async def close(self) -> None:
        """Close the handler and cleanup resources."""
        await self.llm_client.close()

    async def handle_query(self, query: str) -> None:
        """Handle a natural language query.

        Args:
            query: The user's natural language query
        """
        await logger.ainfo("nl_query_start", query=query)

        # Start loading animation immediately for user feedback
        self.status_manager.start("[yellow]Processing query...[/yellow]")

        try:
            # Check if this is a context management query using LLM
            self.status_manager.update("[yellow]Analyzing request...[/yellow]")
            is_context_query = await self._classify_context_query(query)

            if is_context_query:
                await self._handle_context_query(query)
                return

            # Normal ReAct pipeline (existing code)
            # NEW: Resolve paper references first
            self.status_manager.update("[yellow]Resolving references...[/yellow]")
            resolved_query, paper_id = await resolve_paper_references(
                query, self.db, self.llm_client,
            )

            # Show what was resolved to user (if anything changed)
            if paper_id:
                paper = self.db.get_paper(paper_id)
                if paper:
                    console.print(f"[dim]Resolved to: {paper.title}[/dim]")

            # Inject paper collection info on first user query (after system message)
            # This gives the model awareness of what papers are available
            if len(self.conversation.messages) == 1:  # Only system message exists
                papers = self.db.list_papers(limit=100)  # Get all papers
                if papers:
                    paper_context = "\n<beginning_collection>\n"
                    paper_context += f"Current paper collection contains {len(papers)} papers: "
                    # Show papers with semicolon separation for token efficiency
                    paper_list = [f"{p.title} ({p.year})" for p in papers[:100]]
                    paper_context += "; ".join(paper_list)
                    if len(papers) > 100:
                        paper_context += f"; ... and {len(papers) - 100} more papers"
                    paper_context += "\n</beginning_collection>\n\n"
                    resolved_query = paper_context + resolved_query
                    await logger.ainfo(
                        "injected_paper_collection", paper_count=len(papers),
                    )

            # Inject context count on every message
            context_papers = self.session_context.get_all_papers()
            if context_papers:
                context_info = f"\n<context_status>{len(context_papers)} papers in context</context_status>\n"
                resolved_query = context_info + resolved_query

            # Use resolved query for LLM
            self.conversation.add_message("user", resolved_query)
            # Get appropriate tools for the provider
            if self.llm_client.provider == "openai":
                tools = get_openai_tools()
            else:
                tools = get_anthropic_tools()

            # Get LLM response with tools
            provider = self.llm_client.provider or "openai"  # Default to openai if None
            messages = self.conversation.get_messages_for_llm(provider)

            # Update status message since we're now thinking
            self.status_manager.update("[yellow]Thinking...[/yellow]")

            with operation_context(
                "llm_query_processing", provider=provider, tools_count=len(tools),
            ):
                response = await self.llm_client.complete(
                    messages,
                    tools=tools,
                    temperature=0.0,
                    model_size="small",
                    operation_type="query_processing",
                )

            # Handle the response
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])

            # If there are tool calls, execute them
            if tool_calls:
                # Convert to ToolCall objects for approval
                pending_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.name,
                        description=self._get_tool_description(tc.name, tc.arguments),
                        arguments=tc.arguments,
                    )
                    for tc in tool_calls
                ]

                # Get user approval for tool calls
                approved_calls = await self.approval_manager.get_approval(pending_calls)

                # If no tools approved, explain to user
                if not approved_calls:
                    console.print("[yellow]Tool execution cancelled by user.[/yellow]")
                    return

                # Add assistant message with approved tool calls
                self.conversation.add_message(
                    "assistant",
                    content,
                    tool_calls=[
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": tc.arguments,
                        }
                        for tc in approved_calls
                    ],
                )

                # Execute approved tools and get results
                with operation_context(
                    "tool_execution", tools_count=len(approved_calls),
                ):
                    tool_results = await self._execute_tools(approved_calls)

                # Add tool results to conversation
                self.conversation.add_message(
                    "tool",
                    "",
                    tool_results=tool_results,
                )

                # Get final response from LLM
                provider = (
                    self.llm_client.provider or "openai"
                )  # Default to openai if None
                messages = self.conversation.get_messages_for_llm(provider)

                self.status_manager.update("[yellow]Processing results...[/yellow]")
                with operation_context("llm_final_response", provider=provider):
                    final_response = await self.llm_client.complete(
                        messages,
                        temperature=0.0,
                        model_size="small",
                        operation_type="query_processing",
                    )

                final_content = final_response.get("content", "")
                self.conversation.add_message("assistant", final_content)

                # Display the response
                if final_content:
                    output.ai_response(final_content)
            else:
                # Just display the content
                self.conversation.add_message("assistant", content)
                if content:
                    output.ai_response(content)

            await logger.ainfo(
                "nl_query_success", query=query, tool_count=len(tool_calls),
            )

        except Exception as e:
            await logger.aexception("Natural language query failed", query=query)
            output.error(f"Error processing query: {e}")
        finally:
            # Always stop the status manager on error or completion
            self.status_manager.stop()

    async def _execute_tools(self, tool_calls: list[ToolCall]) -> list[dict[str, Any]]:
        """Execute tool calls and return results.

        Args:
            tool_calls: List of approved ToolCall objects to execute

        Returns:
            List of tool results
        """
        results = []

        for tool_call in tool_calls:
            try:
                # Execute the tool (already approved)
                result = await self._execute_single_tool(
                    tool_call.name,
                    tool_call.arguments,
                )

                results.append(
                    {
                        "tool_call_id": tool_call.id,
                        "content": result,
                    },
                )

            except Exception as e:
                await logger.aexception(
                    "Tool execution failed",
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                )
                results.append(
                    {
                        "tool_call_id": tool_call.id,
                        "content": f"Error executing {tool_call.name}: {str(e)}",
                    },
                )

        return results

    async def _execute_single_tool(
        self, tool_name: str, arguments: dict[str, Any],
    ) -> str:
        """Execute a single tool using the provided command handlers.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool

        Returns:
            String result of the tool execution
        """
        with operation_context("single_tool_execution", tool_name=tool_name):
            await logger.ainfo(
                Events.TOOL_EXECUTED, tool_name=tool_name, arguments=arguments,
            )

        # Map tool names to command handlers
        if tool_name == "find_papers":
            handler = self.command_handlers.get("find_papers")
            if handler:
                query = arguments.get("query", "")
                append = arguments.get("append", False)
                result = await handler(query, append=append)
                return str(result)

        elif tool_name == "add_paper":
            handler = self.command_handlers.get("add_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper add operation completed."

        elif tool_name == "list_papers":
            handler = self.command_handlers.get("list_papers")
            if handler:
                page = arguments.get("page", 1)
                result = handler(self.db, page)
                return str(result)

        elif tool_name == "remove_paper":
            handler = self.command_handlers.get("remove_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper remove operation completed."

        elif tool_name == "show_search_results":
            handler = self.command_handlers.get("show_search_results")
            if handler:
                handler()
                return "Search results displayed."

        elif tool_name == "clear_screen":
            console.clear()
            return "Screen cleared."

        elif tool_name == "manage_paper_tags":
            paper_number = arguments.get("paper_number", 0)
            add_tags = arguments.get("add_tags", "")
            remove_tags = arguments.get("remove_tags", "")

            # Build the command string
            if add_tags:
                handler = self.command_handlers.get("handle_tag_command")
                if handler:
                    handler(f"{paper_number} -a {add_tags}", self.db)
                    return f"Added tags to paper {paper_number}."
            elif remove_tags:
                handler = self.command_handlers.get("handle_tag_command")
                if handler:
                    handler(f"{paper_number} -r {remove_tags}", self.db)
                    return f"Removed tags from paper {paper_number}."
            else:
                # Just list tags for the paper
                handler = self.command_handlers.get("handle_tag_command")
                if handler:
                    handler(str(paper_number), self.db)
                    return f"Listed tags for paper {paper_number}."

        elif tool_name == "list_all_tags":
            handler = self.command_handlers.get("list_tags")
            if handler:
                handler(self.db)
                return "Listed all tags."

        elif tool_name == "list_papers_by_tag":
            tag = arguments.get("tag", "")
            page = arguments.get("page", 1)
            handler = self.command_handlers.get("list_papers")
            if handler:
                result = handler(self.db, page, tag)
                return str(result)

        elif tool_name == "papers_command":
            # Handle the papers_command tool
            page = arguments.get("page", 1)
            show_tags = arguments.get("show_tags", False)
            show_notes = arguments.get("show_notes", False)
            tag_filter = arguments.get("tag_filter")

            if show_tags:
                handler = self.command_handlers.get("list_tags")
                if handler:
                    handler(self.db)
                    return "Listed all tags."
            elif show_notes:
                # List papers with notes
                handler = self.command_handlers.get("list_papers")
                if handler:
                    # TODO: Add support for filtering by notes
                    result = handler(self.db, page)
                    return str(result)
            else:
                # Regular list papers, optionally filtered by tag
                handler = self.command_handlers.get("list_papers")
                if handler:
                    result = handler(self.db, page, tag_filter)
                    return str(result)

        elif tool_name == "synthesize":
            query = arguments.get("query", "")
            if not query:
                return "Error: query parameter is required for synthesis"

            handler = self.command_handlers.get("handle_synthesize")
            if handler:
                # Get sharded parameter from arguments (LLM will set based on tool description)
                sharded = arguments.get("sharded", False)
                
                # Call the unified command handler
                # It expects: args, db, session_context, config, token_tracker, sharded
                handler(
                    query,
                    self.db,
                    self.session_context,
                    self.config,
                    self.llm_client.token_tracker,
                    sharded=sharded,
                )
                # The command handler prints directly and doesn't return a value
                mode_msg = " (using sharded mode)" if sharded else ""
                return f"Synthesis completed successfully{mode_msg}."
            return "Error: Synthesis handler not available"

        elif tool_name == "context_show":
            # Show current context using the context_show handler
            handler = self.command_handlers.get("handle_context_show")
            if handler:
                result = handler(self.session_context)
                if result == "":
                    return "Context displayed successfully."
                return result
            return "Error: Context show handler not available"

        elif tool_name == "note":
            # Handle note operations (view or append)
            handler = self.command_handlers.get("handle_note")
            if handler:
                paper_id = arguments.get("paper_id")
                operation = arguments.get("operation")
                content = arguments.get("content")
                
                # Convert paper_id to paper_number for the handler
                papers = self.db.list_papers()
                paper_number = None
                for i, paper in enumerate(papers):
                    if paper.paper_id == paper_id:
                        paper_number = i + 1  # 1-indexed
                        break
                
                if paper_number is None:
                    return f"Paper with ID '{paper_id}' not found in collection"
                
                return await handler(paper_number, operation, content, self.db)
            return "Error: Note handler not available"

        elif tool_name == "prompt":
            # Handle user prompt operations (view or append)
            handler = self.command_handlers.get("handle_user_prompt")
            if handler:
                operation = arguments.get("operation")
                content = arguments.get("content")
                return await handler(operation, content, self.config)
            return "Error: User prompt handler not available"

        else:
            return f"Unknown tool: {tool_name}"

        # Should not reach here, but adding for completeness
        return f"Tool {tool_name} not executed"

    def _get_tool_description(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Get a human-readable description of what a tool will do.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Human-readable description
        """
        if tool_name == "find_papers":
            query = arguments.get("query", "")
            append = arguments.get("append", False)
            return f"{'Append' if append else 'Search for'} papers matching: {query}"
        if tool_name == "add_paper":
            numbers = arguments.get("paper_numbers", "")
            return f"Add paper(s) {numbers} to your collection"
        if tool_name == "list_papers":
            page = arguments.get("page", 1)
            return f"List papers in your collection (page {page})"
        if tool_name == "remove_paper":
            numbers = arguments.get("paper_numbers", "")
            return f"Remove paper(s) {numbers} from your collection"
        if tool_name == "show_search_results":
            return "Display recent search results"
        if tool_name == "clear_screen":
            return "Clear the terminal screen"
        if tool_name == "manage_paper_tags":
            paper_num = arguments.get("paper_number", 0)
            add_tags = arguments.get("add_tags", "")
            remove_tags = arguments.get("remove_tags", "")
            if add_tags:
                return f"Add tags '{add_tags}' to paper {paper_num}"
            if remove_tags:
                return f"Remove tags '{remove_tags}' from paper {paper_num}"
            return f"List tags for paper {paper_num}"
        if tool_name == "papers_command":
            page = arguments.get("page", 1)
            show_tags = arguments.get("show_tags", False)
            show_notes = arguments.get("show_notes", False)
            if show_tags:
                return "Show all tags in the database"
            if show_notes:
                return "Show papers with notes"
            return f"List papers in your collection (page {page})"
        if tool_name == "synthesize":
            query = arguments.get("query", "")
            return f"Synthesize insights from papers in context for: {query}"
        if tool_name == "context_show":
            return "Display papers currently in context for synthesis"
        if tool_name == "note":
            paper_num = arguments.get("paper_number", 0)
            operation = arguments.get("operation", "")
            if operation == "view":
                return f"View notes for paper {paper_num}"
            if operation == "append":
                return f"Append text to notes for paper {paper_num}"
            return f"Perform note operation on paper {paper_num}"
        if tool_name == "prompt":
            operation = arguments.get("operation", "")
            if operation == "view":
                return "View your system prompt"
            if operation == "append":
                return "Add to your system prompt"
            return "Manage your system prompt"
        return f"Execute {tool_name} with provided parameters"

    async def _classify_context_query(self, query: str) -> bool:
        """Use LLM to classify if query is about context management.

        Args:
            query: The user's query to classify

        Returns:
            True if this is a context management query, False otherwise
        """
        await logger.ainfo("context_query_classification_start", query=query)

        classification_prompt = f"""
Is this query about MODIFYING the session context (adding/removing/changing papers)?

Query: {query}

Context MODIFICATION queries involve:
- Adding papers to context (with full text, abstracts, or notes)
- Removing papers from context
- Modifying how papers are included in context (changing context type)

NOT context modification queries:
- Asking what's in the context
- Viewing/showing current context
- Checking context status
- Questions about the context without changing it
- Adding or viewing notes on papers (these are handled by separate note commands)
- Any query mentioning "add to notes", "add to my notes", "note", or "notes" - these refer to paper notes, NOT context

Importantly, if they mention the word 'collection', then they are not referring to context management.
Importantly, if they mention "notes" or "my notes", they are referring to paper notes, NOT context management.

IMPORTANT: Only classify as 'yes' if the user wants to CHANGE the context, not just view it.

Respond with only 'yes' or 'no'.
"""

        try:
            response = await self.llm_client.complete(
                [
                    {"role": "user", "content": classification_prompt},
                ],
                model_size="small",
                operation_type="classification",
            )

            content = response.get("content", "")
            classification_result = (
                content.strip().lower() == "yes" if isinstance(content, str) else False
            )
            await logger.ainfo(
                "context_query_classification_complete",
                query=query,
                is_context_query=classification_result,
                raw_response=response.get("content", ""),
            )
            return classification_result

        except Exception as e:
            await logger.aerror(
                "context_query_classification_failed", query=query, error=str(e),
            )
            # Default to non-context query if classification fails
            return False

    async def _handle_context_query(self, query: str) -> None:
        """Handle context queries with ReAct resolution + interactive approval loop.

        This function implements a sophisticated multi-phase workflow for context management:

        **Phase 1: Initial Resolution (Lines 567-572)**
        - Calls _resolve_context_operations() which runs its own ReAct loop (max 3 LLM iterations)
        - The ReAct loop uses specialized context tools to build a list of operations
        - Each LLM call in ReAct adds tool calls and results back to conversation state
        - This allows multi-step reasoning: "first list papers with tag X, then create operations for each"

        **Phase 2: Interactive Approval Loop (Lines 588-626)**
        - Shows preview table of what context will look like after operations
        - User can: Accept (Enter), Cancel (q), or provide feedback (any text)
        - If feedback provided, calls _update_operations_with_feedback() which makes ANOTHER LLM call
        - This feedback LLM call uses different tools to modify existing operations
        - Loop continues until user accepts or cancels

        **Why Multiple LLM Calls?**
        1. **Initial ReAct**: Translates natural language to concrete operations
           - "Add papers about transformers" → [list_papers_by_tag, create_context_operation x5]
           - Can take multiple iterations to resolve complex requests

        2. **Feedback Processing**: Applies targeted modifications to existing operations
           - "Change the first two to full text" → update_paper_context_type calls
           - More precise than regenerating everything from scratch

        **Example Flow:**
        ```
        User: "Add all inference papers to context as abstracts"

        Phase 1 (ReAct):
        Iteration 1: LLM calls list_papers_by_tag(tag="inference")
        Iteration 2: LLM calls create_context_operation for each paper found
        → Operations: [{"paper_id": "1", "action": "add", "context_type": "abstract"}, ...]

        Phase 2 (Approval):
        [Table shows 5 papers will be added as abstracts]
        User: "make the first one full text"

        Feedback LLM: Calls update_paper_context_type(paper_reference="first", new_context_type="full_text")
        → Updated operations: [{"paper_id": "1", "action": "add", "context_type": "full_text"}, ...]

        [Table shows updated preview]
        User: [Enter]
        → Execute all operations via context command handlers
        ```

        Args:
            query: The user's context management query
        """
        await logger.ainfo("context_query_handling_start", query=query)

        # Phase 1: Use ReAct to resolve context operations
        await logger.ainfo("context_operations_resolution_start", query=query)
        operations = await self._resolve_context_operations(query)
        await logger.ainfo(
            "context_operations_resolution_complete",
            query=query,
            operations_count=len(operations),
            operations=operations,
        )

        if not operations:
            await logger.awarning("context_operations_resolution_empty", query=query)
            # Stop the status manager before returning
            self.status_manager.stop()
            console.print(
                "[yellow]Could not resolve any papers from your request.[/yellow]",
            )
            return

        # Phase 2: Show table and get approval
        iteration = 0
        await logger.ainfo(
            "context_approval_loop_start", operations_count=len(operations),
        )

        # Stop the status manager before entering the interactive approval loop
        self.status_manager.stop()

        while True:
            iteration += 1
            await logger.ainfo(
                "context_approval_iteration",
                iteration=iteration,
                operations_count=len(operations),
            )

            self._display_context_preview(operations)

            user_input = console.input(
                "Press Enter to accept, 'q' to cancel, or type changes: ",
            )
            await logger.ainfo(
                "context_approval_user_input",
                iteration=iteration,
                user_input=user_input,
            )

            if user_input == "":
                # Execute operations
                await logger.ainfo(
                    "context_operations_execution_start",
                    operations_count=len(operations),
                )
                result = await self._execute_context_operations(operations)
                await logger.ainfo(
                    "context_operations_execution_complete", result=result,
                )
                console.print(result)
                return
            if user_input.lower() == "q":
                await logger.ainfo(
                    "context_query_cancelled_by_user", iteration=iteration,
                )
                console.print("[yellow]Cancelled[/yellow]")
                return

            # Go back to ReAct with user feedback to modify operations
            await logger.ainfo(
                "context_operations_modification_start",
                iteration=iteration,
                user_feedback=user_input,
            )

            # Show status while updating operations
            self.status_manager.start(
                "[yellow]Updating operations based on feedback...[/yellow]",
            )

            # Apply user feedback to existing operations instead of regenerating from scratch
            updated_operations = await self._update_operations_with_feedback(
                operations, user_input,
            )
            operations = updated_operations

            # Stop status manager before next iteration
            self.status_manager.stop()

            await logger.ainfo(
                "context_operations_modification_complete",
                iteration=iteration,
                new_operations_count=len(operations),
            )

    async def _resolve_context_operations(self, query: str) -> list[dict]:
        """Use ReAct pipeline to resolve context operations.

        Args:
            query: The context management query or feedback

        Returns:
            List of context operations to execute
        """
        await logger.ainfo("context_operations_resolver_start", query=query)

        # Create context-specific tools
        context_tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_context_operation",
                    "description": "Create a context management operation for a single paper, all papers (leave both paper_reference and tag empty), or papers with a tag",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_reference": {
                                "type": "string",
                                "description": "Paper reference (number or natural language). Leave empty to operate on ALL papers",
                            },
                            "tag": {
                                "type": "string",
                                "description": "Tag name to operate on all papers with that tag. Leave empty to operate on single paper or ALL papers",
                            },
                            "action": {"type": "string", "enum": ["add", "remove"]},
                            "context_type": {
                                "type": "string",
                                "enum": ["full_text", "abstract", "notes"],
                                "description": "The type of content to include. Use 'full_text' for variations like 'full text', 'full-text', 'fulltext'. (required for 'add' action, ignored for 'remove')",
                            },
                        },
                        "required": ["action"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_papers",
                    "description": "List all available papers (for 'add all papers' requests)",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_papers_by_tag",
                    "description": "List papers filtered by a specific tag name (e.g., 'inference', 'GPT', 'theory_lm')",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tag": {
                                "type": "string",
                                "description": "The tag name to filter by (without # symbol)",
                            },
                        },
                        "required": ["tag"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "modify_context_operation",
                    "description": "Modify existing context type for a paper, all papers in context (leave both paper_reference and tag empty), or papers with a tag",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_reference": {
                                "type": "string",
                                "description": "Paper reference (number or natural language). Leave empty to modify ALL papers in context",
                            },
                            "tag": {
                                "type": "string",
                                "description": "Tag name to modify all papers with that tag. Leave empty to modify single paper or ALL papers",
                            },
                            "new_context_type": {
                                "type": "string",
                                "enum": ["full_text", "abstract", "notes"],
                                "description": "The new context type. Use 'full_text' for variations like 'full text', 'full-text', 'fulltext'",
                            },
                        },
                        "required": ["new_context_type"],
                    },
                },
            },
        ]

        # Get current context state to inform the LLM
        current_context = self.session_context.get_all_papers()
        context_info = []
        for paper_id, context_types in current_context.items():
            paper = self.db.get_paper(paper_id)
            paper_title = paper.title if paper else "Unknown"
            for context_type in context_types:
                context_info.append(f"- {paper_title}: {context_type}")

        current_context_text = (
            "\n".join(context_info)
            if context_info
            else "No papers currently in context."
        )

        operations: list[dict] = []
        messages = [
            {
                "role": "system",
                "content": f"""Resolve the user's context management request into specific operations.

CURRENT CONTEXT STATE:
{current_context_text}

TOOL USAGE GUIDELINES:

create_context_operation:
- To add/remove ALL papers: Leave both paper_reference and tag empty
- To add/remove papers with a tag: Use the tag parameter only
- To add/remove a single paper: Use the paper_reference parameter only
- Default context_type for bulk operations is usually "full_text"
- For "full text", "full-text", "fulltext" variations, always use context_type="full_text"

modify_context_operation:
- To modify ALL papers in context: Leave both paper_reference and tag empty
- To modify papers with a tag: Use the tag parameter only  
- To modify a single paper: Use the paper_reference parameter only
- This only modifies papers that are already in context

list_papers: Use when you need to see all available papers before creating operations
list_papers_by_tag: Use to check what papers have a specific tag before operating on them

For remove requests, you MUST create operations with action="remove" for papers that are currently in context.""",
            },
            {"role": "user", "content": query},
        ]

        await logger.ainfo("context_react_loop_start", tools_count=len(context_tools))

        # Run tool-calling loop to collect operations
        # NOTE: Not calling this "ReAct" to avoid confusion - this is specifically
        # the context operations resolver that uses tool calls with conversation state
        for iteration in range(3):  # Max 3 iterations
            await logger.ainfo("context_react_iteration", iteration=iteration + 1)

            try:
                response = await self.llm_client.complete(
                    messages,
                    tools=context_tools,
                    model_size="small",
                    operation_type="context_management",
                )
                await logger.ainfo(
                    "context_react_llm_response",
                    iteration=iteration + 1,
                    has_tool_calls="tool_calls" in response,
                    tool_calls_count=len(response.get("tool_calls", [])),
                )

                if "tool_calls" not in response:
                    await logger.ainfo(
                        "context_react_no_tool_calls", iteration=iteration + 1,
                    )
                    break

                # Process tool calls
                for tool_call_idx, tool_call in enumerate(response["tool_calls"]):
                    tool_name = tool_call.name
                    tool_args = tool_call.arguments

                    await logger.ainfo(
                        "context_react_tool_call",
                        iteration=iteration + 1,
                        tool_call_index=tool_call_idx,
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )

                    if tool_name == "create_context_operation":
                        # Check if this is a tag-based operation, paper reference, or ALL papers
                        if "tag" in tool_args and tool_args.get("tag"):
                            # Handle tag-based operations
                            tag = tool_args["tag"]
                            await logger.ainfo("context_tag_operation_start", tag=tag)

                            # Get papers filtered by tag
                            tagged_papers = self.db.list_papers(tag=tag)
                            await logger.ainfo(
                                "context_tag_operation_papers_found",
                                tag=tag,
                                papers_count=len(tagged_papers),
                            )

                            for paper in tagged_papers:
                                operation = {
                                    "paper_id": paper.paper_id,
                                    "paper_title": paper.title,
                                    "action": tool_args["action"],
                                    "tag": tag,  # Store tag for command execution
                                }
                                # Only add context_type for add operations
                                if tool_args["action"] == "add":
                                    operation["context_type"] = tool_args.get("context_type", "full_text")

                                # Check for duplicates
                                operation_key = (
                                    operation["paper_id"],
                                    operation["action"],
                                    operation.get("context_type", ""),
                                )
                                existing_keys = {
                                    (op["paper_id"], op["action"], op.get("context_type", ""))
                                    for op in operations
                                }

                                if operation_key not in existing_keys:
                                    operations.append(operation)
                                    await logger.ainfo(
                                        "context_tag_operation_created",
                                        operation=operation,
                                    )
                                else:
                                    await logger.ainfo(
                                        "context_tag_operation_duplicate_skipped",
                                        operation=operation,
                                    )

                        elif (
                            "paper_reference" in tool_args
                            and tool_args.get("paper_reference")
                        ):
                            # Resolve paper reference to get title/ID
                            paper_reference = tool_args["paper_reference"]
                            await logger.ainfo(
                                "context_paper_resolution_start",
                                paper_reference=paper_reference,
                            )
                            _, paper_id = await resolve_paper_references(
                                paper_reference,
                                self.db,
                                self.llm_client,
                            )
                            await logger.ainfo(
                                "context_paper_resolution_complete",
                                paper_reference=paper_reference,
                                resolved_paper_id=paper_id,
                            )

                            if paper_id:
                                paper = self.db.get_paper(paper_id)
                                if paper:
                                    operation = {
                                        "paper_id": paper_id,
                                        "paper_title": paper.title,
                                        "action": tool_args["action"],
                                    }
                                    # Only add context_type for add operations
                                    if tool_args["action"] == "add":
                                        operation["context_type"] = tool_args.get("context_type", "full_text")
                            else:
                                await logger.awarning(
                                    "context_paper_not_found_in_db", paper_id=paper_id,
                                )
                                continue

                            # Check for duplicates
                            operation_key = (
                                operation["paper_id"],
                                operation["action"],
                                operation.get("context_type", ""),
                            )
                            existing_keys = {
                                (op["paper_id"], op["action"], op["context_type"])
                                for op in operations
                            }

                            if operation_key not in existing_keys:
                                operations.append(operation)
                                await logger.ainfo(
                                    "context_operation_created", operation=operation,
                                )
                            else:
                                await logger.ainfo(
                                    "context_operation_duplicate_skipped",
                                    operation=operation,
                                )
                        else:
                            # Handle ALL papers case (both paper_reference and tag are empty/not provided)
                            await logger.ainfo("context_all_papers_operation_start")
                            
                            # Get all papers from collection
                            all_papers = self.db.list_papers(limit=1000)
                            await logger.ainfo(
                                "context_all_papers_operation_papers_found",
                                papers_count=len(all_papers),
                            )
                            
                            for paper in all_papers:
                                operation = {
                                    "paper_id": paper.paper_id,
                                    "paper_title": paper.title,
                                    "action": tool_args["action"],
                                }
                                # Only add context_type for add operations
                                if tool_args["action"] == "add":
                                    operation["context_type"] = tool_args.get("context_type", "full_text")
                                
                                # Check for duplicates
                                operation_key = (
                                    operation["paper_id"],
                                    operation["action"],
                                    operation.get("context_type", ""),
                                )
                                existing_keys = {
                                    (op["paper_id"], op["action"], op.get("context_type", ""))
                                    for op in operations
                                }
                                
                                if operation_key not in existing_keys:
                                    operations.append(operation)
                                    await logger.ainfo(
                                        "context_all_papers_operation_created",
                                        operation=operation,
                                    )
                                else:
                                    await logger.ainfo(
                                        "context_all_papers_operation_duplicate_skipped",
                                        operation=operation,
                                    )

                    elif tool_name == "list_papers":
                        # Get all papers for "add all" requests
                        await logger.ainfo("context_list_all_papers_start")
                        all_papers = self.db.list_papers()
                        await logger.ainfo(
                            "context_list_all_papers_complete",
                            papers_count=len(all_papers),
                        )

                        for paper in all_papers:
                            operation = {
                                "paper_id": paper.paper_id,
                                "paper_title": paper.title,
                                "action": "add",
                                "context_type": "full_text",  # default
                            }

                            # Check for duplicates
                            operation_key = (
                                operation["paper_id"],
                                operation["action"],
                                operation.get("context_type", ""),
                            )
                            existing_keys = {
                                (op["paper_id"], op["action"], op["context_type"])
                                for op in operations
                            }

                            if operation_key not in existing_keys:
                                operations.append(operation)
                                await logger.ainfo(
                                    "context_bulk_operation_created",
                                    operation=operation,
                                )
                            else:
                                await logger.ainfo(
                                    "context_bulk_operation_duplicate_skipped",
                                    operation=operation,
                                )

                    elif tool_name == "list_papers_by_tag":
                        # Get papers filtered by tag
                        tag = tool_args.get("tag", "")
                        await logger.ainfo("context_list_papers_by_tag_start", tag=tag)

                        # Use the database method to get papers with specific tag
                        tagged_papers = self.db.list_papers(tag=tag)
                        await logger.ainfo(
                            "context_list_papers_by_tag_complete",
                            papers_count=len(tagged_papers),
                            tag=tag,
                        )

                        for paper in tagged_papers:
                            operation = {
                                "paper_id": paper.paper_id,
                                "paper_title": paper.title,
                                "action": "add",
                                "context_type": "full_text",  # default
                            }

                            # Check for duplicates
                            operation_key = (
                                operation["paper_id"],
                                operation["action"],
                                operation.get("context_type", ""),
                            )
                            existing_keys = {
                                (op["paper_id"], op["action"], op["context_type"])
                                for op in operations
                            }

                            if operation_key not in existing_keys:
                                operations.append(operation)
                                await logger.ainfo(
                                    "context_bulk_operation_created",
                                    operation=operation,
                                )
                            else:
                                await logger.ainfo(
                                    "context_bulk_operation_duplicate_skipped",
                                    operation=operation,
                                )

                    elif tool_name == "modify_context_operation":
                        # Handle modify operations - can be for single paper, tag, or ALL papers in context
                        if "tag" in tool_args and tool_args.get("tag"):
                            # Handle tag-based modify
                            tag = tool_args["tag"]
                            await logger.ainfo("context_modify_tag_start", tag=tag)
                            
                            # Get papers with tag that are in context
                            tagged_papers = self.db.list_papers(tag=tag)
                            for paper in tagged_papers:
                                # Only modify if paper is in context
                                if paper.paper_id in current_context:
                                    operation = {
                                        "paper_id": paper.paper_id,
                                        "paper_title": paper.title,
                                        "action": "modify",
                                        "context_type": tool_args["new_context_type"],
                                        "tag": tag,
                                    }
                                    
                                    # Check for duplicates
                                    operation_key = (
                                        operation["paper_id"],
                                        operation["action"],
                                        operation.get("context_type", ""),
                                    )
                                    existing_keys = {
                                        (op["paper_id"], op["action"], op.get("context_type", ""))
                                        for op in operations
                                    }
                                    
                                    if operation_key not in existing_keys:
                                        operations.append(operation)
                                        await logger.ainfo(
                                            "context_modify_tag_operation_created",
                                            operation=operation,
                                        )
                        
                        elif "paper_reference" in tool_args and tool_args.get("paper_reference"):
                            # Handle single paper modify
                            paper_reference = tool_args["paper_reference"]
                            await logger.ainfo(
                                "context_modify_resolution_start",
                                paper_reference=paper_reference,
                            )
                            _, paper_id = await resolve_paper_references(
                                paper_reference,
                                self.db,
                                self.llm_client,
                            )
                            await logger.ainfo(
                                "context_modify_resolution_complete",
                                paper_reference=paper_reference,
                                resolved_paper_id=paper_id,
                            )

                            if paper_id:
                                paper = self.db.get_paper(paper_id)
                                if paper:
                                    operation = {
                                        "paper_id": paper_id,
                                        "paper_title": paper.title,
                                        "action": "modify",
                                        "context_type": tool_args["new_context_type"],
                                    }
                                else:
                                    await logger.awarning(
                                        "context_modify_paper_not_found_in_db",
                                        paper_id=paper_id,
                                    )
                                    continue

                                # Check for duplicates
                                operation_key = (
                                    operation["paper_id"],
                                    operation["action"],
                                    operation.get("context_type", ""),
                                )
                                existing_keys = {
                                    (op["paper_id"], op["action"], op.get("context_type", ""))
                                    for op in operations
                                }

                                if operation_key not in existing_keys:
                                    operations.append(operation)
                                    await logger.ainfo(
                                        "context_modify_operation_created",
                                        operation=operation,
                                    )
                                else:
                                    await logger.ainfo(
                                        "context_modify_operation_duplicate_skipped",
                                        operation=operation,
                                    )
                            else:
                                await logger.awarning(
                                    "context_modify_resolution_failed",
                                    paper_reference=tool_args["paper_reference"],
                                )
                        else:
                            # Modify ALL papers in context (no paper_reference or tag)
                            await logger.ainfo("context_modify_all_start")
                            
                            # Modify all papers currently in context
                            for paper_id in current_context:
                                paper = self.db.get_paper(paper_id)
                                if paper:
                                    operation = {
                                        "paper_id": paper_id,
                                        "paper_title": paper.title,
                                        "action": "modify",
                                        "context_type": tool_args["new_context_type"],
                                    }
                                    
                                    # Check for duplicates
                                    operation_key = (
                                        operation["paper_id"],
                                        operation["action"],
                                        operation.get("context_type", ""),
                                    )
                                    existing_keys = {
                                        (op["paper_id"], op["action"], op.get("context_type", ""))
                                        for op in operations
                                    }
                                    
                                    if operation_key not in existing_keys:
                                        operations.append(operation)
                                        await logger.ainfo(
                                            "context_modify_all_operation_created",
                                            operation=operation,
                                        )

                    else:
                        await logger.awarning(
                            "context_unknown_tool_call", tool_name=tool_name,
                        )

                # Add assistant response and tool results back to conversation
                # This is crucial for maintaining state between iterations
                tool_calls_for_message = []
                for tc in response.get("tool_calls", []):
                    tool_calls_for_message.append(
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                                if isinstance(tc.arguments, dict)
                                else tc.arguments,
                            },
                        },
                    )

                messages.append(
                    {
                        "role": "assistant",
                        "content": response.get("content", ""),
                        "tool_calls": tool_calls_for_message,
                    },
                )

                # Add tool results (these are for operation collection, not execution)
                tool_results = []
                for tool_call in response.get("tool_calls", []):
                    tool_result = f"Successfully processed {tool_call.name}"
                    if tool_call.name == "create_context_operation":
                        tool_result = f"Proposed context operation for {tool_call.arguments.get('paper_reference', 'unknown paper')}"
                    elif tool_call.name == "list_papers":
                        tool_result = "Listed all available papers for bulk operations"
                    elif tool_call.name == "list_papers_by_tag":
                        tag = tool_call.arguments.get("tag", "unknown")
                        tool_result = (
                            f"Listed papers tagged with '{tag}' for bulk operations"
                        )
                    elif tool_call.name == "modify_context_operation":
                        tool_result = f"Proposed context modification for {tool_call.arguments.get('paper_reference', 'unknown paper')}"

                    tool_results.append(
                        {
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        },
                    )

                # Add individual tool result messages
                for tool_result in tool_results:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result["content"],
                        },
                    )

            except Exception as e:
                await logger.aerror(
                    "context_react_iteration_failed",
                    iteration=iteration + 1,
                    error=str(e),
                )
                break

        await logger.ainfo(
            "context_operations_resolver_complete",
            query=query,
            total_operations=len(operations),
            operations=operations,
        )
        return operations

    async def _update_operations_with_feedback(
        self, operations: list[dict], feedback: str,
    ) -> list[dict]:
        """Update existing operations based on user feedback without losing original operations.

        Args:
            operations: Current list of operations
            feedback: User feedback about what to change

        Returns:
            Updated list of operations preserving originals and applying changes
        """
        await logger.ainfo(
            "update_operations_with_feedback_start",
            current_operations_count=len(operations),
            feedback=feedback,
        )

        # Create a simplified tool for making targeted updates
        update_tools = [
            {
                "type": "function",
                "function": {
                    "name": "update_paper_context_type",
                    "description": "Update the context type for a specific paper",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_reference": {"type": "string"},
                            "new_context_type": {
                                "type": "string",
                                "enum": ["full_text", "abstract", "notes"],
                                "description": "The new context type. Use 'full_text' for variations like 'full text', 'full-text', 'fulltext'",
                            },
                        },
                        "required": ["paper_reference", "new_context_type"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_paper_operation",
                    "description": "Remove a paper from the operations entirely",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_reference": {"type": "string"},
                        },
                        "required": ["paper_reference"],
                    },
                },
            },
        ]

        # Build context about current operations for the LLM
        operations_summary = []
        for op in operations:
            if op['action'] == 'remove':
                operations_summary.append(
                    f"- {op['paper_title']}: {op['action']}",
                )
            else:
                operations_summary.append(
                    f"- {op['paper_title']}: {op['action']} as {op.get('context_type', 'full_text')}",
                )

        operations_text = "\n".join(operations_summary)

        messages = [
            {
                "role": "system",
                "content": f"""You need to update the existing context operations based on user feedback.
                
Current operations:
{operations_text}

IMPORTANT: Only make the specific changes requested by the user. Do not remove or change operations that the user didn't mention.

When the user requests to use "full text", "full-text", "fulltext", "full_text", or "the full text", always use context_type="full_text".
When the user requests to use "abstract" or "abstracts", they mean context_type should be "abstract".
When the user requests to use "notes", they mean context_type should be "notes".

If the user says to use a different context type for ALL papers (e.g., "use full text", "change to full text", "use the full text"), 
you should call update_paper_context_type for EACH paper in the operations list to change them all to that context type.

Use update_paper_context_type to change what context type a paper should use.
Use remove_paper_operation to remove a paper entirely from the operations.""",
            },
            {"role": "user", "content": feedback},
        ]

        # Start with existing operations and apply updates
        updated_operations = operations.copy()

        try:
            response = await self.llm_client.complete(
                messages,
                tools=update_tools,
                model_size="small",
                operation_type="context_modification",
            )
            await logger.ainfo(
                "update_operations_llm_response",
                has_tool_calls="tool_calls" in response,
                tool_calls_count=len(response.get("tool_calls", [])),
            )

            if "tool_calls" in response:
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call.name
                    tool_args = tool_call.arguments

                    await logger.ainfo(
                        "update_operations_tool_call",
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )

                    if tool_name == "update_paper_context_type":
                        paper_ref = tool_args["paper_reference"]
                        new_context_type = tool_args["new_context_type"]

                        # Find and update the matching operation
                        for i, op in enumerate(updated_operations):
                            # Match by paper title or paper ID
                            if (
                                paper_ref.lower() in op["paper_title"].lower()
                                or paper_ref == op["paper_id"]
                            ):
                                updated_operations[i] = {
                                    **op,
                                    "context_type": new_context_type,
                                    "action": "add"
                                    if op["action"] == "add"
                                    else "modify",
                                }
                                await logger.ainfo(
                                    "operation_updated",
                                    paper_id=op["paper_id"],
                                    old_context_type=op["context_type"],
                                    new_context_type=new_context_type,
                                )
                                break
                        else:
                            await logger.awarning(
                                "paper_not_found_for_update", paper_reference=paper_ref,
                            )

                    elif tool_name == "remove_paper_operation":
                        paper_ref = tool_args["paper_reference"]

                        # Remove matching operations
                        updated_operations = [
                            op
                            for op in updated_operations
                            if not (
                                paper_ref.lower() in op["paper_title"].lower()
                                or paper_ref == op["paper_id"]
                            )
                        ]
                        await logger.ainfo(
                            "operation_removed", paper_reference=paper_ref,
                        )

        except Exception as e:
            await logger.aerror(
                "update_operations_failed", error=str(e), feedback=feedback,
            )
            # Return original operations if update fails
            return operations

        await logger.ainfo(
            "update_operations_with_feedback_complete",
            original_count=len(operations),
            updated_count=len(updated_operations),
        )
        return updated_operations

    def _display_context_preview(self, operations: list[dict]) -> None:
        """Display what the user's context will contain after operations.

        Args:
            operations: List of operations to apply and show final state for
        """
        logger.info("context_final_state_display", operations_count=len(operations))

        # Get current context state
        current_context = self.session_context.get_all_papers()
        logger.info("current_context_retrieved", current_papers=len(current_context))

        # Calculate final state after applying all operations
        final_state: dict[str, str] = {}

        # Start with current context (paper_id -> context_type string)
        for paper_id, context_type in current_context.items():
            final_state[paper_id] = context_type

        # Apply operations to calculate final state
        for op in operations:
            paper_id = op["paper_id"]
            action = op["action"]

            if action == "add":
                # Add or replace the context type for this paper
                context_type = op.get("context_type", "full_text")
                final_state[paper_id] = context_type
            elif action == "remove":
                # Remove paper from context entirely
                if paper_id in final_state:
                    del final_state[paper_id]
            elif action == "modify":
                # Modify the context type for this paper (only if in context)
                context_type = op.get("context_type", "full_text")
                if paper_id in final_state or paper_id in current_context:
                    final_state[paper_id] = context_type

        # Display final state table
        table = Table(title="Your context will contain:")
        table.add_column("Paper", style="cyan")
        table.add_column("Context Type", style="yellow")

        # Show each paper and its context type in the final state
        for paper_id, context_type in final_state.items():
            # Get paper title
            paper = self.db.get_paper(paper_id)
            paper_title = paper.title if paper else "Unknown"
            title = paper_title[:60] + "..." if len(paper_title) > 60 else paper_title

            # Show the context type for this paper
            table.add_row(title, context_type)
            logger.info(
                "context_final_state_row_added",
                paper_id=paper_id,
                context_type=context_type,
            )

        console.print(table)
        logger.info("context_final_state_displayed", final_papers=len(final_state))

    async def _execute_context_operations(self, operations: list[dict]) -> str:
        """Execute approved operations using existing command handlers.

        Args:
            operations: List of operations to execute

        Returns:
            Success message with count of executed operations
        """
        success_count = 0

        for op in operations:
            try:
                if op["action"] == "add":
                    handler = self.command_handlers.get("handle_context_add")
                    if handler:
                        context_type = op.get('context_type', 'full_text')
                        args = f"{op['paper_id']} {context_type}"
                        await handler(
                            args, self.db, self.session_context, self.llm_client,
                            skip_resolution=True,  # We already resolved in _resolve_context_operations
                        )
                        success_count += 1
                elif op["action"] == "remove":
                    handler = self.command_handlers.get("handle_context_remove")
                    if handler:
                        args = op['paper_id']  # Remove doesn't need context_type
                        await handler(
                            args, self.db, self.session_context, self.llm_client,
                            skip_resolution=True,  # We already resolved in _resolve_context_operations
                        )
                        success_count += 1
                elif op["action"] == "modify":
                    handler = self.command_handlers.get("handle_context_modify")
                    if handler:
                        # Modify expects: paper_ref new_context_type
                        context_type = op.get('context_type', 'full_text')
                        args = f"{op['paper_id']} {context_type}"
                        await handler(
                            args, self.db, self.session_context, self.llm_client,
                            skip_resolution=True,  # We already resolved in _resolve_context_operations
                        )
                        success_count += 1
            except Exception as e:
                await logger.aerror(
                    "context_operation_failed", operation=op, error=str(e),
                )

        return f"[green]✓ Executed {success_count}/{len(operations)} context operations[/green]"
