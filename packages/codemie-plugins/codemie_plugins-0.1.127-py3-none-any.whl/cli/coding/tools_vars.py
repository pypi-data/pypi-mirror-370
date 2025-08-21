from cli.coding.models import ToolMetadata

READ_FILE_TOOL = ToolMetadata(
    name="read_file",
    description="""
    Read the complete contents of a file from the file system.
    Use this tool when you need to examine the contents of a single file.
    """,
    label="Read File",
)

READ_MULTIPLE_FILES_TOOL = ToolMetadata(
    name="read_multiple_files",
    description="""
    Read the contents of multiple files simultaneously.
    You must use this tool when you need to read multiple files at once.
    This is more efficient than reading files one by one when you need to analyze or compare multiple files. 
    Each file's content is returned with its path as a reference.
    """,
    label="Read Multiple Files",
)

WRITE_FILE_TOOL = ToolMetadata(
    name="write_file",
    description="""
    Create a new file or completely overwrite an existing file with new content.
    Use with caution as it will overwrite existing files without warning.
    Handles text content with proper encoding.
    """,
    label="Write File",
)

EDIT_FILE_TOOL = ToolMetadata(
    name="edit_file",
    description="""
    Make line-based edits to a text file. 
    Each edit replaces exact line sequences with new content. Returns a git-style diff showing the changes made.
    Input parameters:
        - path: The path to the file to edit.
        - edits: A list of dictionaries where each dictionary represents an edit. Each dictionary should have two keys:
            * old_text: Text to search for - must match exactly.
            * end_line: Text to replace with.
        - dry_run (Optional): Preview changes using git-style diff format
    """,
    label="Edit File",
)

CREATE_DIRECTORY_TOOL = ToolMetadata(
    name="create_directory",
    description="""
    Create a new directory or ensure a directory exists. Can create multiple
    nested directories in one operation. If the directory already exists,
    this operation will succeed silently. Perfect for setting up directory
    structures for projects or ensuring required paths exist. 
    """,
    label="Create Directory",
)

LIST_DIRECTORY_TOOL = ToolMetadata(
    name="list_directory",
    description="""
    Get a detailed listing of all files and directories in a specified path. 
    Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. 
    Common directories and files like node_modules, .git, etc. are automatically
    excluded from results. This tool is essential for understanding directory structure and
    finding specific files within a directory.
    """,
    label="List Directory",
)

PROJECT_TREE_TOOL = ToolMetadata(
    name="get_project_tree",
    description="""
    Useful when you want to get code repository file tree for repository or analyze folders structure.
    It must be the first tool to use to get project context.
    Returns list of 'paths' in the project/all folders/repository.
    You do not need to pass arguments, it will return file tree of current selected repository.
    Parameters:
        - directory (optional): Allowed directory path which might be relevant to user input and used by additional filtration.
    First, need to get allowed directories first and provide particular if there are several available.
    Otherwise, do not put anything.
    """,
    label="Directory Tree",
)

MOVE_FILE_TOOL = ToolMetadata(
    name="move_file",
    description="""
    Move or rename files and directories. Can move files between directories
    and rename them in a single operation. If the destination exists, the
    operation will fail. Works across different directories and can be used
    for simple renaming within the same directory. Both source and destination must be within allowed directories.
    """,
    label="Move File",
)

SEARCH_FILES_TOOL = ToolMetadata(
    name="search_files",
    description="""
    Recursively search for files and directories matching a pattern.
    IMPORTANT: Before making search, better to get project tree using 'project_tree' tool.
    Searches through all subdirectories from the starting path.
    The search is case-insensitive and matches partial names. Returns full paths to all
    matching items. Common directories and files like node_modules, .git, etc. are automatically
    excluded from results. Great for finding files when you don't know their exact location.
    Only searches within allowed directories.
    Parameters:
        - full_search (optional): Enable full text search within file contents instead of just file names.
          Default is False (only search in file names).
    """,
    label="Search Files",
)

LIST_ALLOWED_DIRECTORIES_TOOL = ToolMetadata(
    name="list_allowed_directories",
    description="""
    Returns the list of directories that this server is allowed to access.
    Use this to understand which directories are available before trying to access files.
    Might be first tool to invoke to see what directories are accessible.
    """,
    label="List Allowed Directories",
)

COMMAND_LINE_TOOL = ToolMetadata(
    name="command_line",
    description="""
    Execute shell commands in the operating system. This tool allows running
    commands like 'ls', 'grep', or any other available shell command.
    Use with caution as it executes commands with the same permissions as the
    running application.
    Example usages: "git status", "python my_script.py", "npm run test", "docker ps", etc.
    """,
    label="Command Line",
)
