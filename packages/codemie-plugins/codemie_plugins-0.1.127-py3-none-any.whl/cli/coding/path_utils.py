"""
Path Utilities for CodeMie Tools

This module provides common utilities for path handling, filtering, and validation
that are used across multiple tools in the CodeMie codebase.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console

# Default patterns to ignore in directory operations
DEFAULT_IGNORE_PATTERNS = [
    'node_modules',
    'plugins',
    'dist',
    'build',
    '.git',
    '.vscode',
    '.idea',
    'coverage',
    '*.min.js',
    '*.bundle.js',
    '*.map',
    '__pycache__',
    '*.pyc',
    '*.egg-info',
    'venv',
    '.venv',
    'env',
    '.DS_Store',
    '.next',
    '.cache',
    'tmp',
    '*/.*',
    '.*',
    '.pytest_cache',
]

console = Console()

def normalize_path(path: str) -> str:
    """Normalize a path to its absolute form.

    Args:
        path: The path to normalize

    Returns:
        Normalized absolute path
    """
    expanded_path = os.path.expanduser(path) if path.startswith('~') else path
    absolute_path = os.path.abspath(expanded_path)
    return os.path.normpath(absolute_path)


def is_path_ignored(path_part: str, ignore_patterns: List[str]) -> bool:
    """Check if a path part matches any ignore pattern.

    Args:
        path_part: The path part to check
        ignore_patterns: List of patterns to check against

    Returns:
        True if the path part matches any ignore pattern, False otherwise
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path_part, pattern):
            return True
    return False


def format_allowed_dirs_message(allowed_dirs: List[str]) -> str:
    """Format a message with allowed directories.

    Args:
        allowed_dirs: List of allowed directories

    Returns:
        Formatted message with allowed directories
    """
    if not allowed_dirs:
        allowed_dirs = [os.getcwd()]
    return f"Please use one of the allowed directories: {', '.join(allowed_dirs)}"


def validate_path_against_ignore_patterns(path: str, allowed_dirs: List[str] = None) -> Optional[str]:
    """Validate if the path contains any ignored patterns.

    Args:
        path: The path to validate
        allowed_dirs: List of allowed directories

    Returns:
        Error message if path contains ignored patterns, None otherwise
    """
    normalized_path = normalize_path(path)
    basename = os.path.basename(normalized_path)

    # Check if the basename matches any ignore patterns
    for pattern in DEFAULT_IGNORE_PATTERNS:
        if fnmatch.fnmatch(basename, pattern):
            return f"The path '{path}' matches an ignored pattern '{pattern}'. {format_allowed_dirs_message(allowed_dirs)}"

    # Check if any parent directory matches any ignore patterns
    path_parts = Path(normalized_path).parts
    for part in path_parts:
        for pattern in DEFAULT_IGNORE_PATTERNS:
            if fnmatch.fnmatch(part, pattern):
                return f"The path '{path}' contains a part '{part}' that matches an ignored pattern '{pattern}'. {format_allowed_dirs_message(allowed_dirs)}"

    return None


def should_process_directory(dir_name: str, ignore_patterns: List[str], include_ignored: bool) -> bool:
    """Determine if a directory should be processed based on ignore patterns.

    Args:
        dir_name: The directory name to check
        ignore_patterns: List of patterns to ignore
        include_ignored: Whether to include directories that match ignore patterns

    Returns:
        True if the directory should be processed, False otherwise
    """
    if include_ignored:
        return True

    for pattern in ignore_patterns:
        if fnmatch.fnmatch(dir_name, pattern):
            return False
    return True


def should_process_file(file_path: str, ignore_patterns: List[str], include_ignored: bool) -> bool:
    """Determine if a file should be processed based on ignore patterns.

    Args:
        file_path: The file path to check
        ignore_patterns: List of patterns to ignore
        include_ignored: Whether to include files that match ignore patterns

    Returns:
        True if the file should be processed, False otherwise
    """
    if include_ignored:
        return True

    file_name = os.path.basename(file_path)
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return False
    return True


def process_directory_entry(
        entry: os.DirEntry,
        current_path: str,
        base_path: str,
        ignore_patterns: List[str],
        include_ignored: bool
) -> List[str]:
    """Process a directory entry and collect file paths.

    Args:
        entry: The directory entry to process
        current_path: The current directory path
        base_path: The base path to make paths relative to
        ignore_patterns: List of patterns to ignore
        include_ignored: Whether to include files that match ignore patterns

    Returns:
        List of file paths for this entry
    """
    entry_name = entry.name
    full_path = os.path.join(current_path, entry_name)
    rel_path = os.path.relpath(full_path, base_path)

    if entry.is_file():
        if should_process_file(full_path, ignore_patterns, include_ignored):
            return [rel_path]
        return []
    elif entry.is_dir():
        if should_process_directory(entry_name, ignore_patterns, include_ignored):
            return collect_all_files(full_path, base_path, ignore_patterns, include_ignored)
        return []

    return []


def collect_all_files(current_path: str, base_path: str = None, ignore_patterns: List[str] = None, include_ignored: bool = False) -> List[str]:
    """Collect all files recursively, optionally respecting ignore patterns.

    Args:
        current_path: The current directory path to scan
        base_path: The base path to make paths relative to (if None, uses current_path)
        ignore_patterns: List of patterns to ignore (if None, uses DEFAULT_IGNORE_PATTERNS)
        include_ignored: Whether to include files that match ignore patterns

    Returns:
        List of file paths (relative to base_path if provided)
    """
    if base_path is None:
        base_path = current_path

    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    # Get the current directory name
    dir_name = os.path.basename(current_path)

    # Skip this directory if it matches any ignore patterns and we're not including ignored files
    if not should_process_directory(dir_name, ignore_patterns, include_ignored):
        return []

    result = []
    try:
        with os.scandir(current_path) as it:
            for entry in it:
                result.extend(process_directory_entry(
                    entry, current_path, base_path, ignore_patterns, include_ignored
                ))
    except Exception as e:
        console.log(f"[red]Error collecting files in {current_path}: {str(e)}[/]")

    return result


def list_directory_entries(path: str, include_ignored: bool = False) -> List[Tuple[str, bool]]:
    """List directory entries, optionally filtering ignored patterns.

    Args:
        path: The path to list
        include_ignored: Whether to include entries that match ignore patterns

    Returns:
        List of tuples (entry_name, is_dir) for each entry in the directory
    """
    entries = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                entry_name = entry.name

                # Skip entries that match any of the ignore patterns if not including ignored
                if not include_ignored:
                    should_include = True
                    for pattern in DEFAULT_IGNORE_PATTERNS:
                        if fnmatch.fnmatch(entry_name, pattern):
                            should_include = False
                            break

                    if not should_include:
                        continue

                entries.append((entry_name, entry.is_dir()))
    except Exception as e:
        console.log(f"[red]Error listing directory {path}: {str(e)}[/]")

    return entries
