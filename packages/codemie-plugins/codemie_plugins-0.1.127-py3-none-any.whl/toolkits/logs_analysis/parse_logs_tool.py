import mmap
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type, Dict, Set, NamedTuple

import pandas as pd
from pydantic import Field

from codemie.logging import logger
from codemie.toolkit import RemoteInput, RemoteTool
from toolkits.logs_analysis.tools_vars import PARSE_LOG_FILE_TOOL

# Global constants
TIMESTAMP_PATTERN = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
DEFAULT_OUTPUT_DIR = "output_logs"
DEFAULT_ROOT_DIR = "."
DATE_FORMAT = "%Y%m%d_%H%M%S"
FILE_ENCODING = "utf-8"
LOG_LEVELS = {"error", "warn", "info", "debug", "trace"}
PATTERN = 'pattern'
FILE_PATH = 'file_path'
TIMESTAMP = 'timestamp'

# File extensions
LOG_EXT = ".log"
CSV_EXT = ".csv"

# Output file prefixes
OCCURRENCE_PREFIX = "occurrence"
STATISTICS_PREFIX = "statistics"


class ParseLogFileInput(RemoteInput):
    file_paths: List[str] = Field(None, description="List of paths to log files to read from file system")
    patterns: List[str] = Field(None, description="List of patterns to search for. Patterns can be regex or "
                                                  "string, e.g. 'Traceback', 'error', r'exception', etc.")
    ignore_patterns: Optional[List[str]] = Field(None,
                                                 description="List of patterns to ignore. Patterns can be regex or "
                                                             "string, e.g. 'OutputError', 'DeprecatedWarning', etc.")
    output_dir: Optional[str] = Field(None, description="Output directory to save the found log files")


@dataclass
class LogEntry:
    """Data class to store log entry information"""
    timestamp: Optional[str]
    pattern: str
    content: str
    file_path: str
    occurrence_id: str


class LogStatistics(NamedTuple):
    """Statistics for log analysis"""
    total_occurrences: int
    unique_files: int
    first_occurrence: str
    last_occurrence: str
    pattern: str
    file_distribution: Dict[str, int]


class LogFileProcessor:
    """Handles the processing of individual log files"""

    def __init__(self, patterns: Dict[str, re.Pattern], ignore_patterns: List[re.Pattern]):
        self.compiled_patterns = patterns
        self.compiled_ignore_patterns = ignore_patterns

    def should_ignore(self, line: str) -> bool:
        """Check if line matches any ignore patterns"""
        return any(regex.search(line) for regex in self.compiled_ignore_patterns)

    def is_new_log_entry(self, line: str) -> bool:
        """Check if line starts a new log entry"""
        return any(level in line.lower() for level in LOG_LEVELS)

    def extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line"""
        timestamp_match = re.search(TIMESTAMP_PATTERN, line)
        return timestamp_match.group(0) if timestamp_match else None

    def find_matching_pattern(self, line: str) -> Optional[str]:
        """Find the first matching pattern for a line"""
        return next((pattern for pattern, regex in self.compiled_patterns.items()
                     if regex.search(line)), None)


class LogAnalyzer:
    """Main class for log analysis"""

    def __init__(self, root_dir: str, output_dir: str):
        self.root_dir = root_dir
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime(DATE_FORMAT)

    def compile_patterns(self, patterns: List[str], ignore_patterns: List[str]) -> tuple:
        """Compile regex patterns"""
        compiled_patterns = {pattern: re.compile(pattern) for pattern in patterns}
        compiled_ignore_patterns = [re.compile(pattern) for pattern in ignore_patterns]
        return compiled_patterns, compiled_ignore_patterns

    def save_occurrence(self, log_entry: LogEntry) -> str:
        """Save individual occurrence to a separate file"""
        filename = f"{OCCURRENCE_PREFIX}_{log_entry.pattern}_{log_entry.occurrence_id}{LOG_EXT}"
        output_file = self.output_dir / filename

        with open(output_file, 'w', encoding=FILE_ENCODING) as f:
            f.write(f"Timestamp: {log_entry.timestamp}\n")
            f.write(f"Source File: {log_entry.file_path}\n")
            f.write(f"Pattern: {log_entry.pattern}\n")
            f.write("Content:\n")
            f.write(log_entry.content)
            f.write('\n')

        return str(output_file)

    def save_statistics(self, statistics: List[LogStatistics]) -> str:
        """Save all statistics to a single CSV file"""
        stats_file = self.output_dir / f"{STATISTICS_PREFIX}_{self.timestamp}{CSV_EXT}"

        stats_data = []
        for stat in statistics:
            stat_dict = stat._asdict()
            file_dist = stat_dict.pop('file_distribution')
            stat_dict.update({
                f"file_count_{k}": v for k, v in file_dist.items()
            })
            stats_data.append(stat_dict)

        pd.DataFrame(stats_data).to_csv(stats_file, index=False)
        return str(stats_file)

    def process_file(self, file_path: str, processor: LogFileProcessor,
                     seen_entries: Set[str]) -> List[LogEntry]:
        """Process a single log file and return log entries"""
        log_entries = []
        full_path = os.path.join(self.root_dir, file_path)

        try:
            with open(full_path, "r", encoding=FILE_ENCODING) as f:
                mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                content = mmapped_file.read().decode(FILE_ENCODING)
                lines = content.split('\n')

                current_block = []
                current_pattern = None
                current_timestamp = None

                for line in lines:
                    if processor.should_ignore(line):
                        continue

                    timestamp = processor.extract_timestamp(line)
                    if timestamp:
                        current_timestamp = timestamp

                    if processor.is_new_log_entry(line) and current_block:
                        self._handle_log_block(
                            current_block, current_pattern, current_timestamp,
                            file_path, seen_entries, log_entries
                        )
                        current_block = []
                        current_pattern = None

                    matched_pattern = processor.find_matching_pattern(line)
                    if matched_pattern:
                        current_pattern = matched_pattern

                    if current_pattern:
                        current_block.append(line)

                # Handle the last block
                if current_block and current_pattern:
                    self._handle_log_block(
                        current_block, current_pattern, current_timestamp,
                        file_path, seen_entries, log_entries
                    )

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")

        return log_entries

    def _handle_log_block(self, block: List[str], pattern: str, timestamp: str,
                          file_path: str, seen_entries: Set[str], log_entries: List[LogEntry]):
        """Handle a block of log lines"""
        normalized_block = '\n'.join(block).lower()
        if normalized_block not in seen_entries:
            occurrence_id = str(len(seen_entries) + 1)
            log_entries.append(LogEntry(
                timestamp=timestamp,
                pattern=pattern,
                content='\n'.join(block),
                file_path=file_path,
                occurrence_id=occurrence_id
            ))
            seen_entries.add(normalized_block)


class ParseLogFileTool(RemoteTool):
    """Main tool class for analyzing log files"""

    name: str = PARSE_LOG_FILE_TOOL.name
    args_schema: Type[RemoteInput] = ParseLogFileInput
    description: str = PARSE_LOG_FILE_TOOL.description
    root_dir: Optional[str] = DEFAULT_ROOT_DIR

    def _run(self,
             file_paths: List[str],
             patterns: List[str],
             ignore_patterns: List[str] = None,
             output_dir: Optional[str] = DEFAULT_OUTPUT_DIR,
             *args,
             **kwargs) -> str:

        try:
            output_dir = f"{self.root_dir}/{output_dir}"
            ignore_patterns = ignore_patterns or []  # Use empty list if None
            analyzer = LogAnalyzer(self.root_dir, output_dir)
            compiled_patterns, compiled_ignore_patterns = analyzer.compile_patterns(
                patterns, ignore_patterns
            )
            processor = LogFileProcessor(compiled_patterns, compiled_ignore_patterns)

            saved_files = []
            seen_entries = set()
            all_log_entries = []

            # Process all files
            for file_path in file_paths:
                log_entries = analyzer.process_file(file_path, processor, seen_entries)
                all_log_entries.extend(log_entries)

            # Save individual occurrences and collect statistics
            statistics = []
            if all_log_entries:
                df = pd.DataFrame([vars(entry) for entry in all_log_entries])
                df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP])

                # Save each occurrence separately
                for entry in all_log_entries:
                    saved_files.append(analyzer.save_occurrence(entry))

                # Collect statistics for each pattern
                for pattern in patterns:
                    pattern_df = df[df[PATTERN] == pattern]
                    if not pattern_df.empty:
                        statistics.append(LogStatistics(
                            total_occurrences=len(pattern_df),
                            unique_files=pattern_df[FILE_PATH].nunique(),
                            first_occurrence=str(pattern_df[TIMESTAMP].min()),
                            last_occurrence=str(pattern_df[TIMESTAMP].max()),
                            pattern=pattern,
                            file_distribution=pattern_df[FILE_PATH].value_counts().to_dict()
                        ))

                # Save consolidated statistics
                saved_files.append(analyzer.save_statistics(statistics))

            logger.info(f"Saved {len(saved_files)} files to {output_dir}")
            return str({'log_files': saved_files})

        except Exception as e:
            error_msg = f"Error analyzing log files: {str(e)}"
            logger.error(error_msg)
            return error_msg
