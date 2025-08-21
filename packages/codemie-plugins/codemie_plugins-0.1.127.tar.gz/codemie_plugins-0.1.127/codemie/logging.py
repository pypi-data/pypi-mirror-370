"""Module for logger configuration and usage with Rich Console for better UX."""
import contextlib
import logging
from typing import Any, Generator, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Define a custom theme for logging
LOG_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "debug": "dim blue",
    "critical": "bold white on red",
})

# Create Rich console with custom theme
console = Console(theme=LOG_THEME, highlight=True)

# Configure logging with Rich handler
# Use force=True to override any existing configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Just the message, Rich will handle the formatting
    datefmt="%H:%M:%S",  # Simpler time format
    handlers=[RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        omit_repeated_times=True,  # Avoid repeating timestamps
        show_time=False,  # Don't show time in the log message to match fancy logs
        show_path=False,  # Don't show the path
        show_level=False,  # Don't show the level in the log message
        log_time_format="%H:%M:%S"  # Won't be used with show_time=False
    )],
    force=True  # Force this configuration to override any existing ones
)

# Remove all other handlers from the root logger to ensure our configuration is used
for handler in logging.root.handlers[:]:
    if not isinstance(handler, RichHandler):
        logging.root.removeHandler(handler)

# Get the base logger
_logger = logging.getLogger("codemie")


class RichLogger:
    """Enhanced logger using Rich for better UX."""
    
    def __init__(self, name: str = "codemie"):
        self._logger = logging.getLogger(name)
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message with Rich formatting."""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message with Rich formatting."""
        # Remove any existing Rich markup tags to avoid duplication
        clean_message = self._clean_markup(message)
        self._logger.info(f"[cyan]{clean_message}[/cyan]", *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message with Rich formatting."""
        clean_message = self._clean_markup(message)
        self._logger.warning(f"[yellow]⚠️ {clean_message}[/yellow]", *args, **kwargs)
    
    def error(self, message: str, *args: Any, exc_info: Optional[bool] = None, **kwargs: Any) -> None:
        """Log error message with Rich formatting and optional traceback."""
        clean_message = self._clean_markup(message)
        self._logger.error(f"[bold red]❌ {clean_message}[/bold red]", *args, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, *args: Any, exc_info: Optional[bool] = None, **kwargs: Any) -> None:
        """Log critical message with Rich formatting and optional traceback."""
        clean_message = self._clean_markup(message)
        self._logger.critical(f"[bold white on red]🚨 {clean_message}[/bold white on red]", *args, exc_info=exc_info, **kwargs)
        
    def _clean_markup(self, message: str) -> str:
        """Remove any existing Rich markup tags to avoid duplication."""
        import re
        # Remove common Rich markup patterns like [info]...[/info], [cyan]...[/cyan], etc.
        return re.sub(r'\[(\w+)\](.*?)\[/\1\]', r'\2', str(message))
    
    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log exception message with Rich formatting and traceback."""
        clean_message = self._clean_markup(message)
        self._logger.exception(f"[bold red]❌ {clean_message}[/bold red]", *args, **kwargs)
    
    def log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        """Log message with specified level and Rich formatting."""
        self._logger.log(level, message, *args, **kwargs)
    
    @contextlib.contextmanager
    def safe_status(self, message: str, spinner: str = "dots") -> Generator[None, None, None]:
        """A safer context manager for Rich status displays.
        
        This context manager will fall back to simple progress messages if a live display
        cannot be created, ensuring that the code continues to work even if there are
        issues with Rich's live displays.
        
        Args:
            message: The status message to display
            spinner: The spinner animation to use
            
        Yields:
            None
        """
        status_obj = None
        try:
            # Only try to create a status if there's no live display already active
            if not hasattr(console, "_live") or console._live is None:
                status_obj = console.status(message, spinner=spinner)
                status_obj.__enter__()
            else:
                # If there's already a live display, use progress instead
                self.progress(message)
        except Exception as e:
            # If there's an error creating the status display, fall back to progress
            self.progress(message)
            status_obj = None
            
        try:
            # Yield control back to the caller
            yield
        finally:
            # Clean up the status display if it was created
            if status_obj is not None:
                try:
                    status_obj.__exit__(None, None, None)
                except Exception:
                    pass
                    
    def status(self, message: str, spinner: str = "dots") -> Any:
        """Create and return a Rich status context manager.
        
        Note: Only one status can be active at a time. Using multiple
        status displays simultaneously will cause errors.
        
        Args:
            message: The status message to display
            spinner: The spinner animation to use
            
        Returns:
            A context manager for the status display or None if there's an error
        """
        # Check if there's already a live display active
        if hasattr(console, "_live") and console._live is not None:
            # If there's already a live display, use progress() instead as a safer alternative
            self.progress(message)
            return None
            
        try:
            # Try to create a new status display
            return console.status(message, spinner=spinner)
        except Exception as e:
            # If there's an error creating the status display, fall back to progress()
            if "Only one live display may be active at once" in str(e):
                self.progress(message)
                return None
            else:
                # For other errors, just print the message and return None
                console.print(message)
                return None
    
    def rule(self, title: str = "", **kwargs: Any) -> None:
        """Print a horizontal rule with optional title."""
        console.rule(title, **kwargs)
    
    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to console with Rich formatting."""
        console.print(*args, **kwargs)
        
    def progress(self, message: str, complete: bool = False) -> None:
        """Print a progress message with optional completion indicator.
        
        This is a safer alternative to status() when you need to show progress
        without using a live display that could conflict with other displays.
        
        Args:
            message: The progress message to display
            complete: Whether this is a completion message (adds checkmark)
        """
        try:
            if complete:
                console.print(f"[bold green]✓[/bold green] {message}")
            else:
                console.print(f"[bold cyan]→[/bold cyan] {message}")
        except Exception as e:
            # Fallback if Rich formatting fails
            if complete:
                print(f"✓ {message}")
            else:
                print(f"→ {message}")


# Create the enhanced logger instance for import
logger = RichLogger()

