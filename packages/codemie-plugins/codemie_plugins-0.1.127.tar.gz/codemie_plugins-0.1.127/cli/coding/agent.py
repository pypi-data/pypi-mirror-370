import asyncio
import os
import time
from typing import Any, Dict, List, Optional

from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from cli.coding.agent_formatter import AgentResponseFormatter
from cli.coding.mcp_client import MCPClientManager
from cli.coding.prompts import CODING_AGENT_PROMPT
from cli.coding.toolkit import FilesystemToolkit
from cli.utils import LOCAL_CONFIG_PROMPT_FILE, get_config_value, load_local_config_file

console = Console()
# Configuration keys
KEY_LLM_SERVICE_API_KEY = "LLM_SERVICE_API_KEY"
KEY_LLM_SERVICE_BASE_URL = "LLM_SERVICE_BASE_URL"
# Default recursion limit for the agent
DEFAULT_RECURSION_LIMIT = 50


class Agent:
    """Class to manage the agent and its interactions."""

    def __init__(self, model_name: str = "gpt-4o",
                 temperature: float = 0.7,
                 verbose: bool = False,
                 allowed_directories: Optional[List[str]] = None,
                 recursion_limit: int = DEFAULT_RECURSION_LIMIT,
                 use_global_prompt: bool = False,
                 mcp_servers: Optional[str] = None,
                 disable_default_tools: bool = False):
        """Initialize the agent with the specified configuration."""
        self.verbose = verbose
        self.use_global_prompt = use_global_prompt
        self.mcp_servers = mcp_servers
        self.disable_default_tools = disable_default_tools

        # Initialize conversation history
        self.conversation_history = []

        # Initialize token tracking
        self.token_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

        # Initialize execution time tracking
        self.start_time = None

        # Set recursion limit
        self.recursion_limit = recursion_limit

        # Create a single event loop to be used throughout the lifecycle
        self._initialize_event_loop()

        # Setup LLM and tools
        self._setup_llm(model_name, temperature)
        self._setup_tools(allowed_directories)

        # Initialize formatter
        self.formatter = AgentResponseFormatter()

    def _initialize_event_loop(self):
        """Initialize a global event loop for async operations."""
        # Store a reference to the loop for future use
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def _setup_llm(self, model_name: str, temperature: float) -> None:
        """Set up the language model with the given parameters."""
        # Get API key and base URL from environment or config
        api_key = os.getenv(KEY_LLM_SERVICE_API_KEY) or get_config_value(KEY_LLM_SERVICE_API_KEY)
        base_url = os.getenv(KEY_LLM_SERVICE_BASE_URL) or get_config_value(KEY_LLM_SERVICE_BASE_URL)

        if not api_key:
            raise ValueError("LLM_SERVICE_API_KEY is not set. \nPlease configure it using:\n"
                             "codemie-plugins config set LLM_SERVICE_API_KEY your-api-key")

        self.llm = AzureChatOpenAI(
            model=model_name,
            max_retries=2,
            temperature=temperature,
            openai_api_key=api_key,
            azure_endpoint=base_url,
            openai_api_version="2024-12-01-preview",
            openai_api_type="azure",
        )

    def _setup_tools(self, allowed_directories: Optional[List[str]]) -> None:
        """Set up the tools and agent with the given parameters."""
        self.config = {
            "allowed_directories": allowed_directories or [os.getcwd()]
        }

        # Initialize tools list
        self.tools = []
        
        # Add MCP tools if specified
        mcp_tools = []
        if self.mcp_servers:
            mcp_client = MCPClientManager(self.mcp_servers, self.disable_default_tools)
            mcp_tools = mcp_client.setup_mcp_tools()
            if mcp_tools:
                self.tools.extend(mcp_tools)
        
        # Add base filesystem tools unless disabled when MCP tools are loaded
        if not (self.disable_default_tools and self.mcp_servers and mcp_tools):
            self.tools.extend(FilesystemToolkit.get_toolkit(self.config).get_tools())
        elif self.disable_default_tools and self.mcp_servers and mcp_tools:
            console.print("[yellow]Default tools disabled as requested. Using only MCP tools.[/yellow]")

        # Set up the agent with appropriate prompt
        self._setup_agent()

    def _setup_agent(self) -> None:
        """Set up the agent with the appropriate prompt."""
        # Check for local prompt override unless global prompt is forced
        local_prompt = None if self.use_global_prompt else load_local_config_file(LOCAL_CONFIG_PROMPT_FILE)
        prompt_to_use = local_prompt if local_prompt else CODING_AGENT_PROMPT

        # Show appropriate notification about which prompt is being used
        self._notify_prompt_source(local_prompt)

        self.coder = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=prompt_to_use,
        )

    def _notify_prompt_source(self, local_prompt: Optional[str]) -> None:
        """Notify the user about which prompt is being used."""
        if self.use_global_prompt and load_local_config_file(LOCAL_CONFIG_PROMPT_FILE):
            console.print("[yellow]Forcing use of global prompt (ignoring local prompt)[/yellow]")
        elif local_prompt:
            console.print("[yellow]Using local prompt from .codemie/prompt.txt[/yellow]")

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to handle Unicode characters properly."""
        if isinstance(text, str):
            return text.encode('utf-8', errors='replace').decode('utf-8')
        return str(text)

    def _add_to_conversation(self, role: str, content: str) -> None:
        """Add a message to the conversation history with proper encoding."""
        sanitized_content = self._sanitize_text(content)
        self.conversation_history.append({"role": role, "content": sanitized_content})

    def _update_token_usage(self, msg: Any) -> None:
        """Update token usage statistics from message metadata."""
        if not hasattr(msg, "usage_metadata") or not msg.usage_metadata:
            return

        usage = msg.usage_metadata
        self.token_usage["input_tokens"] += usage.get("input_tokens", 0)
        self.token_usage["output_tokens"] += usage.get("output_tokens", 0)
        self.token_usage["total_tokens"] += usage.get("total_tokens", 0)

    def _process_agent_response(self, update_data: Dict[str, Any]) -> None:
        """Process agent responses and update conversation history and token usage."""
        if "agent" not in update_data:
            return

        for msg in update_data["agent"]["messages"]:
            # Add message content to conversation if it's not a tool call
            content = getattr(msg, "content", "")
            tool_calls = getattr(msg, "tool_calls", None)

            if content and not tool_calls:
                self._add_to_conversation("assistant", content)

            # Track token usage
            self._update_token_usage(msg)

    def _update_status_message(self, status: Status, update_type: str, update_data: Dict[str, Any]) -> None:
        """Update the status message based on the current operation."""
        if update_type == "tool" and "name" in update_data:
            tool_name = update_data.get("name", "unknown")
            status.update(f"[yellow]Using tool: {tool_name}...[/yellow]")
        else:
            status.update("[cyan]Agent is thinking...[/cyan]")

    def _stream_agent_responses(self) -> None:
        """Stream responses from the agent and process them."""
        # Start timing execution
        self.start_time = time.time()

        # Use Rich's Status for the thinking indicator
        with Status("[cyan]Agent is thinking...", spinner="dots", refresh_per_second=20) as status:
            # Track time for updates
            last_update_time = time.time()

            # Stream responses
            for chunk in self.coder.stream(
                    {"messages": self.conversation_history},
                    {"recursion_limit": self.recursion_limit},
                    stream_mode=["updates"]
            ):
                # Each chunk is a tuple with (update_type, update_data)
                update_type, update_data = chunk

                # Update status message based on what's happening
                current_time = time.time()
                if current_time - last_update_time > 1.0:
                    self._update_status_message(status, update_type, update_data)
                    last_update_time = current_time

                # Print the actual content without affecting the status
                status.stop()
                self.formatter.print_update(update_type, update_data, self.verbose)
                status.start()  # Resume the status spinner

                # Process agent responses for conversation history
                self._process_agent_response(update_data)

            # Update status to show completion
            status.update("[green]Response complete[/green]")

        # Display final information
        self._display_completion_info()

    def _display_completion_info(self) -> None:
        """Display final information about the agent execution."""
        if not self.start_time:
            return
            
        # Calculate execution time
        execution_time = time.time() - self.start_time
        execution_time_str = f"{execution_time:.2f} seconds"

        summary = (
            f"[bold green]✓ Agent Execution Complete[/bold green]\n"
            f"[cyan]Execution Duration:[/cyan] {execution_time_str}"
        )
        
        # Add token usage information if verbose mode is enabled
        if self.verbose:
            summary += self._get_token_usage_summary()
            
        # Create a panel with completion information
        console.print(Panel(
            summary,
            title="Execution Summary",
            border_style="green",
            expand=False
        ))

    def _get_token_usage_summary(self) -> str:
        """Get a formatted summary of token usage."""
        return (
            f"\n[cyan]Tokens Usage:[/cyan]\n"
            f"  • Input Tokens: [yellow]{self.token_usage['input_tokens']:,}[/yellow]\n"
            f"  • Output Tokens: [yellow]{self.token_usage['output_tokens']:,}[/yellow]\n"
            f"  • Total Tokens: [bold yellow]{self.token_usage['total_tokens']:,}[/bold yellow]"
        )

    def run(self, user_input: str) -> None:
        """Run the agent with the given user input and print formatted responses."""
        try:
            # Sanitize input and add to conversation
            sanitized_input = self._sanitize_text(user_input)

            # Add user message to conversation history
            self._add_to_conversation("user", sanitized_input)

            # Process agent responses
            self._stream_agent_responses()

        except Exception as e:
            console.print(f"[red]Error processing input:[/red] {str(e)}")

    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like exit and reset.
        Returns True if a special command was handled, False otherwise."""
        command = user_input.strip().lower()

        if command == "exit":
            console.print("[yellow]Exiting interactive mode...[/yellow]")
            self._cleanup_resources()
            return True

        if command == "reset":
            self._reset_conversation()
            console.print("[green]Conversation history has been reset. You can start a new conversation.[/green]")
            return True

        return False

    def _reset_conversation(self) -> None:
        """Reset the conversation history and token usage."""
        self.conversation_history = []
        # Reset token usage
        self.token_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

    def _cleanup_resources(self) -> None:
        """Clean up resources before exiting."""
        # Close the event loop if it's still open
        if hasattr(self, 'loop') and self.loop and not self.loop.is_closed():
            try:
                self.loop.close()
            except Exception as e:
                console.print(f"[yellow]Warning: Error closing event loop: {str(e)}[/yellow]")

    def run_interactive(self) -> None:
        """Run the agent in interactive mode."""
        # Display welcome message with instructions
        self._display_welcome_message()

        try:
            while True:
                try:
                    # Get user input using Rich's console.input
                    console.print()  # Add a blank line for better readability
                    user_input = console.input("[bold cyan]>>> [/bold cyan] ")

                    # Handle special commands
                    if self._handle_special_commands(user_input):
                        if user_input.strip().lower() == "exit":
                            break
                        continue

                    # Process the input
                    self.run(user_input)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Keyboard interrupt received. Type 'exit' to quit.[/yellow]")
                except UnicodeEncodeError as e:
                    console.print(f"[red]Unicode encoding error:[/red] {str(e)}")
                    console.print("[yellow]Some characters in your input couldn't be processed. Please try again with different text.[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error:[/red] {str(e)}")
                    console.print("[yellow]Please try again or type 'exit' to quit.[/yellow]")
        finally:
            # Ensure resources are cleaned up
            self._cleanup_resources()
            
    def _display_welcome_message(self) -> None:
        """Display welcome message with instructions for interactive mode."""
        welcome_message = "[bold green]CodeMie Developer Agent Interactive Mode[/bold green]\n\n"
        welcome_message += "[yellow]Commands:[/yellow]\n"
        welcome_message += "  • [cyan]exit[/cyan] - Exit interactive mode\n"
        welcome_message += "  • [cyan]reset[/cyan] - Reset conversation history\n\n"

        # Add MCP server information if applicable
        if self.mcp_servers:
            from toolkits.mcp.main import ArgumentHandler
            server_names = ArgumentHandler.parse_server_names(self.mcp_servers)
            if server_names:
                welcome_message += f"[green]MCP Servers Enabled:[/green] {', '.join(server_names)}\n"
                if self.disable_default_tools:
                    welcome_message += "[yellow]Default tools disabled[/yellow]\n\n"
                else:
                    welcome_message += "\n"

        welcome_message += "Type your coding questions or requests below:"

        console.print(Panel(
            welcome_message,
            border_style="green",
            expand=False
        ))
