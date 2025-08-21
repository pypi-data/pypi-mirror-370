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

DIFF_UPDATE_FILE_TOOL = RemoteToolMetadata(
    name="_diff_update_file_tool",
    description="""
    Use this tool when you need to update file by the provided list of changes
        
    You MUST describe each change with a *SEARCH/REPLACE block* per the examples below. All changes must use this *SEARCH/REPLACE block* format. ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
    Required arguments:
    - file_path: Path to the file to write to
    - changes: List of changes to apply to the file
    - should_create: (Optional) Whether the file should be created if it does not exist.
    
    Every *SEARCH/REPLACE block* must use this format:
    1. The opening fence and code language, eg: !!!python
    2. The start of search block: <<<<<<< SEARCH
    3. A contiguous chunk of lines to search for in the existing source code
    4. The dividing line: =======
    5. The lines to replace into the source code
    6. The end of the replace block: >>>>>>> REPLACE
    7. The closing fence: !!!

        """.strip(),
    label="Update File (diff)"
)

GENERIC_GIT_TOOL = RemoteToolMetadata(
    name="_generic_git_tool",
    description="""
        Use this tool to perform any git commands on file system.
        
        Examples of usage:
        Create and checkout new branch - `checkout -b {new_branch_name}`
        Add file contents to the index - `add {file_path}`
        Remove files from the working tree and from the index - `rm {file_path}`
        Commit changes in index (changes must be added by `add` or `rm` commands) - `commit -m {commit_message}`
        Push commited changes to branch - `push [--set-upstream origin {branch_name}]`
        
        For getting whole git contract you can use git tool help - `help`
        """,
    label="Generic Git Tool"
)