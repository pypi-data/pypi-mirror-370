import os
import subprocess
from pathlib import Path
from typing import Type, Optional, Any, List, Tuple

from pydantic import Field
from langchain_community.tools.file_management.utils import FileValidationError, \
    INVALID_PATH_TEMPLATE

from codemie.toolkit import RemoteInput, RemoteTool, logger
from codemie.langchain.services import format_tool_message, format_tool_content
from toolkits.core.tools_vars import READ_FILE_TOOL, LIST_DIRECTORY_TOOL, WRITE_FILE_TOOL, \
    COMMAND_LINE_TOOL
from toolkits.core.utils import get_relative_path, create_folders


class ReadFileInput(RemoteInput):
    file_path: str = Field(None, description="File path to read from file system")


class ReadFileTool(RemoteTool):
    name: str = READ_FILE_TOOL.name
    args_schema: Type[RemoteInput] = ReadFileInput
    description: str = READ_FILE_TOOL.description
    root_dir: Optional[str] = "."

    def _run(self, file_path: str, *args, **kwargs) -> str:
        try:
            read_path = get_relative_path(self.root_dir, file_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)
        if not read_path.exists():
            return f"Error: no such file or directory: {file_path}"
        try:
            with read_path.open("r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error: {str(e)}"


class DirectoryListingInput(RemoteInput):
    dir_path: str = Field(None, description="Subdirectory to list.")


class ListDirectoryTool(RemoteTool):

    name: str = LIST_DIRECTORY_TOOL.name
    args_schema: Type[RemoteInput] = DirectoryListingInput
    description: str = LIST_DIRECTORY_TOOL.description
    root_dir: Optional[str] = "."

    def _run(self, dir_path: str = ".", *args, **kwargs) -> str:
        try:
            dir_path_ = get_relative_path(self.root_dir, dir_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="dir_path", value=dir_path)
        try:
            entries = os.listdir(dir_path_)
            logger.info(f"Files in directory {dir_path}: {entries}")
            if entries:
                return "\n".join(entries)
            else:
                return f"No files found in directory {dir_path}"
        except Exception as e:
            return "Error: " + str(e)


class WriteFileInput(RemoteInput):
    file_path: str = Field(None, description="File path to write to file system")
    text: str = Field(None, description="Content or text to write to file.")


class WriteFileTool(RemoteTool):
    name: str = WRITE_FILE_TOOL.name
    args_schema: Type[RemoteInput] = WriteFileInput
    description: str = WRITE_FILE_TOOL.description
    root_dir: Optional[str] = "."

    def _run(self, file_path: str, text: str) -> str:
        try:
            write_path = get_relative_path(self.root_dir, file_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)
        try:
            create_folders(write_path)
            write_path.parent.mkdir(exist_ok=True, parents=False)
            mode = "w"
            with write_path.open(mode, encoding="utf-8") as f:
                f.write(text)

            return f"File written successfully to {file_path}"
        except Exception as e:
            return "Error: " + str(e)


class CommandLineInput(RemoteInput):
    command: str = Field(
        None,
        description="Command to execute in the CLI."
    )


class CommandLineTool(RemoteTool):
    name: str = COMMAND_LINE_TOOL.name
    description: str = COMMAND_LINE_TOOL.description
    args_schema: Type[RemoteInput] = CommandLineInput
    timeout: int = int(os.getenv('COMMAND_LINE_TOOL_TIMEOUT', 300))
    root_dir: str = "."
    allowed_patterns: List[Tuple[str, str]] = COMMAND_LINE_TOOL.allowed_patterns
    denied_patterns: List[Tuple[str, str]] = COMMAND_LINE_TOOL.denied_patterns

    def _run(self, command: str, *args, **kwargs) -> Any:
        error = self.sanitize_input(command)
        if error:
            return str(error)
        else:
            work_dir = Path(self.root_dir)
            work_dir.mkdir(exist_ok=True)

            result = subprocess.run(
                command, cwd=work_dir, shell=True, text=True, capture_output=True, timeout=float(self.timeout)
            )

            if result.returncode != 0:
                output = str(result.stderr) if result.stderr else str(result.stdout)
                formatted_error = format_tool_content(output, max_length=500)
                separator = "-" * 40
                logger.error(f"\n{separator}\nError during tool '{self.name}' invocation:\n{formatted_error}\n{separator}")
                return output
            else:
                logger.info(format_tool_message(self.name, {"command": command}, result.stdout))
                return str(result.stdout)

