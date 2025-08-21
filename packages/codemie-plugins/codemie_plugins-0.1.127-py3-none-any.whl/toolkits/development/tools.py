from typing import Type, Optional

from pydantic import Field

from codemie.toolkit import RemoteInput, RemoteTool
from toolkits.development.service.diff_update_coder import get_edits, apply_edits
from toolkits.development.service.git_service import GitCommandService
from toolkits.core.utils import get_relative_path, create_folders
from toolkits.development.tools_vars import DIFF_UPDATE_FILE_TOOL, GENERIC_GIT_TOOL


class DiffUpdateFileInput(RemoteInput):
    file_path: str = Field(None, description="File path of the file that should be updated with provided changes")
    changes: str = Field(None, description="""
List of *SEARCH/REPLACE* blocks in the following format:

!!!python
<<<<<<< SEARCH
from flask import Flask
=======
import math
from flask import Flask
>>>>>>> REPLACE
!!!  
    """)
    should_create: Optional[bool] = Field(default=False, description="Whether the file should be created if it does not exist.")


class DiffUpdateFileTool(RemoteTool):
    name: str = DIFF_UPDATE_FILE_TOOL.name
    args_schema: Type[RemoteInput] = DiffUpdateFileInput
    description: str = DIFF_UPDATE_FILE_TOOL.description
    root_dir: Optional[str] = "."

    def _run(self, file_path: str, changes: str, should_create: Optional[bool] = False) -> str:
        try:
            return self._try_execute(file_path, changes, should_create)
        except Exception as e:
            return f"Error: {str(e)}"

    def _try_execute(self, file_path: str, changes: str, should_create: bool) -> str:
        read_path = get_relative_path(self.root_dir, file_path)

        if should_create and not read_path.exists():
            create_folders(read_path)
            read_path.touch()
        elif should_create and read_path.exists():
            return f"Error: File {read_path} already exists"
        elif not read_path.exists():
            return f"Error: no such file or directory: {file_path}"

        with read_path.open("r", encoding="utf-8") as f:
            content = f.read()

        edits = get_edits(changes)

        if not edits:
            raise ValueError("List of edits are empty")

        new_content = apply_edits(edits, content)

        with read_path.open("w", encoding="utf-8") as f:
            f.write(new_content)

        return f"File written successfully to {file_path}"


class GenericGitInput(RemoteInput):
    """Schema for operations that require a git command as input."""
    git_command: str = Field(default=None, description="Git command to execute.")

class GenericGitTool(RemoteTool):
    name: str = GENERIC_GIT_TOOL.name
    args_schema: Type[RemoteInput] = GenericGitInput
    description: str = GENERIC_GIT_TOOL.description
    root_dir: Optional[str] = "."

    def _run(self, git_command: str, *args, **kwargs) -> str:
        return GitCommandService.call_git_command(self.root_dir, git_command)
