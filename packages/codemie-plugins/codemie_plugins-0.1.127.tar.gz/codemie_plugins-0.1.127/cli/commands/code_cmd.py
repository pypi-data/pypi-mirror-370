"""Command module for interactive coding assistance.

This module provides an interactive coding assistant that helps with
code-related tasks through a conversational interface.
"""
import os
import traceback

import click
from rich.console import Console

from cli.coding.agent import DEFAULT_RECURSION_LIMIT, Agent
from cli.commands.custom_command import CustomCommand


class CodeCommand(CustomCommand):
    """Custom command implementation for the code command."""
    
    def _get_command_examples(self, ctx: click.Context) -> str:
        """Get command-specific examples for the help text."""
        # Get the full command path
        command_path = self._get_command_path(ctx)
        
        # Command-specific examples
        return (
            f"# Start the interactive coding assistant\n"
            f"{command_path}\n\n"
            f"# Use a specific model\n"
            f"{command_path} --model gpt-4o\n\n"
            f"# Set a custom temperature\n"
            f"{command_path} --temperature 0.2\n\n"
            f"# Specify allowed directories\n"
            f"{command_path} --allowed-dir /path/to/project\n\n"
            f"# Use with specific LLM service configuration\n"
            f"{command_path} --llm-api-key your-api-key --llm-base-url https://your-llm-service.com\n\n"
            f"# Use with a local prompt (overrides default)\n"
            f"codemie-plugins config local-prompt \"Your custom prompt\"\n"
            f"# Force using the default global prompt\n"
            f"{command_path} -g\n\n"
            f"# Use with MCP servers\n"
            f"{command_path} --mcp-servers firecrawl\n\n"
            f"# Use MCP servers and disable default tools\n"
            f"{command_path} --mcp-servers jetbrains -d"
        )

MSG_ERROR_RUNNING_CODE = "[bold red]Error running Code command:[/] {}"

# Initialize console for pretty terminal output
console = Console()


@click.command(name="code", cls=CodeCommand)
@click.option(
    "--model", 
    "-m", 
    default="anthropic.claude-3-7-sonnet-20250219-v1:0",
    help="The model to use for the coding assistant"
)
@click.option(
    "--temperature", 
    "-t", 
    default=0.7,
    type=float,
    help="Temperature setting for the model (0.0-1.0)"
)
@click.option(
    "--allowed-dir", 
    "-d", 
    multiple=True,
    help="Directories the agent is allowed to access (can specify multiple)"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode to avoid logs truncation"
)
@click.option(
    "--recursion-limit",
    "-r",
    default=DEFAULT_RECURSION_LIMIT,
    type=int,
    help=f"Maximum recursion limit for the agent (default: {DEFAULT_RECURSION_LIMIT})"
)
@click.option(
    "--global-prompt",
    "-g",
    is_flag=True,
    help="Use the default global prompt even if a local prompt is configured"
)
@click.option(
    "--mcp-servers",
    help="Comma-separated list of MCP server names to include in the agent"
)
@click.option(
    "--disable-default-tools",
    "-d",
    is_flag=True,
    help="Disable default tools when similar MCP servers and tools are loaded. Do NOT disable this unless you have similar tools on MCP servers"
)
@click.pass_context
def code_cmd(ctx: click.Context, model: str, temperature: float, allowed_dir, verbose: bool = False,
             recursion_limit: int = DEFAULT_RECURSION_LIMIT, global_prompt: bool = False, mcp_servers: str = None,
             disable_default_tools: bool = False):
    """Start an interactive coding assistant.
    
    This command launches an AI-powered coding assistant that can help with
    various coding tasks through a conversational interface. The assistant
    can access the filesystem to help with code-related tasks.
    """
    # Welcome message
    try:
        # Set up allowed directories
        allowed_directories = list(allowed_dir) if allowed_dir else None
        
        # Display working directory information
        if allowed_directories:
            console.print("[green]Using specified allowed directories:[/green]")
            for directory in allowed_directories:
                console.print(f"  • [cyan]{directory}[/cyan]")
        else:
            console.print(f"[green]Using default directory:[/green] [cyan]{os.getcwd()}[/cyan]")

        # Set verbose environment variable if enabled
        if verbose:
            console.print("[yellow]Verbose mode enabled. Logs will be displayed without truncation.[/yellow]")

        # Initialize and run the agent
        agent = Agent(
            model_name=model,
            temperature=temperature,
            allowed_directories=allowed_directories,
            verbose=verbose,
            recursion_limit=recursion_limit,
            use_global_prompt=global_prompt,
            mcp_servers=mcp_servers,
            disable_default_tools=disable_default_tools
        )

        # Run in interactive mode
        agent.run_interactive()
    except UnicodeEncodeError as e:
        console.print(MSG_ERROR_RUNNING_CODE.format(f"Unicode encoding error: {str(e)}"))
        console.print("[yellow]Some characters couldn't be processed. Please try again with different text.[/yellow]")
        if ctx.obj.get('DEBUG'):
            console.print(traceback.format_exc())
    except Exception as e:
        console.print(MSG_ERROR_RUNNING_CODE.format(str(e)))
        if ctx.obj.get('DEBUG'):
            console.print(traceback.format_exc())


