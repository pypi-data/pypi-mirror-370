"""LangChain tool definitions for the results parser agent."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from .file_tools import grep_file, read_file_chunk, scan_directory


# Pydantic schemas for tool arguments
class ScanInputArgs(BaseModel):
    input_path: str = Field(description="Path to file or directory to scan")


class ReadFileChunkArgs(BaseModel):
    file_path: str = Field(description="Path to the file to read")
    start_line: int = Field(description="Starting line number (0-based)", default=0)
    num_lines: int = Field(description="Number of lines to read", default=100)


class GrepFileArgs(BaseModel):
    file_path: str = Field(description="Path to the file to search")
    pattern: str = Field(description="Pattern to search for")
    case_sensitive: bool = Field(
        description="Whether search is case sensitive", default=False
    )
    max_matches: int = Field(
        description="Maximum number of matches to return", default=50
    )


class ExecuteCommandArgs(BaseModel):
    command: str = Field(description="Command to execute in terminal")
    working_directory: str = Field(
        description="Working directory for command", default="."
    )


class ToolHandler:
    """Handler class for tool functions."""

    def __init__(self, state_manager: Any = None) -> None:
        self.state_manager = state_manager

    def scan_input(self, input_path: str) -> dict[str, Any]:
        """Scan input path to identify files to process."""
        try:
            logger.info(f"🔍 Scanning input path: {input_path}")
            files = scan_directory(input_path)
            result = {
                "input_path": input_path,
                "files_found": len(files),
                "file_paths": files,
                "is_single_file": len(files) == 1,
            }
            logger.info(f"✅ Scan completed: {len(files)} files found")
            return result
        except Exception as e:
            logger.error(f"❌ Error scanning input {input_path}: {str(e)}")
            return {"error": str(e)}

    def read_file_chunk(
        self, file_path: str, start_line: int = 0, num_lines: int = 100
    ) -> str:
        """Read a chunk of lines from a file."""
        try:
            logger.debug(
                f"📖 Reading file chunk: {file_path} (lines {start_line}-{start_line + num_lines})"
            )
            content = read_file_chunk(file_path, start_line, num_lines)
            logger.debug(f"✅ File chunk read successfully: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"❌ Error reading file chunk {file_path}: {str(e)}")
            return f"Error: {str(e)}"

    def grep_file(
        self,
        file_path: str,
        pattern: str,
        case_sensitive: bool = False,
        max_matches: int = 50,
    ) -> list[dict[str, Any]]:
        """Search for any pattern in a file."""
        try:
            logger.info(f"🔍 Grepping file: {file_path} for pattern: '{pattern}'")
            result = grep_file(file_path, pattern, case_sensitive, max_matches)
            logger.info(f"✅ Grep completed: {len(result)} matches found")
            return result
        except Exception as e:
            logger.error(f"❌ Error grepping file {file_path}: {str(e)}")
            return [{"error": str(e)}]

    def execute_command(
        self, command: str, working_directory: str = "."
    ) -> dict[str, Any]:
        """Execute a command in the terminal."""
        try:
            import os
            import subprocess

            logger.info(f"🖥️  Executing command: {command}")
            if working_directory != ".":
                logger.info(f"📁 Working directory: {working_directory}")

            # Change to working directory if specified
            original_cwd = os.getcwd()
            if working_directory != ".":
                os.chdir(working_directory)

            # Execute command
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            # Restore original directory
            if working_directory != ".":
                os.chdir(original_cwd)

            # Log command results
            if result.returncode == 0:
                logger.info(
                    f"✅ Command executed successfully (return code: {result.returncode})"
                )
                if result.stdout.strip():
                    logger.debug(
                        f"📤 Command output: {len(result.stdout.strip())} characters"
                    )
                if result.stderr.strip():
                    logger.warning(f"⚠️  Command stderr: {result.stderr.strip()}")
            else:
                logger.warning(
                    f"⚠️  Command completed with non-zero return code: {result.returncode}"
                )
                if result.stderr.strip():
                    logger.warning(f"⚠️  Command stderr: {result.stderr.strip()}")

            return {
                "command": command,
                "working_directory": working_directory,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            logger.error(f"❌ Error executing command '{command}': {str(e)}")
            return {"error": str(e)}


def create_tools(state_manager: Any) -> list[Any]:
    """Create LangChain tools with proper schemas."""
    handler = ToolHandler(state_manager)

    from langchain_core.tools import StructuredTool

    tools = [
        StructuredTool(
            name="scan_input",
            description="Scan input path (file or directory) to identify files to process",
            func=handler.scan_input,
            args_schema=ScanInputArgs,
        ),
        StructuredTool(
            name="read_file_chunk",
            description="Read a chunk of lines from a file",
            func=handler.read_file_chunk,
            args_schema=ReadFileChunkArgs,
        ),
        StructuredTool(
            name="grep_file",
            description="Search for any pattern in a file - use this to discover metrics and patterns",
            func=handler.grep_file,
            args_schema=GrepFileArgs,
        ),
        StructuredTool(
            name="execute_command",
            description="Execute a command in the terminal (useful for file analysis, grep, etc.)",
            func=handler.execute_command,
            args_schema=ExecuteCommandArgs,
        ),
    ]

    return tools
