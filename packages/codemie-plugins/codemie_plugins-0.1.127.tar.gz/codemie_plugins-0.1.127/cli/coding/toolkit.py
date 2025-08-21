import os
from typing import Any, List, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from cli.coding.models import FilesystemToolConfig
from cli.coding.tools import (
    CreateDirectoryTool,
    ProjectTreeTool,
    EditFileTool,
    ListAllowedDirectoriesTool,
    ListDirectoryTool,
    MoveFileTool,
    ReadFileTool,
    ReadMultipleFilesTool,
    SearchFilesTool,
    WriteFileTool,
    CommandLineTool,
)


class FilesystemToolkit(BaseModel):
    """Toolkit for secure filesystem operations."""

    filesystem_config: Optional[FilesystemToolConfig] = None

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        tools = [
            ReadFileTool(filesystem_config=self.filesystem_config),
            ReadMultipleFilesTool(filesystem_config=self.filesystem_config),
            WriteFileTool(filesystem_config=self.filesystem_config),
            EditFileTool(filesystem_config=self.filesystem_config),
            CreateDirectoryTool(filesystem_config=self.filesystem_config),
            ListDirectoryTool(filesystem_config=self.filesystem_config),
            ProjectTreeTool(filesystem_config=self.filesystem_config),
            MoveFileTool(filesystem_config=self.filesystem_config),
            SearchFilesTool(filesystem_config=self.filesystem_config),
            ListAllowedDirectoriesTool(filesystem_config=self.filesystem_config),
            CommandLineTool(filesystem_config=self.filesystem_config),
        ]

        return tools

    @classmethod
    def get_toolkit(cls, configs: dict[str, Any] = None):
        """Create a toolkit instance from config."""
        if configs:
            filesystem_config = FilesystemToolConfig(**configs)
        else:
            # Use current directory as default if no config is provided
            filesystem_config = FilesystemToolConfig(allowed_directories=[os.getcwd()])
        return FilesystemToolkit(filesystem_config=filesystem_config)