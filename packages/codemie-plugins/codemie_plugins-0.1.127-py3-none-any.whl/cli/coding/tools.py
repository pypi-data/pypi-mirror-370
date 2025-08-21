import difflib
import json
import logging
import os
import re
import shutil
import subprocess
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from cli.coding.base import CodeMieTool
from cli.coding.models import (
    CommandLineInput,
    CreateDirectoryInput,
    EditFileInput,
    EditOperation,
    FilesystemToolConfig,
    ListDirectoryInput,
    MoveFileInput,
    ProjectTreeInput,
    ReadFileInput,
    ReadMultipleFilesInput,
    SearchFilesInput,
    WriteFileInput,
)
from cli.coding.path_utils import (
    DEFAULT_IGNORE_PATTERNS,
    collect_all_files,
    list_directory_entries,
    validate_path_against_ignore_patterns,
)
from cli.coding.tools_vars import (
    COMMAND_LINE_TOOL,
    CREATE_DIRECTORY_TOOL,
    EDIT_FILE_TOOL,
    LIST_ALLOWED_DIRECTORIES_TOOL,
    LIST_DIRECTORY_TOOL,
    MOVE_FILE_TOOL,
    PROJECT_TREE_TOOL,
    READ_FILE_TOOL,
    READ_MULTIPLE_FILES_TOOL,
    SEARCH_FILES_TOOL,
    WRITE_FILE_TOOL,
)

logger = logging.getLogger(__name__)

class BaseFilesystemTool(CodeMieTool):
    """Base class for all filesystem tools with security validation."""

    filesystem_config: Optional[FilesystemToolConfig] = Field(exclude=True, default=None)

    def normalize_path(self, path: str) -> str:
        """Normalize path consistently."""
        return os.path.normpath(path)

    def expand_home(self, filepath: str) -> str:
        """Expand '~' to the user's home directory."""
        if filepath.startswith('~/') or filepath == '~':
            return os.path.join(os.path.expanduser('~'), filepath[1:] if len(filepath) > 1 else '')
        return filepath

    def _ensure_filesystem_config(self):
        """Ensure filesystem_config is properly initialized."""
        if not self.filesystem_config:
            self.filesystem_config = FilesystemToolConfig(allowed_directories=[os.getcwd()])
        elif not self.filesystem_config.allowed_directories:
            self.filesystem_config.allowed_directories = [os.getcwd()]

    def _is_path_in_allowed_dirs(self, path: str) -> bool:
        """Check if a path is within allowed directories."""
        return any(
            path.startswith(self.normalize_path(dir))
            for dir in self.filesystem_config.allowed_directories
        )

    def _validate_real_path(self, absolute_path: str) -> str:
        """Validate the real path (resolving symlinks)."""
        real_path = os.path.realpath(absolute_path)
        normalized_real = self.normalize_path(real_path)
        
        if not self._is_path_in_allowed_dirs(normalized_real):
            raise ValueError("Access denied - symlink target outside allowed directories")
            
        return real_path

    def _validate_parent_dir(self, absolute_path: str) -> str:
        """Validate the parent directory when the path itself doesn't exist."""
        parent_dir = os.path.dirname(absolute_path)
        try:
            real_parent_path = os.path.realpath(parent_dir)
            normalized_parent = self.normalize_path(real_parent_path)
            
            if not self._is_path_in_allowed_dirs(normalized_parent):
                raise ValueError("Access denied - parent directory outside allowed directories")
                
            return absolute_path
        except FileNotFoundError:
            raise ValueError(f"Parent directory does not exist: {parent_dir}")

    def validate_path(self, requested_path: str) -> str:
        """Validate that a path is within allowed directories."""
        self._ensure_filesystem_config()

        expanded_path = self.expand_home(requested_path)
        absolute = os.path.abspath(expanded_path)
        normalized_requested = self.normalize_path(absolute)

        if not self._is_path_in_allowed_dirs(normalized_requested):
            allowed_dirs = ', '.join(self.filesystem_config.allowed_directories)
            raise ValueError(f"Access denied - path outside allowed directories: {absolute} not in {allowed_dirs}")

        try:
            return self._validate_real_path(absolute)
        except FileNotFoundError:
            return self._validate_parent_dir(absolute)

    def integration_healthcheck(self) -> Tuple[bool, str]:
        if not self.filesystem_config:
            self.filesystem_config = FilesystemToolConfig(allowed_directories=[os.getcwd()])
        elif not self.filesystem_config.allowed_directories:
            self.filesystem_config.allowed_directories = [os.getcwd()]

        for dir_path in self.filesystem_config.allowed_directories:
            try:
                expanded_path = self.expand_home(dir_path)
                if not os.path.isdir(expanded_path):
                    return False, f"Path is not a directory: {dir_path}"
                if not os.access(expanded_path, os.R_OK):
                    return False, f"Directory is not accessible: {dir_path}"
            except Exception as e:
                return False, f"Error checking directory {dir_path}: {str(e)}"

        return True, ""


class ReadFileTool(BaseFilesystemTool):
    name: str = READ_FILE_TOOL.name
    args_schema: type[BaseModel] = ReadFileInput
    description: str = READ_FILE_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            with open(validated_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"


class ReadMultipleFilesTool(BaseFilesystemTool):
    name: str = READ_MULTIPLE_FILES_TOOL.name
    tokens_size_limit: int = 30000
    args_schema: type[BaseModel] = ReadMultipleFilesInput
    description: str = READ_MULTIPLE_FILES_TOOL.description

    def execute(self, paths: List[str]) -> str:
        results = []

        for file_path in paths:
            try:
                validated_path = self.validate_path(file_path)
                with open(validated_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                results.append(f"{file_path}:\n{content}\n")
            except Exception as e:
                results.append(f"{file_path}: Error - {str(e)}")

        return "\n---\n".join(results)


class WriteFileTool(BaseFilesystemTool):
    name: str = WRITE_FILE_TOOL.name
    args_schema: type[BaseModel] = WriteFileInput
    description: str = WRITE_FILE_TOOL.description

    def execute(self, path: str, content: str) -> str:
        validated_path = self.validate_path(path)
        try:
            os.makedirs(os.path.dirname(validated_path), exist_ok=True)

            with open(validated_path, 'w', encoding='utf-8') as file:
                file.write(content)

            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file {path}: {str(e)}"


class EditFileTool(BaseFilesystemTool):
    name: str = EDIT_FILE_TOOL.name
    args_schema: type[BaseModel] = EditFileInput
    description: str = EDIT_FILE_TOOL.description

    def normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to LF."""
        return text.replace('\r\n', '\n')

    def create_unified_diff(self, original_content: str, new_content: str, filepath: str = 'file') -> str:
        """Create a unified diff between original and new content."""
        normalized_original = self.normalize_line_endings(original_content)
        normalized_new = self.normalize_line_endings(new_content)

        diff_lines = list(difflib.unified_diff(
            normalized_original.splitlines(keepends=True),
            normalized_new.splitlines(keepends=True),
            fromfile=filepath,
            tofile=filepath,
            fromfiledate='original',
            tofiledate='modified'
        ))

        return ''.join(diff_lines)

    def _find_exact_match(self, old_lines: List[str], content_lines: List[str]) -> Optional[int]:
        """Find the exact match position for a set of lines in the content."""
        for i in range(len(content_lines) - len(old_lines) + 1):
            potential_match = content_lines[i:i + len(old_lines)]
            
            is_match = all(
                old_line.strip() == content_line.strip()
                for old_line, content_line in zip(old_lines, potential_match)
            )
            
            if is_match:
                return i
        return None
    
    def _get_indent(self, line: str) -> str:
        """Extract the indentation from a line."""
        indent_match = re.match(r'^\s*', line)
        return indent_match.group(0) if indent_match else ''
    
    def _format_new_line(self, line: str, j: int, original_indent: str, old_lines: List[str], new_lines_split: List[str]) -> str:
        """Format a new line with proper indentation."""
        if j == 0:
            return original_indent + line.lstrip()
        
        old_indent = self._get_indent(old_lines[j] if j < len(old_lines) else '')
        new_indent = self._get_indent(line)
        
        if old_indent and new_indent:
            relative_indent = max(0, len(new_indent) - len(old_indent))
            return original_indent + ' ' * relative_indent + line.lstrip()
        else:
            return line
    
    def _replace_lines_with_indentation(self, content_lines: List[str], match_index: int, old_lines: List[str], normalized_new: str) -> List[str]:
        """Replace lines while preserving indentation."""
        original_indent = self._get_indent(content_lines[match_index])
        new_lines = []
        
        for j, line in enumerate(normalized_new.split('\n')):
            new_lines.append(self._format_new_line(line, j, original_indent, old_lines, normalized_new.split('\n')))
        
        result = content_lines.copy()
        result[match_index:match_index + len(old_lines)] = new_lines
        return result
    
    def _format_diff_output(self, diff: str) -> str:
        """Format the diff output with appropriate backticks."""
        num_backticks = 3
        while '`' * num_backticks in diff:
            num_backticks += 1
        
        return f"{'`' * num_backticks}diff\n{diff}{'`' * num_backticks}\n\n"

    def apply_file_edits(
            self,
            file_path: str,
            edits: List[EditOperation],
            dry_run: bool = False
    ) -> str:
        """Apply edits to a file and return a diff."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = self.normalize_line_endings(file.read())

        modified_content = content
        for edit in edits:
            normalized_old = self.normalize_line_endings(edit.old_text)
            normalized_new = self.normalize_line_endings(edit.new_text)

            # Simple case: direct string replacement
            if normalized_old in modified_content:
                modified_content = modified_content.replace(normalized_old, normalized_new)
                continue

            # More complex case: line-by-line matching with indentation preservation
            old_lines = normalized_old.split('\n')
            content_lines = modified_content.split('\n')
            
            match_index = self._find_exact_match(old_lines, content_lines)
            if match_index is not None:
                content_lines = self._replace_lines_with_indentation(
                    content_lines, match_index, old_lines, normalized_new
                )
                modified_content = '\n'.join(content_lines)
            else:
                raise ValueError(f"Could not find exact match for edit:\n{edit.old_text}")

        # Create and format the diff
        diff = self.create_unified_diff(content, modified_content, file_path)
        formatted_diff = self._format_diff_output(diff)

        # Write changes if not a dry run
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

        return formatted_diff

    def execute(self, path: str, edits: List[EditOperation], dry_run: Optional[bool] = False) -> str:
        validated_path = self.validate_path(path)
        try:
            edit_operations = []
            for edit in edits:
                old_text = edit.old_text
                new_text = edit.new_text
                edit_operations.append(EditOperation(old_text=old_text, new_text=new_text))

            result = self.apply_file_edits(validated_path, edit_operations, dry_run)
            return result
        except Exception as e:
            return f"Error editing file {path}: {str(e)}"


class CreateDirectoryTool(BaseFilesystemTool):
    name: str = CREATE_DIRECTORY_TOOL.name
    args_schema: type[BaseModel] = CreateDirectoryInput
    description: str = CREATE_DIRECTORY_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            os.makedirs(validated_path, exist_ok=True)
            return f"Successfully created directory {path}"
        except Exception as e:
            return f"Error creating directory {path}: {str(e)}"


class ListDirectoryTool(BaseFilesystemTool):
    name: str = LIST_DIRECTORY_TOOL.name
    args_schema: type[BaseModel] = ListDirectoryInput
    description: str = LIST_DIRECTORY_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            # Get directory entries using the common utility
            dir_entries = list_directory_entries(validated_path)
            
            # Format the entries for display
            entries = []
            for name, is_dir in dir_entries:
                prefix = "[DIR]" if is_dir else "[FILE]"
                entries.append(f"{prefix}{name}")

            return "\n".join(entries) if entries else "Empty directory"
        except Exception as e:
            return f"Error listing directory {path}: {str(e)}"


class ProjectTreeTool(BaseFilesystemTool):
    name: str = PROJECT_TREE_TOOL.name
    args_schema: type[BaseModel] = ProjectTreeInput
    description: str = PROJECT_TREE_TOOL.description

    def execute(self, directory: Optional[str]) -> str:
        try:
            path = directory if directory else self.filesystem_config.allowed_directories[0]
            
            # First validate if the path contains ignored patterns
            allowed_dirs = self.filesystem_config.allowed_directories if self.filesystem_config else [os.getcwd()]
            error_message = validate_path_against_ignore_patterns(path, allowed_dirs)
            if error_message:
                return error_message
                
            # Validate path is within allowed directories
            validated_path = self.validate_path(path)
            
            # Use the implementation that collects all files excluding those that match ignore patterns
            all_files = collect_all_files(validated_path, include_ignored=False)

            # Return as a simple JSON array of file paths
            return json.dumps(all_files, indent=2)
        except Exception as e:
            return f"Error generating project tree for {directory}: {str(e)}"


class MoveFileTool(BaseFilesystemTool):
    name: str = MOVE_FILE_TOOL.name
    args_schema: type[BaseModel] = MoveFileInput
    description: str = MOVE_FILE_TOOL.description

    def execute(self, source: str, destination: str) -> str:
        valid_source_path = self.validate_path(source)
        valid_dest_path = self.validate_path(destination)

        try:
            dest_dir = os.path.dirname(valid_dest_path)
            os.makedirs(dest_dir, exist_ok=True)

            shutil.move(valid_source_path, valid_dest_path)
            return f"Successfully moved {source} to {destination}"
        except Exception as e:
            return f"Error moving {source} to {destination}: {str(e)}"


class SearchFilesTool(BaseFilesystemTool):
    name: str = SEARCH_FILES_TOOL.name
    args_schema: type[BaseModel] = SearchFilesInput
    description: str = SEARCH_FILES_TOOL.description

    def _matches_filename_pattern(self, file_path: str, pattern_lower: str) -> bool:
        """Check if the file name matches the pattern.
        
        Args:
            file_path: The path to the file
            pattern_lower: The lowercase pattern to match against
            
        Returns:
            True if the file name contains the pattern, False otherwise
        """
        return pattern_lower in os.path.basename(file_path).lower()
    
    def _matches_content_pattern(self, abs_path: str, pattern_lower: str) -> bool:
        """Check if the file content matches the pattern.
        
        Args:
            abs_path: The absolute path to the file
            pattern_lower: The lowercase pattern to match against
            
        Returns:
            True if the file content contains the pattern, False otherwise
        """
        if not self._is_text_file(abs_path):
            return False
            
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return pattern_lower in content.lower()
        except Exception:
            # Skip files that can't be read
            return False

    def search_files(
            self,
            root_path: str,
            pattern: str,
            exclude_patterns: Optional[List[str]] = None,
            full_search: bool = False
    ) -> List[str]:
        """Search for files matching a pattern.
        
        Args:
            root_path: The root path to search in
            pattern: The pattern to search for
            exclude_patterns: Patterns to exclude from the search
            full_search: Whether to perform full text search within file contents
            
        Returns:
            List of file paths that match the pattern
        """
        if exclude_patterns is None:
            exclude_patterns = []
            
        # First collect all files that don't match exclude patterns
        all_files = collect_all_files(root_path, root_path, exclude_patterns, include_ignored=False)
        
        # Convert pattern to lowercase for case-insensitive search
        pattern_lower = pattern.lower()
        
        # Filter files that match the search pattern
        results = []
        for file_path in all_files:
            # Convert relative path to absolute path for display
            abs_path = os.path.join(root_path, file_path)
            
            # Check if the file name matches the pattern
            if self._matches_filename_pattern(file_path, pattern_lower):
                results.append(abs_path)
                continue
                
            # If full_search is enabled, check file contents
            if full_search and self._matches_content_pattern(abs_path, pattern_lower):
                results.append(abs_path)
                
        return results
    
    # Define common text file extensions as a class variable
    _TEXT_EXTENSIONS = [
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
        '.yaml', '.yml', '.ini', '.cfg', '.conf', '.sh', '.bash', '.bat',
        '.ps1', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs',
        '.rb', '.php', '.pl', '.pm', '.swift', '.kt', '.kts', '.dart',
        '.lua', '.r', '.scala', '.sql', '.proto', '.jsx', '.tsx', '.vue',
        '.gradle', '.properties', '.toml', '.csv', '.log'
    ]
    
    def _has_text_extension(self, file_path: str) -> bool:
        """Check if a file has a known text file extension.
        
        Args:
            file_path: The path to the file
            
        Returns:
            True if the file has a text extension, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self._TEXT_EXTENSIONS
    
    def _has_text_content(self, file_path: str) -> bool:
        """Check if a file has text content by examining its bytes.
        
        Args:
            file_path: The path to the file
            
        Returns:
            True if the file appears to contain text, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                # Read first 1024 bytes
                sample = f.read(1024)
                # Check for null bytes which indicate binary file
                if b'\x00' in sample:
                    return False
                # Try to decode as UTF-8
                sample.decode('utf-8')
                return True
        except Exception:
            return False
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if a file is a text file based on its extension and content.
        
        Args:
            file_path: The path to the file
            
        Returns:
            True if the file is likely a text file, False otherwise
        """
        # First check by extension (faster)
        if self._has_text_extension(file_path):
            return True
            
        # If extension check fails, examine content
        return self._has_text_content(file_path)

    def _prepare_exclude_patterns(self, exclude_patterns: Optional[List[str]]) -> List[str]:
        """Prepare the exclude patterns list by combining with default patterns.
        
        Args:
            exclude_patterns: User-provided patterns to exclude
            
        Returns:
            Combined list of exclude patterns
        """
        if exclude_patterns is None:
            exclude_patterns = []
        
        # Combine with default patterns and remove duplicates
        return list(set(exclude_patterns + DEFAULT_IGNORE_PATTERNS))
    
    def _format_search_results(self, results: List[str]) -> str:
        """Format the search results for display.
        
        Args:
            results: List of file paths that match the search
            
        Returns:
            Formatted string of results
        """
        return "\n".join(results) if results else "No matches found"
    
    def execute(self, path: str, pattern: str, exclude_patterns: Optional[List[str]] = None, full_search: bool = False) -> str:
        # Prepare exclude patterns
        combined_patterns = self._prepare_exclude_patterns(exclude_patterns)
        
        try:
            # Validate path
            validated_path = self.validate_path(path)
            
            # Perform search
            results = self.search_files(validated_path, pattern, combined_patterns, full_search)
            
            # Format and return results
            return self._format_search_results(results)
        except Exception as e:
            return f"Error searching in {path}: {str(e)}"


class ListAllowedDirectoriesTool(BaseFilesystemTool):
    name: str = LIST_ALLOWED_DIRECTORIES_TOOL.name
    args_schema: Optional[type[BaseModel]] = None
    description: str = LIST_ALLOWED_DIRECTORIES_TOOL.description

    def execute(self) -> str:
        if not self.filesystem_config or not self.filesystem_config.allowed_directories:
            return "No allowed directories configured"

        return f"Allowed directories:\n{os.linesep.join(self.filesystem_config.allowed_directories)}"


class CommandLineTool(BaseFilesystemTool):
    name: str = COMMAND_LINE_TOOL.name
    args_schema: type[BaseModel] = CommandLineInput
    description: str = COMMAND_LINE_TOOL.description
    timeout: int = 120  # Default timeout in seconds

    # Define dangerous patterns as a class variable to avoid recreating it each time
    _DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",  # Prevent removing root directory
        r"mkfs",  # Prevent formatting drives
        r"dd\s+if=",  # Prevent disk operations
        r"wget\s+.+\s+\|\.+sh",  # Prevent downloading and piping to shell
        r"curl\s+.+\s+\|\.+sh",  # Prevent downloading and piping to shell
        r"sudo",  # Prevent privilege escalation
        r"chmod\s+777",  # Prevent setting unsafe permissions
        r"chmod\s+\+x",  # Prevent making files executable
        r">\s*/etc/",  # Prevent writing to system config
        r">\s*/dev/",  # Prevent writing to devices
    ]
    
    def _contains_dangerous_pattern(self, command: str, pattern: str) -> bool:
        """Check if a command contains a specific dangerous pattern."""
        return bool(re.search(pattern, command, re.IGNORECASE))
    
    def _sanitize_command(self, command: str) -> Optional[str]:
        """Sanitize the command for security purposes.
        
        Returns an error message if the command is not allowed, None if it's safe.
        """
        for pattern in self._DANGEROUS_PATTERNS:
            if self._contains_dangerous_pattern(command, pattern):
                return f"Command contains potentially dangerous pattern: {pattern}"
        
        return None

    def execute(self, command: str, working_directory: Optional[str] = None) -> str:
        # Sanitize the command
        error = self._sanitize_command(command)
        if error:
            return f"Error: {error}"
        
        # Set working directory
        if working_directory:
            work_dir = self.validate_path(working_directory)
            if not os.path.isdir(work_dir):
                return f"Error: Working directory does not exist: {working_directory}"
        else:
            # Use the first allowed directory as default
            if self.filesystem_config and self.filesystem_config.allowed_directories:
                work_dir = self.validate_path(self.filesystem_config.allowed_directories[0])
            else:
                work_dir = os.getcwd()
        
        try:
            # Execute the command with timeout
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Prepare the output
            output = [f"Working directory: {work_dir}"]
            output.append(f"Command: {command}")
            output.append(f"Exit code: {result.returncode}")
            
            if result.stdout:
                output.append("\nStandard output:")
                output.append(result.stdout)
            
            if result.returncode != 0 and result.stderr:
                output.append("\nStandard error:")
                output.append(result.stderr)
            
            return "\n".join(output)
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
