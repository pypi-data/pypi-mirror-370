"""Custom Click Command implementation for CodeMie Plugins CLI.

This module provides a custom Click Command class that enhances the CLI with rich
formatting, consistent help display, and other features.
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from cli.utils import print_banner

# Global objects
console = Console()


class CustomCommand(click.Command):
    """Custom Click Command that shows the banner and formatted help."""
    
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
        
        # Print usage panel with examples
        self._print_usage_panel(ctx)

        # Print options table
        self._print_options_table(ctx)
        
        # Print arguments table if any
        self._print_arguments_table(ctx)
    
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
        # Filter out arguments (positional parameters)
        options = [param for param in ctx.command.params if not param]
        
        if not options:
            return
            
        options_table = Table(title="Options", box=box.ROUNDED, border_style="blue", expand=False)
        options_table.add_column("Option", style="green")
        options_table.add_column("Description", style="white")
        options_table.add_column("Default", style="yellow")
        
        for param in options:
            if param.hidden:
                continue
            
            option_name = self._format_option_name(param)
            help_text = param.help or ""
            default = self._format_default_value(param)
            
            options_table.add_row(option_name, help_text, default)
        
        console.print(options_table)
    
    def _print_arguments_table(self, ctx: click.Context) -> None:
        """Print a table containing the command arguments."""
        # Filter to only include arguments (positional parameters)
        arguments = [param for param in ctx.command.params if param]
        
        if not arguments:
            return
            
        args_table = Table(title="Arguments", box=box.ROUNDED, border_style="blue", expand=False)
        args_table.add_column("Argument", style="green")
        args_table.add_column("Description", style="white")
        args_table.add_column("Required", style="yellow")
        
        for param in arguments:
            if param.hidden:
                continue
            
            arg_name = param.name
            help_text = param.help or ""
            required = "Yes" if param.required else "No"
            
            args_table.add_row(arg_name, help_text, required)
        
        console.print(args_table)
    
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
        """Get command-specific examples for the help text.
        
        This method should be implemented by child classes to provide
        command-specific examples. The base implementation provides
        a default example.
        """
        # Get the full command path
        command_path = self._get_command_path(ctx)
        
        # Default examples if no specific ones are available
        return (
            f"# Get help for this command\n"
            f"{command_path} --help"
        )
    
    def _get_command_path(self, ctx: click.Context) -> str:
        """Get the full command path for use in examples."""
        parts = ["codemie-plugins"]

        # Build the command path by traversing up the context hierarchy
        cmd_path = []
        current_ctx = ctx
        while current_ctx is not None and current_ctx.command.name != "cli":
            cmd_path.insert(0, current_ctx.command.name)
            current_ctx = current_ctx.parent
            
        parts.extend(cmd_path)
        return " ".join(parts)