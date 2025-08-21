from codemie.toolkit import RemoteToolMetadata

READ_FILE_TOOL = RemoteToolMetadata(
    name="_read_file_from_file_system",
    description="""
    Use this tool to read file from file system or disk.
    Might be useful when it is necessary to get context first and then use it.
    """.strip(),
    label="Read file",
)

LIST_DIRECTORY_TOOL = RemoteToolMetadata(
    name="_list_files_in_directory",
    description="""
    Use this tool to list files and directories in a specified folder from file system or disk
    """.strip(),
    label="List directory",
)

WRITE_FILE_TOOL = RemoteToolMetadata(
    name="_write_file_to_file_system",
    description="""
    Use this tool to write file to file system or disk.
    Useful when you need to implement changes, create or update file, code, etc.
    Required arguments:
    - file_path: Path to the file to write to
    - text: Content to write to the file
    """.strip(),
    label="Write file",
)

COMMAND_LINE_TOOL_ALLOWED_PATTERNS = [(r".*", "All commands are allowed, EXCEPT the denied ones!")]

COMMAND_LINE_TOOL_DENIED_PATTERNS = [
            (r"\brm\s+-rf\b", "Use of 'rm -rf' command is not allowed."),
            (r"\bmv\b.*?\s+/dev/null", "Moving files to /dev/null is not allowed."),
            (r"\bdd\b", "Use of 'dd' command is not allowed."),
            (r">\s*/dev/sd[a-z][1-9]?", "Overwriting disk blocks directly is not allowed."),
            (r":\(\)\{\s*:\|\:&\s*\};:", "Fork bombs are not allowed."),
        ]

COMMAND_LINE_TOOL = RemoteToolMetadata(
    name="_run_command_line_tool",
    description=f"""
    Command line tool to execute linux/osx shell commands which are not denied and allowed(see descriptions below).
    NEVER execute denied commands, they can be harmful to the system.
    Allowed commands description: {COMMAND_LINE_TOOL_ALLOWED_PATTERNS}
    DENIED commands description: {COMMAND_LINE_TOOL_DENIED_PATTERNS}
    """.strip(),
    label="Run command line",
    allowed_patterns=COMMAND_LINE_TOOL_ALLOWED_PATTERNS,
    denied_patterns=COMMAND_LINE_TOOL_DENIED_PATTERNS,
)
