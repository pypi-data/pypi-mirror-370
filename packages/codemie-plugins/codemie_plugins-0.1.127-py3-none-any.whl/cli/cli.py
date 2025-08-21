"""Main CLI entry point for CodeMie Plugins.

This module provides the main command line interface for CodeMie Plugins,
allowing users to interact with the plugin system through various commands.
It handles configuration, sets up signal handlers for graceful shutdown,
and registers commands for the CLI.
"""
import atexit
import builtins
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, List, Optional

import click
from rich.console import Console

from cli.commands.code_cmd import code_cmd
from cli.commands.config_cmd import config_cmd
from cli.commands.custom_group import CustomGroup
from cli.commands.development_cmd import development_cmd
from cli.commands.list_cmd import list_cmd
from cli.commands.mcp_cmd import mcp_cmd
from cli.utils import get_config_value, print_banner

# Constants
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
SHUTDOWN_MESSAGE = "\n[yellow]Keyboard interrupt received, shutting down gracefully...[/]"

# Configuration keys
KEY_DEBUG = "DEBUG"
KEY_CONFIG = "CONFIG"
KEY_PLUGIN_KEY = "PLUGIN_KEY"
KEY_PLUGIN_ENGINE_URI = "PLUGIN_ENGINE_URI"
KEY_LLM_SERVICE_API_KEY = "LLM_SERVICE_API_KEY"
KEY_LLM_SERVICE_BASE_URL = "LLM_SERVICE_BASE_URL"

# Default values
DEFAULT_PLUGIN_ENGINE_URI = "nats://nats-codemie.epmd-edp-anthos.eu.gcp.cloudapp.epam.com:443"
DEFAULT_LLM_SERVICE_BASE_URL = "https://ai-proxy.lab.epam.com"

# CLI options
OPT_PLUGIN_KEY = "--plugin-key"
OPT_PLUGIN_ENGINE_URI = "--plugin-engine-uri"
OPT_LLM_SERVICE_API_KEY = "--llm-api-key"
OPT_LLM_SERVICE_BASE_URL = "--llm-base-url"
OPT_DEBUG = "--debug"

# CLI option descriptions
DESC_PLUGIN_KEY = "Authentication key for the plugin engine for runtime authentication during CLI execution"
DESC_PLUGIN_ENGINE_URI = f"URI for the plugin engine (typically a NATS server, defaults to {DEFAULT_PLUGIN_ENGINE_URI})"
DESC_LLM_SERVICE_API_KEY = "API key for OpenAI-compatible LLM service (ChatGPT, EPAM DIAL, or CodeMie)"
DESC_LLM_SERVICE_BASE_URL = f"Base URL for OpenAI-compatible LLM service (defaults to {DEFAULT_LLM_SERVICE_BASE_URL})"
DESC_DEBUG = "Enable debug mode"

# CLI info
CLI_NAME = "CodeMie Plugins CLI"

# Global objects
console = Console()

# Global registry of running processes to terminate on exit
# A process is any object with terminate(), cancel(), or close() method
RUNNING_PROCESSES: List[Any] = []

def print_version(ctx, param, value):
    """Custom version callback that shows the banner before printing version."""
    if not value or ctx.resilient_parsing:
        return
    
    # Print the banner first
    version = print_banner()
    
    # Then print version info in Click's format and exit
    click.echo(f"{CLI_NAME}, version {version}")
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, cls=CustomGroup)
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show version and exit')
@click.option(
    OPT_PLUGIN_KEY,
    envvar=KEY_PLUGIN_KEY,
    help=DESC_PLUGIN_KEY,
)
@click.option(
    OPT_PLUGIN_ENGINE_URI,
    envvar=KEY_PLUGIN_ENGINE_URI,
    help=DESC_PLUGIN_ENGINE_URI,
)
@click.option(
    OPT_LLM_SERVICE_API_KEY,
    envvar=KEY_LLM_SERVICE_API_KEY,
    help=DESC_LLM_SERVICE_API_KEY,
)
@click.option(
    OPT_LLM_SERVICE_BASE_URL,
    envvar=KEY_LLM_SERVICE_BASE_URL,
    help=DESC_LLM_SERVICE_BASE_URL,
)
@click.option(OPT_DEBUG, is_flag=True, default=False, help=DESC_DEBUG)
@click.pass_context
def cli(
    ctx: click.Context,
    plugin_key: Optional[str],
    plugin_engine_uri: Optional[str],
    llm_api_key: Optional[str],
    llm_base_url: Optional[str],
    debug: bool,
) -> None:
    """CodeMie Plugins CLI - Run CodeMie toolkits."""
    # Ensure the context object exists and is a dictionary
    ctx.ensure_object(dict)

    # Add project root to PYTHONPATH to ensure imports work correctly
    _add_project_root_to_path()

    # Banner is now printed by the CustomGroup.get_help method when no subcommand is provided
    # For subcommands, we still want to print the banner here
    if ctx.invoked_subcommand is not None:
        print_banner()

    # Store configuration in context
    ctx.obj[KEY_DEBUG] = debug
    ctx.obj[KEY_CONFIG] = {
        KEY_PLUGIN_KEY: plugin_key,
        KEY_PLUGIN_ENGINE_URI: plugin_engine_uri,
        KEY_LLM_SERVICE_API_KEY: llm_api_key,
        KEY_LLM_SERVICE_BASE_URL: llm_base_url,
    }

    # Resolve configuration values from multiple sources
    resolved_plugin_key = plugin_key or os.getenv(KEY_PLUGIN_KEY) or get_config_value(KEY_PLUGIN_KEY)
    resolved_plugin_engine_uri = (
        plugin_engine_uri
        or os.getenv(KEY_PLUGIN_ENGINE_URI)
        or get_config_value(KEY_PLUGIN_ENGINE_URI)
        or DEFAULT_PLUGIN_ENGINE_URI
    )
    resolved_llm_api_key = (
        llm_api_key
        or os.getenv(KEY_LLM_SERVICE_API_KEY)
        or get_config_value(KEY_LLM_SERVICE_API_KEY)
    )
    resolved_llm_base_url = (
        llm_base_url
        or os.getenv(KEY_LLM_SERVICE_BASE_URL)
        or get_config_value(KEY_LLM_SERVICE_BASE_URL)
        or DEFAULT_LLM_SERVICE_BASE_URL
    )

    # Set environment variables for nested commands
    if resolved_plugin_key:
        os.environ[KEY_PLUGIN_KEY] = resolved_plugin_key
    # Always set the plugin engine URI (using default if not provided)
    os.environ[KEY_PLUGIN_ENGINE_URI] = resolved_plugin_engine_uri
    
    # Set LLM service environment variables
    if resolved_llm_api_key:
        os.environ[KEY_LLM_SERVICE_API_KEY] = resolved_llm_api_key
        # Also set OPENAI_API_KEY for compatibility with libraries that use it directly
        os.environ["OPENAI_API_KEY"] = resolved_llm_api_key
    
    # Always set the LLM base URL (using default if not provided)
    os.environ[KEY_LLM_SERVICE_BASE_URL] = resolved_llm_base_url
    # Also set OPENAI_BASE_URL for compatibility with libraries that use it directly
    os.environ["OPENAI_BASE_URL"] = resolved_llm_base_url

    # Set up logging if debug is enabled
    if debug:
        # Import and use the Rich logger instead of basic logging
        # Just set the httpx logger level without reconfiguring the root logger
        logging.getLogger("httpx").setLevel(level=logging.DEBUG)
    else:
        logging.getLogger("httpx").setLevel(level=logging.WARNING)

    # Setup signal handlers for graceful shutdown
    _setup_graceful_shutdown()


def _add_project_root_to_path() -> None:
    """Add the project root directory to Python path for imports."""
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def _setup_graceful_shutdown() -> None:
    """Configure signal handlers to ensure graceful shutdown."""
    # Register cleanup function to be called at exit
    atexit.register(_cleanup_processes)

    # Register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)


def _cleanup_processes():
    """Clean up all registered processes on exit."""
    for process in RUNNING_PROCESSES:
        if hasattr(process, "terminate") and callable(process.terminate):
            process.terminate()
        elif hasattr(process, "cancel") and callable(process.cancel):
            process.cancel()
        elif hasattr(process, "close") and callable(process.close):
            process.close()


def _signal_handler(sig: int, frame: Any) -> None:
    """Handle termination signals by cleaning up and exiting.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    console.print(SHUTDOWN_MESSAGE, highlight=False)
    _cleanup_processes()
    sys.exit(0)


def register_process(process: Any) -> None:
    """Register a process to be terminated on exit.
    
    Args:
        process: Any process-like object with terminate(), cancel(), or close() method
    """
    RUNNING_PROCESSES.append(process)


# Global function name used by other modules
REGISTER_PROCESS_NAME = "register_codemie_process"

# Make the register_process function available to all modules
setattr(builtins, REGISTER_PROCESS_NAME, register_process)


# Add commands to the CLI group
cli.add_command(list_cmd)
cli.add_command(config_cmd)
cli.add_command(mcp_cmd)
cli.add_command(development_cmd)
cli.add_command(code_cmd)


if __name__ == "__main__":
    cli(obj={})
