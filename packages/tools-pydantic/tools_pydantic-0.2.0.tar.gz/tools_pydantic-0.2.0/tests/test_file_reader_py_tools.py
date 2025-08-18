import pytest
from pydantic_ai import ModelRetry
from unittest.mock import patch, MagicMock

from ToolsPydantic.file_reader_py_tools import FileReaderPyTools


@pytest.fixture
def file_reader():
    return FileReaderPyTools()


@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with open(file_path, "w") as f:
        for i in range(1, 101):
            f.write(f"This is line {i}\n")
    return file_path


def test_get_tool(file_reader):
    tool = file_reader.get_tool()
    assert tool.name == "File-Reader-PyTools"
    assert tool.takes_ctx is False
    assert tool.max_retries == 2
    expected_description = (
        "<summary>Read a file and return its contents.</summary>\n"
        "<returns>\n"
        "<type>str</type>\n"
        "<description>The contents of the file from the specified line number for the specified number of lines.\n"
        "    If the file is a .go file, returns an error message directing to use the Go-Analyzer-Tool.\n"
        "    If the file cannot be read, returns an error message with details about the failure.</description>\n"
        "</returns>"
    )
    # Verify the description matches exactly
    assert tool.description == expected_description


def test_run_success(file_reader, temp_file):
    result = file_reader._run(str(temp_file), line_number=10, line_count=5)
    assert "File Line:10 to 15 from: 100" in result
    assert "This is line 11" in result
    assert "This is line 15" in result
    assert "--- start---" in result
    assert "--- end ---" in result


def test_run_file_not_found(file_reader):
    with pytest.raises(ModelRetry) as exc_info:
        file_reader._run("nonexistent_file.txt")
    assert "File not found" in str(exc_info.value)


def test_run_permission_error(file_reader, temp_file):
    with patch("builtins.open", side_effect=PermissionError("No permission")):
        with pytest.raises(ModelRetry) as exc_info:
            file_reader._run(str(temp_file))
        assert "Permission denied" in str(exc_info.value)


def test_run_general_exception(file_reader, temp_file):
    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        with pytest.raises(ModelRetry) as exc_info:
            file_reader._run(str(temp_file))
        assert "Failed to read file" in str(exc_info.value)


def test_run_line_number_exceeds_file_length(file_reader, temp_file):
    result = file_reader._run(str(temp_file), line_number=200, line_count=10)
    assert "File Line:200 to 210 from: 100" in result
    assert "--- start---\n\n--- end ---" in result  # Should be empty content


def test_run_zero_line_count(file_reader, temp_file):
    result = file_reader._run(str(temp_file), line_number=10, line_count=0)
    assert "File Line:10 to 10 from: 100" in result
    assert "--- start---\n\n--- end ---" in result  # Should be empty content


def test_run_negative_line_number(file_reader, temp_file):
    with pytest.raises(ValueError):
        file_reader._run(str(temp_file), line_number=-1)


def test_run_negative_line_count(file_reader, temp_file):
    with pytest.raises(ValueError):
        file_reader._run(str(temp_file), line_count=-1)


def test_tracing_attributes(file_reader, temp_file):
    with patch("opentelemetry.trace.get_current_span") as mock_span:
        mock_span.return_value = MagicMock()
        result = file_reader._run(str(temp_file))

        # Check that span attributes were set
        mock_span.return_value.set_attribute.assert_any_call("input", str(temp_file))
        mock_span.return_value.set_attribute.assert_called_with("output", result)


def test_run_empty_file(file_reader, tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()

    result = file_reader._run(str(empty_file))
    assert "File Line:0 to 200 from: 0" in result
    assert "--- start---\n\n--- end ---" in result
