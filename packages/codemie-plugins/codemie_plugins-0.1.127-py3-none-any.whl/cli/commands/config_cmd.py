"""Commands for configuration management.

This module provides CLI commands for managing and viewing configuration settings
for the CodeMie Plugins CLI. It allows users to view, set, and retrieve configuration
values that affect the behavior of the CLI tool.
"""
import json
import os
import uuid
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from cli.commands.custom_command import CustomCommand
from cli.commands.custom_group import CustomGroup
from cli.utils import (
    get_config_value, load_config, set_config_value,
    get_local_config_dir, get_local_config_file, 
    load_local_config_file, save_local_config_file,
    LOCAL_CONFIG_PROMPT_FILE
)

# Constants for configuration keys
CONFIG_KEY_PLUGIN_KEY = "PLUGIN_KEY"

# Constants for UI elements
TABLE_TITLE = "CodeMie Plugins Configuration"
COLUMN_KEY = "Key"
COLUMN_VALUE = "Value"
COLUMN_SOURCE = "Source"
SOURCE_ENVIRONMENT = "Environment"
SOURCE_CONFIG_FILE = "Config File"
NOT_SET_TEXT = "[dim]Not set[/]"

# Console styling
STYLE_KEY = "cyan"
STYLE_VALUE = "green"
STYLE_SOURCE = "yellow"
STYLE_SUCCESS = "green"
STYLE_WARNING = "yellow"
STYLE_ERROR = "bold red"

# Global console instance
console = Console()

USAGE = (
    "# Show current configuration\n"
    "codemie-plugins config list\n\n"
    "# Generate a random UUID and set it as the plugin key\n"
    "codemie-plugins config generate-key\n\n"
    "# List all configuration including environment variables\n"
    "codemie-plugins config list --all\n\n"
    "# Set your plugin key\n"
    "codemie-plugins config set PLUGIN_KEY your-plugin-key\n\n"
    "# Get a specific configuration value\n"
    "codemie-plugins config get PLUGIN_KEY\n\n"
    "# Create or update a local prompt file for CodeMie Code\n"
    "codemie-plugins config local-prompt 'Your custom prompt text'\n\n"
    "# Show the current local prompt\n"
    "codemie-plugins config show-local-prompt"
)

class ConfigGroup(CustomGroup):

    def _get_command_examples(self, ctx: click.Context) -> str:
        return USAGE

class ConfigCommand(CustomCommand):

    def _get_command_examples(self, ctx: click.Context) -> str:
        return USAGE


@click.group(name="config", cls=ConfigGroup)
@click.pass_context
def config_cmd(ctx: click.Context) -> None:
    """Manage CLI configuration settings."""
    pass


@config_cmd.command(name="list", cls=ConfigCommand)
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration settings.
    
    Displays a table of configuration values from both environment variables
    and the configuration file. JSON values are automatically detected and
    pretty-formatted for better readability.
    """
    config = load_config()
    table = _create_config_table()
    keys = config.keys()
    _populate_config_table(table, keys, config)
    console.print(table)


@config_cmd.command(name="set", cls=ConfigCommand)
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value.
    
    Args:
        key: The configuration key to set
        value: The value to assign to the key
    """
    try:
        set_config_value(key, value)
        console.print(f"[{STYLE_SUCCESS}]Configuration updated:[/] {key} = {value}")
    except Exception as e:
        console.print(f"[{STYLE_ERROR}]Error setting configuration:[/] {str(e)}")


@config_cmd.command(name="get", cls=ConfigCommand)
@click.argument("key")
@click.pass_context
def config_get(ctx: click.Context, key: str) -> None:
    """Get a specific configuration value.
    
    Args:
        key: The configuration key to retrieve
    """
    value = get_config_value(key)
    if value is not None:
        formatted_value = _format_value(value)
        if isinstance(formatted_value, Syntax):
            # For JSON values, display with more context
            console.print(f"{key}:")
            console.print(formatted_value)
        else:
            # For simple values, display inline
            console.print(f"{key} = {formatted_value}")
    else:
        console.print(f"[{STYLE_WARNING}]Configuration key '{key}' is not set[/]")


@config_cmd.command(name="generate-key", cls=ConfigCommand)
@click.pass_context
def config_generate_key(ctx: click.Context) -> None:
    """Generate and set a new plugin key as UUID.
    
    Generates a random UUID and sets it as the PLUGIN_KEY in the configuration.
    This provides a unique identifier for your plugin.
    """
    # Generate a random UUID
    plugin_key = str(uuid.uuid4())
    
    try:
        # Set the plugin key in the configuration
        set_config_value(CONFIG_KEY_PLUGIN_KEY, plugin_key)
        console.print(f"[{STYLE_SUCCESS}]Generated and set new plugin key:[/] {plugin_key}")
    except Exception as e:
        console.print(f"[{STYLE_ERROR}]Error setting plugin key:[/] {str(e)}")


@config_cmd.command(name="local-prompt", cls=ConfigCommand)
@click.argument("prompt_text", required=False)
@click.option("--file", "-f", help="Load prompt from a file instead of command line")
@click.pass_context
def config_local_prompt(ctx: click.Context, prompt_text: Optional[str], file: Optional[str]) -> None:
    """Create or update a local prompt file in .codemie directory.
    
    The local prompt file overrides the default prompt for code_cmd in the current directory.
    
    Args:
        prompt_text: The prompt text to save (optional if --file is provided)
        file: Path to a file containing the prompt text (optional)
    """
    content = None
    
    # Get content from file if specified
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            console.print(f"[{STYLE_ERROR}]Error reading prompt file:[/] {str(e)}")
            return
    # Otherwise use the provided prompt text
    elif prompt_text:
        content = prompt_text
    else:
        console.print(f"[{STYLE_ERROR}]Error: Please provide prompt text or a file path[/]")
        return
    
    # Save the prompt to the local config directory
    if save_local_config_file(LOCAL_CONFIG_PROMPT_FILE, content):
        local_path = get_local_config_file(LOCAL_CONFIG_PROMPT_FILE)
        console.print(f"[{STYLE_SUCCESS}]Local prompt saved to:[/] {local_path}")
    else:
        console.print(f"[{STYLE_ERROR}]Failed to save local prompt[/]")


@config_cmd.command(name="show-local-prompt", cls=ConfigCommand)
@click.pass_context
def config_show_local_prompt(ctx: click.Context) -> None:
    """Show the current local prompt if it exists.
    
    Displays the content of the local prompt.txt file from the .codemie directory.
    """
    prompt_content = load_local_config_file(LOCAL_CONFIG_PROMPT_FILE)
    
    if prompt_content:
        # Create a syntax-highlighted panel for the prompt
        syntax = Syntax(prompt_content, "text", theme="monokai", word_wrap=True)
        panel = Panel(
            syntax,
            title="[bold green]Local Prompt[/]",
            border_style="green",
            expand=False
        )
        console.print(panel)
    else:
        local_path = get_local_config_file(LOCAL_CONFIG_PROMPT_FILE)
        console.print(f"[{STYLE_WARNING}]No local prompt found at:[/] {local_path}")
        console.print("Use 'codemie-plugins config local-prompt 'Your prompt text' to create one.")


@config_cmd.command(name="list-local", cls=ConfigCommand)
@click.pass_context
def config_list_local(ctx: click.Context) -> None:
    """List all local configuration files in the .codemie directory.
    
    Shows all configuration files in the local .codemie directory with their status.
    """
    local_dir = get_local_config_dir()
    
    if not local_dir.exists():
        console.print(f"[{STYLE_WARNING}]No local configuration directory found at:[/] {local_dir}")
        return
    
    # Create a table for the local config files
    table = Table(title="Local Configuration Files")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Path", style="yellow")
    
    # Check for prompt.txt
    prompt_file = local_dir / LOCAL_CONFIG_PROMPT_FILE
    if prompt_file.exists():
        table.add_row(
            LOCAL_CONFIG_PROMPT_FILE,
            "[green]Active[/]",
            str(prompt_file)
        )
    else:
        table.add_row(
            LOCAL_CONFIG_PROMPT_FILE,
            "[dim]Not created[/]",
            str(prompt_file)
        )
    
    # Add other local config files if they exist
    for file in local_dir.iterdir():
        if file.is_file() and file.name != LOCAL_CONFIG_PROMPT_FILE:
            table.add_row(
                file.name,
                "[green]Active[/]",
                str(file)
            )
    
    console.print(table)

def _create_config_table() -> Table:
    """Create and configure a table for displaying configuration.
    
    Returns:
        A styled Rich Table object ready for configuration data
    """
    table = Table(title=TABLE_TITLE)
    table.add_column(COLUMN_KEY, style=STYLE_KEY)
    table.add_column(COLUMN_VALUE, style=STYLE_VALUE)
    table.add_column(COLUMN_SOURCE, style=STYLE_SOURCE)
    return table


def _format_value(value: Any) -> Any:
    """Format a configuration value for display.
    
    Detects and pretty-formats JSON values.
    
    Args:
        value: The configuration value to format
        
    Returns:
        A formatted representation of the value, suitable for display
    """
    # If it's already a string, try to parse it as JSON
    if isinstance(value, str):
        try:
            # Try to parse as JSON
            json_obj = json.loads(value)
            # If it's a dict or list, format it as pretty JSON
            if isinstance(json_obj, (dict, list)):
                json_str = json.dumps(json_obj, indent=2)
                return Syntax(json_str, "json", theme="monokai", word_wrap=True)
        except (json.JSONDecodeError, ValueError):
            # Not valid JSON, return as is
            return value
    
    # If it's a dict or list, format it as pretty JSON
    if isinstance(value, (dict, list)):
        json_str = json.dumps(value, indent=2)
        return Syntax(json_str, "json", theme="monokai", word_wrap=True)
    
    # For other types, convert to string
    return str(value)


def _populate_config_table(table: Table, keys: List[str], config: Dict[str, Any]) -> None:
    """Fill the table with configuration data.
    
    Args:
        table: The Rich Table to populate
        keys: List of configuration keys to check
        config: The loaded configuration dictionary
    """
    for key in keys:
        # Check environment first
        env_value = os.environ.get(key)
        file_value = config.get(key)
        
        if env_value is not None:
            formatted_value = _format_value(env_value)
            table.add_row(key, formatted_value, SOURCE_ENVIRONMENT)
        elif file_value is not None:
            formatted_value = _format_value(file_value)
            table.add_row(key, formatted_value, SOURCE_CONFIG_FILE)
        else:
            table.add_row(key, NOT_SET_TEXT, "")
