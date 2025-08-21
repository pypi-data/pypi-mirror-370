"""Command module to list available CLI commands and toolkits.

This module provides functionality to display available commands in the CLI
with optional verbose output showing command descriptions and options.
"""
from typing import Dict, List

import click
from rich.console import Console
from rich.table import Table

from cli.commands.custom_command import CustomCommand

# Constants
TITLE_AVAILABLE_COMMANDS = "Available CodeMie CLI Commands"
COLUMN_COMMAND = "Command"
COLUMN_DESCRIPTION = "Description"
COLUMN_OPTIONS = "Options"
DEFAULT_DESCRIPTION = "No description available"
NO_OPTIONS = "None"

# Styles
STYLE_COMMAND = "cyan"
STYLE_DESCRIPTION = "green"
STYLE_OPTIONS = "yellow"

# Error messages
ERROR_NO_COMMAND_INFO = "[yellow]Could not retrieve command information.[/]"
ERROR_NO_COMMANDS = "[yellow]No commands available.[/]"

# Initialize console globally for consistent styling
console = Console()


class ListCommand(CustomCommand):
    """Custom command implementation for the list command."""
    
    def _get_command_examples(self, ctx: click.Context) -> str:
        """Get command-specific examples for the help text."""
        # Get the full command path
        command_path = self._get_command_path(ctx)
        
        # Command-specific examples
        return (
            f"# List available commands\n"
            f"{command_path}\n\n"
            f"# List commands with detailed information\n"
            f"{command_path} -v"
        )


@click.command(name="list", cls=ListCommand)
@click.option(
    "--verbose", 
    "-v", 
    is_flag=True, 
    help="Display detailed information about each item"
)
@click.pass_context
def list_cmd(ctx: click.Context, verbose: bool):
    """List available CodeMie CLI commands.
    
    By default, displays available toolkits.
    Use --verbose flag to view details about CLI commands.
    """
    list_available_commands(ctx, verbose)


def list_available_commands(ctx: click.Context, verbose: bool):
    """List all available CLI commands from the main CLI group.
    
    Args:
        ctx: The Click context object containing parent command information
        verbose: Flag to display detailed information about commands
    """
    # Get the parent CLI group from context
    parent_cli = ctx.parent
    
    if not parent_cli or not hasattr(parent_cli, 'command') or not hasattr(parent_cli.command, 'commands'):
        console.print(ERROR_NO_COMMAND_INFO)
        return
    
    # Get available commands from the parent CLI group
    commands = parent_cli.command.commands
    
    if not commands:
        console.print(ERROR_NO_COMMANDS)
        return
    
    # Create and display the commands table
    table = _create_commands_table(commands, verbose)
    console.print(table)


def _create_commands_table(commands: Dict[str, click.Command], verbose: bool) -> Table:
    """Create a formatted table of commands.
    
    Args:
        commands: Dictionary of command names to command objects
        verbose: Flag to include additional command details
        
    Returns:
        A Rich Table object populated with command information
    """
    table = Table(title=TITLE_AVAILABLE_COMMANDS)
    table.add_column(COLUMN_COMMAND, style=STYLE_COMMAND)
    
    if verbose:
        table.add_column(COLUMN_DESCRIPTION, style=STYLE_DESCRIPTION)
        table.add_column(COLUMN_OPTIONS, style=STYLE_OPTIONS)
    
    # Add each command to the table
    for cmd_name, cmd in sorted(commands.items()):
        if verbose:
            description = cmd.help or DEFAULT_DESCRIPTION
            options_text = _get_command_options_text(cmd)
            table.add_row(cmd_name, description, options_text)
        else:
            table.add_row(cmd_name)
    
    return table


def _get_command_options_text(command: click.Command) -> str:
    """Extract and format options text from a command.
    
    Args:
        command: The Click command to extract options from
        
    Returns:
        A string representation of the command's options
    """
    options: List[str] = []
    
    if hasattr(command, 'params'):
        for param in command.params:
            if isinstance(param, click.Option):
                options.append(f"{', '.join(param.opts)}")
    
    return ", ".join(options) if options else NO_OPTIONS
