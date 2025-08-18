import pytest
from unittest.mock import patch, MagicMock

from ToolsPydantic.list_project_files_py_tools import ListProjectFilesPyTools


@pytest.fixture
def project_lister():
    return ListProjectFilesPyTools()


@pytest.fixture
def custom_lister():
    return ListProjectFilesPyTools(
        ignored_dirs=["custom_ignore_dir"],
        ignored_extensions=[".ignore"]
    )


@pytest.fixture
def mock_directory_structure(tmp_path):
    # Create a test directory structure
    root = tmp_path / "test_project"
    root.mkdir()

    # Create files in root
    (root / "file1.txt").touch()
    (root / "file2.py").touch()
    (root / "file.ignore").touch()

    # Create subdirectories
    (root / "docs").mkdir()
    (root / "docs" / "readme.md").touch()

    (root / "tests").mkdir()
    (root / "tests" / "test_file.py").touch()

    (root / ".git").mkdir()  # Should be ignored by default
    (root / ".git" / "config").touch()

    (root / "custom_ignore_dir").mkdir()  # For custom ignore tests
    (root / "custom_ignore_dir" / "file.txt").touch()

    return root


def test_get_tool(project_lister):
    tool = project_lister.get_tool()
    assert tool.name == "List-Project-Files-PyTools"
    assert tool.takes_ctx is False
    assert tool.max_retries == 2
    expected_description = (
        '<summary>List files in a directory recursively, grouping them by directory.\n'
        '\n'
        'This function walks through the directory tree starting from the given path,\n'
        'collecting all files and organizing them by their parent directories.\n'
        'It skips any directories specified in the ignored_dirs list.</summary>\n'
        '<returns>\n'
        '<type>str</type>\n'
        '<description>A formatted string containing the directory structure and files,\n'
        "    with files grouped by their parent directories. Each directory's\n"
        '    files are listed on a new line, sorted alphabetically.</description>\n'
        '</returns>'
    )
    assert tool.description == expected_description


def test_run_basic_structure(project_lister, mock_directory_structure):
    result = project_lister._run(str(mock_directory_structure))

    print(result)
    assert "Files grouped by directory" in result
    assert str(mock_directory_structure) in result
    assert "/: ['file.ignore', 'file1.txt', 'file2.py']" in result
    assert "/docs: ['readme.md']" in result
    assert "/tests: ['test_file.py']" in result
    assert ".git" not in result  # Should be ignored by default


def test_run_with_trailing_slash(project_lister, mock_directory_structure):
    result = project_lister._run(str(mock_directory_structure) + "/")
    assert "/: ['file.ignore', 'file1.txt', 'file2.py']" in result


def test_run_empty_directory(tmp_path, project_lister):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = project_lister._run(str(empty_dir))
    assert f"No files found in {empty_dir}." in result


def test_run_default_ignores(project_lister, mock_directory_structure):
    result = project_lister._run(str(mock_directory_structure))
    assert ".git" not in result
    assert "file.ignore" in result  # .tmp not in default ignored extensions


def test_run_custom_ignores(custom_lister, mock_directory_structure):
    result = custom_lister._run(str(mock_directory_structure))
    print(result)
    assert "custom_ignore_dir" not in result
    assert "file.ignore" not in result


def test_run_tracing(project_lister, mock_directory_structure):
    with patch('opentelemetry.trace.get_current_span') as mock_span:
        mock_span.return_value = MagicMock()
        result = project_lister._run(str(mock_directory_structure))

        mock_span.return_value.set_attribute.assert_any_call(
            "input", str(mock_directory_structure)
        )
        mock_span.return_value.set_attribute.assert_called_with(
            "output", result
        )


def test_run_directory_not_found(project_lister):
    result = project_lister._run("/nonexistent/path")
    assert "No files found in /nonexistent/path." in result


def test_run_with_no_ignores():
    lister = ListProjectFilesPyTools(ignored_dirs=[], ignored_extensions=[])
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ("/root", [".git", "docs"], ["file1.txt", "file2.py"]),
            ("/root/.git", [], ["config"]),
            ("/root/docs", [], ["readme.md"]),
        ]
        result = lister._run("/root")

        assert "/: ['file1.txt', 'file2.py']" in result
        assert "/.git: ['config']" in result
        assert "/docs: ['readme.md']" in result


def test_run_output_format(project_lister, mock_directory_structure):
    result = project_lister._run(str(mock_directory_structure))

    print(str(mock_directory_structure))

    # Check the basic output format
    assert result.startswith(f"Files grouped by directory (relative to {mock_directory_structure}):")

    # Check each directory is on its own line
    lines = result.split('\n')
    assert any(line.startswith("/:") for line in lines)
    assert any(line.startswith("/docs:") for line in lines)
    assert any(line.startswith("/tests:") for line in lines)
