import os

from codemie.toolkit import RemoteToolkit
from toolkits.core.file_system_tools import WriteFileTool, ReadFileTool, ListDirectoryTool, CommandLineTool
from toolkits.development.tools import GenericGitTool, DiffUpdateFileTool


class FileSystemAndCommandToolkit(RemoteToolkit):
    def get_tools(self, root_dir: str = "."):
        if os.getenv("WRITE_FILE_STRATEGY") == "diff":
            write_tool = DiffUpdateFileTool(root_dir=root_dir)
        else:
            write_tool = WriteFileTool(root_dir=root_dir)
        return [
            ReadFileTool(root_dir=root_dir),
            ListDirectoryTool(root_dir=root_dir),
            write_tool,
            CommandLineTool(root_dir=root_dir),
            GenericGitTool(root_dir=root_dir),
        ]
