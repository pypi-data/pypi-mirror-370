import os

from opentelemetry import trace
from pydantic_ai import ModelRetry, Tool

from ToolsPydantic.abstract_py_tools import AbstractPyTools


class FileReaderPyTools(AbstractPyTools):
    def __init__(self):
        pass

    def get_tool(self):
        return Tool(self._run, name="File-Reader-PyTools", takes_ctx=False, max_retries=2)

    def _run(self, file_path: str, line_number: int = 0, line_count: int = 200) -> str:
        """Read a file and return its contents.

        Args:
            file_path (str): The path to the file to read.
            line_number (int, optional): The starting line number to read from. Defaults to 0.
            line_count (int, optional): The number of lines to read. Defaults to 200.

        Returns:
            str: The contents of the file from the specified line number for the specified number of lines.
                If the file is a .go file, returns an error message directing to use the Go-Analyzer-Tool.
                If the file cannot be read, returns an error message with details about the failure.
        """

        # Input validation
        if line_number < 0:
            raise ValueError("line_number must be non-negative")
        if line_count < 0:
            raise ValueError("line_count must be non-negative")

        trace.get_current_span().set_attribute("input", file_path)

        if not os.path.exists(file_path):
            raise ModelRetry(message="File not found")

        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                total_lines = len(lines)

                if line_number > 0:
                    lines = lines[line_number:]
                lines = lines[:line_count]

                output = (
                    f"File Line:{line_number} to {line_number + line_count} from: {total_lines}\n--- start---\n"
                    + "".join(lines)
                    + "\n--- end ---\n"
                )
                trace.get_current_span().set_attribute("output", output)

                return output
        except PermissionError:
            raise ModelRetry(message="Permission denied when trying to read file")
        except Exception as e:
            raise ModelRetry(message=f"Failed to read file {file_path}. {str(e)}")
