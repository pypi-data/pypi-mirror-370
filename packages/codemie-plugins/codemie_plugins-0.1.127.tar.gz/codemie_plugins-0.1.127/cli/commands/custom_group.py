"""Custom Click Group implementation for CodeMie Plugins CLI.

This module provides a custom Click Group class that enhances the CLI with rich
formatting, consistent help display, and other features.
"""
import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.utils import print_banner

# Global objects
console = Console()


class CustomGroup(click.Group):
    """Custom Click Group that shows the banner and formatted help."""
    
    def get_help(self, ctx: click.Context) -> str:
        """Override get_help to show banner and formatted help text."""
        # Print the banner first
        print_banner()
        
        # Format and display help in a pretty way using Rich
        self._format_help_with_rich(ctx)
        
        # Return empty string since we've already printed the help
        return ""
    
    def _format_help_with_rich(self, ctx: click.Context) -> None:
        """Format and display help using Rich tables."""
        # Print description panel
        self._print_description_panel(ctx)
        
        # Print commands table if this is a group
        if isinstance(ctx.command, click.Group):
            self._print_commands_table(ctx)
        
        # Print usage panel with examples
        self._print_usage_panel(ctx)

        # Print options table
        self._print_options_table(ctx)
    
    def _print_description_panel(self, ctx: click.Context) -> None:
        """Print a panel containing the command description."""
        description = ctx.command.help or "No description available."
        desc_panel = Panel(
            Text(description, style="cyan"),
            border_style="blue",
            title="Description",
            expand=False
        )
        console.print(desc_panel)
    
    def _print_options_table(self, ctx: click.Context) -> None:
        """Print a table containing the command options."""
        options_table = Table(title="Options", box=box.ROUNDED, border_style="blue", expand=False)
        options_table.add_column("Option", style="green")
        options_table.add_column("Description", style="white")
        options_table.add_column("Default", style="yellow")
        
        for param in ctx.command.params:
            if param.hidden:
                continue
            
            option_name = self._format_option_name(param)
            help_text = param.help or ""
            default = self._format_default_value(param)
            
            options_table.add_row(option_name, help_text, default)
        
        console.print(options_table)
    
    def _format_option_name(self, param) -> str:
        """Format the option name from parameter opts and secondary_opts."""
        names = []
        names.extend(param.opts)
        names.extend(param.secondary_opts)
        return ", ".join(names)
    
    def _format_default_value(self, param) -> str:
        """Format the default value for a parameter."""
        if param.default is not None and param.default != "" and not param.is_flag:
            return str(param.default)
        elif param.is_flag and param.default:
            return "Enabled"
        elif param.is_flag:
            return "Disabled"
        return ""
    
    def _print_commands_table(self, ctx: click.Context) -> None:
        """Print a table containing the available commands."""
        commands = getattr(ctx.command, "commands", {})
        if not commands:
            return
            
        commands_table = Table(title="Commands", box=box.ROUNDED, border_style="blue", expand=False)
        commands_table.add_column("Command", style="green")
        commands_table.add_column("Description", style="white")
        
        # Sort commands by name
        command_list = sorted(commands.items(), key=lambda x: x[0])
        
        # Add each command to the table
        for cmd_name, cmd in command_list:
            cmd_help = cmd.get_short_help_str(limit=300) or "No description available."
            commands_table.add_row(cmd_name, cmd_help)
        
        console.print(commands_table)
    
    def _print_usage_panel(self, ctx: click.Context) -> None:
        """Print a panel containing usage information and examples."""
        usage_text = self.get_usage(ctx)
        examples = self._get_command_examples(ctx)
        
        usage_panel = Panel(
            Text.assemble(
                Text(usage_text + "\n\n", style="white"),
                Text("Examples:\n", style="bold yellow"),
                Text(examples, style="green")
            ),
            border_style="blue",
            title="Usage",
            expand=False
        )
        console.print(usage_panel)
        
    def _get_command_examples(self, ctx: click.Context) -> str:
        """Get command-specific examples for the help text."""
        # Base examples for the main CLI
        if ctx.command.name == "cli" and not ctx.parent:
            return (
                "# Show CLI version\n"
                "codemie-plugins --version\n\n"
                "# Generate a plugin key and set it automatically\n"
                "codemie-plugins config generate-key\n\n"
                "# Configure your plugin key manually with own value\n"
                "codemie-plugins config set PLUGIN_KEY your-plugin-key\n\n"
                "# Configure LLM service API key\n"
                "codemie-plugins config set LLM_SERVICE_API_KEY your-api-key\n\n"
                "# Configure LLM service base URL\n"
                "codemie-plugins config set LLM_SERVICE_BASE_URL https://your-llm-service.com\n\n"
                "# List available MCP servers\n"
                "codemie-plugins mcp list\n\n"
                "# Run MCP with JetBrains IDE servers\n"
                "codemie-plugins mcp run -s jetbrains\n\n"
                "# Run MCP with filesystem and CLI servers\n"
                "codemie-plugins mcp run -s filesystem,cli-mcp-server\n\n"
                "# Run development toolkit on a repository\n"
                "codemie-plugins development run --repo-path /path/to/repo\n\n"
                "# Start interactive coding assistant\n"
                "codemie-plugins code\n\n"
                "# Enable verbose mode for mcp command\n"
                "codemie-plugins mcp run -s jetbrains -v\n\n"
                "# Using uvx for isolated environment\n"
                "uvx codemie-plugins mcp list\n\n"
                "# Run development with uvx\n"
                "uvx codemie-plugins mcp run -s jetbrains"
            )
        
        # Default examples if no specific ones are available
        command_name = ctx.command.name
        return (
            "# Get help for this command\n"
            f"codemie-plugins {command_name} --help"
        )