from typing import List, Optional

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    name: str
    label: str = ''
    description: str = ''

class FilesystemToolConfig(BaseModel):
    """Configuration for filesystem tools with allowed directories."""
    allowed_directories: List[str] = Field(
        default_factory=list,
        description="List of directories that the filesystem tools are allowed to access"
    )


class ReadFileInput(BaseModel):
    path: str = Field(..., description="Path to the file to read")


class ReadMultipleFilesInput(BaseModel):
    paths: List[str] = Field(..., description="List of file paths to read")


class WriteFileInput(BaseModel):
    path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")


class EditOperation(BaseModel):
    old_text: str = Field(..., description="Text to search for - must match exactly")
    new_text: str = Field(..., description="Text to replace with")


class EditFileInput(BaseModel):
    path: str = Field(..., description="Path to the file to edit")
    edits: List[EditOperation] = Field(..., description="List of edit operations to apply")
    dry_run: bool = Field(False, description="Preview changes using git-style diff format")


class CreateDirectoryInput(BaseModel):
    path: str = Field(..., description="Path to the directory to create")


class ListDirectoryInput(BaseModel):
    path: str = Field(..., description="Path to the directory to list")


class ProjectTreeInput(BaseModel):
    directory: Optional[str] = Field(..., description="""
    Allowed directory path which might be relevant to user input and used by additional filtration.
    First, need to get allowed directories first and provide particular if there are several available.
    Otherwise, do not put anything.
    """)


class MoveFileInput(BaseModel):
    source: str = Field(..., description="Source path")
    destination: str = Field(..., description="Destination path")


class SearchFilesInput(BaseModel):
    path: str = Field(..., description="Path to search in")
    pattern: str = Field(..., description="Pattern to search for")
    exclude_patterns: Optional[List[str]] = Field(
        default=[],
        description="Additional patterns to exclude from the search (default patterns are already excluded: node_modules, dist, build, .git, etc.)"
    )
    full_search: bool = Field(
        default=False,
        description="Enable full text search within file contents instead of just file names"
    )

class CommandLineInput(BaseModel):
    command: str = Field(..., description="Command to execute in the shell")
    working_directory: Optional[str] = Field(None, description="Working directory for command execution")


class FileInfo(BaseModel):
    size: int
    created: str
    modified: str
    accessed: str
    isDirectory: bool
    isFile: bool
    permissions: str


class TreeEntry(BaseModel):
    name: str
    type: str  # "file" or "directory"
    children: Optional[List["TreeEntry"]] = None
