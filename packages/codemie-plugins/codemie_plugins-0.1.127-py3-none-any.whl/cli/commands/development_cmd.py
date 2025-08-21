"""Commands for development toolkit functionality."""
import asyncio
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console

from cli.commands.custom_group import CustomGroup
from cli.utils import register_for_graceful_shutdown
from codemie.client import PluginClient
from toolkits.development.toolkit import FileSystemAndCommandToolkit

console = Console()

class DevelopmentGroup(CustomGroup):

    def _get_command_examples(self, ctx: click.Context) -> str:
        return (
            "# Run development toolkit on current directory\n"
            "codemie-plugins development run\n\n"
            "# Run development toolkit on a specific repository\n"
            "codemie-plugins development run --repo-path /path/to/repo\n\n"
            "# Run with a custom timeout\n"
            "codemie-plugins development run --timeout 600"
        )


@click.group(name="development", cls=DevelopmentGroup)
@click.pass_context
def development_cmd(ctx: Dict[str, Any]) -> None:
    """Development toolkit commands for working with repositories."""
    pass


def setup_environment(repo_path: str, timeout: Optional[int] = None) -> None:
    """Set up environment variables for the development toolkit.
    
    Args:
        repo_path: Path to the repository directory
        timeout: Optional timeout in seconds for command execution
    """
    os.environ['REPO_FILE_PATH'] = str(repo_path)
    
    if timeout:
        os.environ['COMMAND_LINE_TOOL_TIMEOUT'] = str(timeout)


def setup_python_path() -> str:
    """Add the project root to sys.path to ensure imports work.
    
    Returns:
        str: The project root path
    """
    project_root = str(Path(__file__).parents[2])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return project_root


def print_debug_info(ctx: Dict[str, Any], repo_path: str, project_root: str) -> None:
    """Print debug information if debug mode is enabled.
    
    Args:
        ctx: Click context object
        repo_path: Path to the repository
        project_root: Project root path
    """
    if ctx.obj and ctx.obj.get('DEBUG'):
        console.print(f"[dim]Python path: {sys.path}[/dim]")
        console.print(f"[dim]REPO_FILE_PATH: {repo_path}[/dim]")
        console.print(f"[dim]Project root: {project_root}[/dim]")


def import_dependencies():
    """Import required dependencies for the development toolkit.
    
    Returns:
        tuple: Imported modules (PluginClient, FileSystemAndCommandToolkit)
        
    Raises:
        ImportError: If dependencies cannot be imported
    """

    return PluginClient, FileSystemAndCommandToolkit


async def run_toolkit_service(
    repo_path: str, 
    plugin_client_cls: Any, 
    toolkit_cls: Any, 
    debug_mode: bool
) -> None:
    """Run the development toolkit service.
    
    Args:
        repo_path: Path to the repository
        plugin_client_cls: PluginClient class
        toolkit_cls: FileSystemAndCommandToolkit class
        debug_mode: Whether debug mode is enabled
    """
    plugin_label = os.path.basename(repo_path)
    os.environ["PLUGIN_LABEL"] = plugin_label
    toolkit_timeout = int(os.getenv('COMMAND_LINE_TOOL_TIMEOUT', '300'))
    plugin = None
    
    try:
        # Create the plugin
        toolkit = toolkit_cls()
        tools = toolkit.get_tools(repo_path)
        plugin = plugin_client_cls(tools=tools, timeout=toolkit_timeout)
        
        # Register the plugin for graceful shutdown
        register_for_graceful_shutdown(plugin)
        
        # Connect to the plugin engine
        await plugin.connect()
        
        # Keep the connection alive until terminated
        await maintain_connection()
            
    except asyncio.CancelledError:
        console.print("[yellow]Development toolkit execution was cancelled[/]")
        if plugin and hasattr(plugin, "close"):
            await plugin.close()
    except Exception as e:
        console.print(f"[bold red]Error in development toolkit:[/] {str(e)}")
        if debug_mode:
            console.print(traceback.format_exc())
    finally:
        # Ensure proper cleanup
        if plugin and hasattr(plugin, "close"):
            try:
                await plugin.close()
            except Exception:
                pass


async def maintain_connection() -> None:
    """Maintain the connection to the plugin engine until terminated."""
    while True:
        await asyncio.sleep(1)


def handle_import_error(error: ImportError) -> None:
    """Handle import errors with helpful messages.
    
    Args:
        error: The import error that occurred
    """
    console.print(f"[bold red]Import error with dependencies:[/] {str(error)}")
    console.print("[yellow]Make sure the codemie package is installed correctly.[/]")
    console.print("[yellow]Try installing with: pip install -e .[/]")


def print_startup_message(repo_path: str) -> None:
    """Print startup message for the development toolkit.
    
    Args:
        repo_path: Path to the repository
    """
    console.print(f"[bold green]Running development toolkit on:[/] {repo_path}")
    console.print("[dim]Press Ctrl+C to exit gracefully[/]")


def run_async_toolkit(toolkit_coroutine: Any, debug_mode: bool) -> None:
    """Run the async toolkit with proper exception handling.
    
    Args:
        toolkit_coroutine: Coroutine to run
        debug_mode: Whether debug mode is enabled
    """
    try:
        asyncio.run(toolkit_coroutine)
    except KeyboardInterrupt:
        console.print("\n[yellow]Keyboard interrupt received, shutting down development toolkit...[/]")
    except Exception as e:
        console.print(f"[bold red]Error in development toolkit execution loop:[/] {str(e)}")
        if debug_mode:
            console.print(traceback.format_exc())


@development_cmd.command(name="run")
@click.option('--repo-path', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
              help="Path to the repository directory")
@click.option('--timeout', '-t', type=int, help="Timeout in seconds for command execution")
@click.pass_context
def dev_run(ctx: Dict[str, Any], repo_path: Optional[str] = None, timeout: Optional[int] = None) -> None:
    """Run development toolkit on a repository.
    
    If --repo-path is not provided, uses current directory.
    """
    # Use current directory if repo_path not provided
    repo_path = repo_path or os.getcwd()
    debug_mode = bool(ctx.obj and ctx.obj.get('DEBUG'))
    
    try:
        # Setup environment and paths
        setup_environment(repo_path, timeout)
        project_root = setup_python_path()
        print_debug_info(ctx, repo_path, project_root)

        # Import dependencies
        try:
            plugin_client, file_system_toolkit = import_dependencies()
        except ImportError as e:
            handle_import_error(e)
            return

        # Print startup message
        print_startup_message(repo_path)
        
        # Create and run the toolkit service
        toolkit_coroutine = run_toolkit_service(
            repo_path, 
            plugin_client, 
            file_system_toolkit,
            debug_mode
        )
        run_async_toolkit(toolkit_coroutine, debug_mode)
            
    except Exception as e:
        console.print(f"[bold red]Error running development toolkit:[/] {str(e)}")
        if debug_mode:
            console.print(traceback.format_exc())
