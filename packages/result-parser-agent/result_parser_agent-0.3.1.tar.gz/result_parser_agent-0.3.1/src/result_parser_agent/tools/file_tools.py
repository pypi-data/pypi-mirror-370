"""Autonomous file analysis tools for the results parser agent."""

import re
from pathlib import Path
from typing import Any

from loguru import logger


def scan_directory(directory_path: str, file_pattern: str = "*.txt") -> list[str]:
    """
    Scan directory for result files matching the pattern.

    Args:
        directory_path: Path to the directory to scan
        file_pattern: File pattern to match (default: *.txt)

    Returns:
        List of file paths found
    """
    try:
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return []

        if not directory.is_dir():
            logger.error(f"Path is not a directory: {directory_path}")
            return []

        # Find all files matching the pattern (including subdirectories)
        if file_pattern == "*.txt":
            # Use recursive glob for .txt files to search subdirectories
            files = list(directory.rglob("*.txt"))
        else:
            files = list(directory.glob(file_pattern))
        file_paths = [str(f) for f in files if f.is_file()]

        logger.info(f"Found {len(file_paths)} files in {directory_path}")
        return file_paths

    except Exception as e:
        logger.error(f"Error scanning directory {directory_path}: {str(e)}")
        return []


def read_file_chunk(file_path: str, start_line: int = 0, num_lines: int = 100) -> str:
    """
    Read a chunk of lines from a file.

    Args:
        file_path: Path to the file to read
        start_line: Starting line number (0-based)
        num_lines: Number of lines to read

    Returns:
        File content as string
    """
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        if start_line >= len(lines):
            return ""

        end_line = min(start_line + num_lines, len(lines))
        chunk_lines = lines[start_line:end_line]

        content = "".join(chunk_lines)
        logger.debug(
            f"Read {len(chunk_lines)} lines from {file_path} (lines {start_line+1}-{end_line})"
        )

        return content

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""


def grep_file(
    file_path: str, pattern: str, case_sensitive: bool = False, max_matches: int = 50
) -> list[dict[str, Any]]:
    """
    Search for a pattern in a file and return matches with context.

    Args:
        file_path: Path to the file to search
        pattern: Pattern to search for
        case_sensitive: Whether search is case sensitive
        max_matches: Maximum number of matches to return

    Returns:
        List of matches with line numbers and context
    """
    try:
        matches = []
        flags = 0 if case_sensitive else re.IGNORECASE

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                if re.search(pattern, line, flags):
                    # Get context (previous and next lines)
                    context_start = max(0, line_num - 3)
                    context_end = line_num + 2

                    match_info = {
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "pattern": pattern,
                        "context_start": context_start,
                        "context_end": context_end,
                    }
                    matches.append(match_info)

                    if len(matches) >= max_matches:
                        break

        logger.debug(
            f"Found {len(matches)} matches for pattern '{pattern}' in {file_path}"
        )
        return matches

    except Exception as e:
        logger.error(f"Error searching pattern '{pattern}' in {file_path}: {str(e)}")
        return []
