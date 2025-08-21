from codemie.toolkit import RemoteToolMetadata

PARSE_LOG_FILE_TOOL = RemoteToolMetadata(
    name="_parse_log_file",
    description="""
    Use this tool to parse log files and finding issues from them by any patterns or strings.
    This tool process large log files and split findings into chunks and save to file system for further processing.
    There are required arguments:
    - file_paths: List of paths to log files to read from file system;
    - patterns: List of patterns to search for. Patterns can be regex or string, e.g. 'Traceback', 'error', r'exception', etc. 
    You must generate possible regex and strings based on programming language;
    """.strip(),
    label="Parse log files",
)
