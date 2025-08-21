"""Utility functions for the CodeMie Plugins CLI.

This module provides common utilities for the CodeMie Plugins CLI,
including configuration management, toolkit discovery, and display helpers.
"""

import asyncio
import builtins
import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pyfiglet
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Console instance for rich text output
console = Console()

# Configuration paths
CONFIG_DIR = Path.home() / ".codemie"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOCAL_CONFIG_DIR_NAME = ".codemie"
LOCAL_CONFIG_PROMPT_FILE = "prompt.txt"

# Banner styling constants
BANNER_FONT_MAIN = "slant"
BANNER_FONT_SECONDARY = "small"
BANNER_BORDER_STYLE = "cyan"
BANNER_MAIN_COLOR = "cyan"
BANNER_SECONDARY_COLOR = "bold blue"
BANNER_PADDING = 10
BANNER_BOX_STYLE = box.ROUNDED

# Error and message constants
ERROR_INVALID_JSON = "[bold red]Error:[/] Config file is invalid JSON"
ERROR_CONFIG_SAVE = "[bold red]Error saving configuration:[/] {}"
ERROR_IMPORT_TOOLKIT = "[yellow]Warning: Could not import {}: {}[/]"
ERROR_VERSION_READ = "[yellow]Warning: Could not read version, using default[/]"

# Application constants
DEFAULT_VERSION = "0.1.119"
PROJECT_NAME = "codemie-plugins"
PYPROJECT_PATH = "pyproject.toml"
VERSION_SECTION_POETRY = "tool.poetry"
VERSION_PROPERTY = "version"


def print_banner() -> str:
    """Print a professional welcome banner for the CLI using pyfiglet.
    
    Displays a styled banner with the CodeMie logo, version information,
    and basic usage instructions.
    
    Returns:
        str: The version string displayed in the banner.
    """
    version = get_version()

    # Create logo using pyfiglet for "CodeMie" with a compact font
    figlet = pyfiglet.Figlet(font=BANNER_FONT_MAIN)
    codemie_text = figlet.renderText("CodeMie")

    # Create colored logo text
    logo = Text()
    for line in codemie_text.rstrip().split("\n"):
        logo.append(f"{line}\n", style=BANNER_MAIN_COLOR)

    # Create "PLUGINS" text with a different font
    plugins_figlet = pyfiglet.Figlet(font=BANNER_FONT_SECONDARY)
    plugins_text = plugins_figlet.renderText("PLUGINS")

    # Format plugins text with bold styling
    plugins_styled = Text()
    for line in plugins_text.rstrip().split("\n"):
        plugins_styled.append(f"{line}\n", style=BANNER_SECONDARY_COLOR)

    # Information and version
    info = Text()
    info.append("\nToolkits for efficient development workflows\n", style="cyan")
    info.append("Get started with: ", style="white")
    info.append("codemie-plugins --help\n", style="yellow")
    info.append("Version: ", style="white")
    info.append(f"v{version}", style="green")

    # Build the complete banner with all components
    banner_content = Text.assemble(
        logo,
        plugins_styled,
        info
    )

    # Calculate width based on longest line in the figlet text
    max_width = max(
        max(len(line) for line in codemie_text.split("\n")),
        max(len(line) for line in plugins_text.split("\n"))
    ) + BANNER_PADDING  # Add some padding

    # Put everything in a compact panel
    banner = Panel(
        banner_content,
        border_style=BANNER_BORDER_STYLE,
        box=BANNER_BOX_STYLE,
        width=max_width,
        title="[bold blue]CodeMie Ecosystem[/]",
        subtitle=f"[dim]© {datetime.now().year} CodeMie Team[/]"
    )

    console.print(banner)
    return version


def get_version() -> str:
    """Get the current version of the CodeMie Plugins CLI.
    
    Retrieves version from the installed package metadata first (for PyPI installations),
    then falls back to reading pyproject.toml directly (for development).
    
    Returns:
        str: The version string of the package.
    """
    try:
        # First try to get version from the installed package metadata
        # This handles the PyPI installation case when run via uvx
        import importlib.metadata
            
        try:
            # Try to get version from package metadata (works for installed packages, including via uvx)
            return importlib.metadata.version(PROJECT_NAME)
        except importlib.metadata.PackageNotFoundError:
            # If the package is not installed, fall back to pyproject.toml
            console.print("[yellow]Package not found in metadata, falling back to pyproject.toml[/]", style="dim")
                    
        # Development case - try to load from pyproject.toml
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / PYPROJECT_PATH

        if not pyproject_path.exists():
            console.print(f"[yellow]pyproject.toml not found at {pyproject_path}, using default version[/]", style="dim")
            return DEFAULT_VERSION

        # Read raw content and parse TOML sections manually
        # to avoid additional dependencies
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple version extraction for "version" in [tool.poetry] section
        import re
        version_match = re.search(
            r'\[tool\.poetry\][^\[]*?version\s*=\s*["\']([^"\']+)["\']',
            content,
            re.DOTALL
        )

        if version_match:
            version = version_match.group(1)
            console.print(f"[green]Found version {version} in pyproject.toml[/]", style="dim")
            return version

        console.print("[yellow]Version not found in pyproject.toml, using default version[/]", style="dim")
        return DEFAULT_VERSION

    except Exception as e:
        console.print(f"{ERROR_VERSION_READ}: {e}")
        return DEFAULT_VERSION


def get_local_config_dir() -> Path:
    """Get the path to the local configuration directory.
    
    Returns:
        Path: The path to the local configuration directory (.codemie in current directory).
    """
    return Path.cwd() / LOCAL_CONFIG_DIR_NAME

def get_local_config_file(filename: str) -> Path:
    """Get the path to a specific local configuration file.
    
    Args:
        filename: The name of the configuration file.
        
    Returns:
        Path: The path to the specified local configuration file.
    """
    return get_local_config_dir() / filename

def load_config() -> Dict[str, Any]:
    """Load configuration from the config file.
    
    Returns:
        Dict[str, Any]: The configuration dictionary or an empty dict if no
                      configuration exists or an error occurs.
    """
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print(ERROR_INVALID_JSON)
        return {}
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to the config file.
    
    Args:
        config: Dictionary containing configuration values to save.
        
    Returns:
        bool: True if the save was successful, False otherwise.
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        console.print(ERROR_CONFIG_SAVE.format(str(e)))
        return False


def load_local_config_file(filename: str) -> Optional[str]:
    """Load content from a local configuration file.
    
    Args:
        filename: The name of the local configuration file to load.
        
    Returns:
        Optional[str]: The content of the file, or None if the file doesn't exist or an error occurs.
    """
    file_path = get_local_config_file(filename)
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading local config file {filename}:[/] {str(e)}")
        return None

def save_local_config_file(filename: str, content: str) -> bool:
    """Save content to a local configuration file.
    
    Args:
        filename: The name of the local configuration file to save.
        content: The content to write to the file.
        
    Returns:
        bool: True if the save was successful, False otherwise.
    """
    local_config_dir = get_local_config_dir()
    local_config_dir.mkdir(exist_ok=True)
    
    try:
        with open(local_config_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        console.print(f"[bold red]Error saving local config file {filename}:[/] {str(e)}")
        return False

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value with fallback to environment and default.
    
    The function checks environment variables first, then the config file,
    and finally falls back to the provided default value.
    
    Args:
        key: The configuration key to look up.
        default: The default value to return if the key is not found.
        
    Returns:
        Any: The configuration value or default.
    """
    # First check environment variables
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value
    
    # Then check config file
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> bool:
    """Set a configuration value in the config file.
    
    Args:
        key: The configuration key to set.
        value: The value to assign to the key.
        
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    config = load_config()
    config[key] = value
    return save_config(config)


def get_available_toolkits() -> List[str]:
    """Get a list of available toolkit names.
    
    Discovers toolkit directories that have a main.py file.
    
    Returns:
        List[str]: A list of toolkit names.
    """
    # Find the toolkits directory relative to this file
    toolkits_dir = Path(__file__).parent.parent / "toolkits"
    
    if not toolkits_dir.exists() or not toolkits_dir.is_dir():
        return []
    
    # Get directories from the toolkits folder that have a main.py file
    toolkits = []
    for item in toolkits_dir.iterdir():
        main_file_exists = item.is_dir() and not item.name.startswith('__') and (item / 'main.py').exists()
        if main_file_exists:
            toolkits.append(item.name)
    
    return sorted(toolkits)  # Sort for consistent output


def find_toolkit_module(name: str) -> Optional[str]:
    """Find the module path for a toolkit by name.
    
    Args:
        name: The name of the toolkit to find.
        
    Returns:
        Optional[str]: The module path if found, None otherwise.
    """
    # Ensure the project root is in sys.path
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Check if the toolkit directory exists
    toolkits_dir = Path(project_root) / "toolkits"
    toolkit_dir = toolkits_dir / name
    
    if not toolkit_dir.exists() or not toolkit_dir.is_dir():
        return None
        
    # Check if main.py exists in the toolkit directory
    if not (toolkit_dir / "main.py").exists():
        return None
        
    # Return the module path
    toolkit_path = f"toolkits.{name}"
    try:
        __import__(toolkit_path)
        return toolkit_path
    except ImportError as e:
        console.print(ERROR_IMPORT_TOOLKIT.format(toolkit_path, e))
        return None


def safe_cancel_task(task: asyncio.Task) -> bool:
    """Safely cancel an asyncio task without raising exceptions.
    
    Args:
        task: The asyncio task to cancel.
        
    Returns:
        bool: True if the task was cancelled, False if it was already done.
    """
    if task.done():
        return False
        
    task.cancel()
    
    # We need to suppress the CancelledError that would be raised when
    # the task is awaited after cancellation
    if sys.version_info >= (3, 8):
        # Python 3.8+ has a cleaner way to suppress the exception
        try:
            asyncio.get_event_loop().run_until_complete(
                _suppress_cancelled_error(task)
            )
        except (RuntimeError, asyncio.CancelledError):
            # Handle case where event loop is closed or not in the main thread
            pass
    
    return True


async def _suppress_cancelled_error(task: asyncio.Task) -> None:
    """Suppress CancelledError when awaiting a cancelled task.
    
    Args:
        task: The asyncio task that might raise CancelledError.
    """
    try:
        await task
    except asyncio.CancelledError:
        pass


def register_for_graceful_shutdown(
    obj: Union[asyncio.Task, asyncio.Future, threading.Thread, Any]
) -> bool:
    """Register an object to be gracefully shut down when the program exits.
    
    Args:
        obj: The object to register. Can be an asyncio.Task, asyncio.Future,
             threading.Thread, subprocess.Popen, or any object with a close(),
             terminate() or cancel() method.
    
    Returns:
        bool: True if the registration was successful, False otherwise.
    """
    try:
        if hasattr(builtins, 'register_codemie_process'):
            builtins.register_codemie_process(obj)
            return True
    except (NameError, AttributeError):
        # If the builtins function isn't available (because setup_graceful_shutdown
        # hasn't been called yet), we don't register the object
        pass
    
    return False
