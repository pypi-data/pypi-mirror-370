import pytest
from unittest.mock import patch, MagicMock
from pydantic_ai import ModelRetry
from ToolsPydantic.read_private_network_py_tools import ReadPrivateNetworkPyTools
import requests

PRIVATE_BASE_URL = "https://internal.example.com"


@pytest.fixture
def private_py_tools():
    return ReadPrivateNetworkPyTools(private_base_url=PRIVATE_BASE_URL)


def test_get_tool_description(private_py_tools):
    tool = private_py_tools.get_tool()
    expected_description = (
        f"<summary>Read a page from the private network that wil start with {PRIVATE_BASE_URL} and return its contents.</summary>"
        '<returns>\n'
        '<type>str</type>\n'
        '<description>The content of the page.\n'
        '    If the page cannot be found, raises a ModelRetry with a "Page not found" '
        'message.\n'
        '    If there is a network or other failure, raises a ModelRetry with details '
        'about the failure.</description>\n'
        '</returns>'
    )

    assert tool.description == expected_description
    assert tool.name == "Read-Private-Network-PyTools"
    assert tool.takes_ctx is False
    assert tool.max_retries == 2


def test_run_success(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/data"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Mock response content"

    with patch('requests.get', return_value=mock_response) as mock_get:
        with patch('opentelemetry.trace.get_current_span') as mock_span:
            mock_span.return_value = MagicMock()
            result = private_py_tools._run(test_url)

            mock_get.assert_called_once_with(test_url, timeout=10)
            mock_span.return_value.set_attribute.assert_any_call("input", test_url)
            mock_span.return_value.set_attribute.assert_called_with("output", "Mock response content")
            assert result == "Mock response content"


def test_run_invalid_url(private_py_tools):
    test_url = "https://external.example.com/api/data"
    with pytest.raises(ModelRetry) as exc_info:
        private_py_tools._run(test_url)
    assert "Page is not supported by this tool" in str(exc_info.value)


def test_run_page_not_found(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/missing"
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Page not found at" in str(exc_info.value)


def test_run_unauthorized(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/secure"
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Unauthorized. Check credentials for" in str(exc_info.value)


def test_run_server_error(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/error"
    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Failed to fetch page" in str(exc_info.value)
        assert "Status code: 500" in str(exc_info.value)


def test_run_connection_error(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/data"

    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Failed to fetch page" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)


def test_run_timeout_error(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/data"

    with patch('requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Failed to fetch page" in str(exc_info.value)
        assert "Request timed out" in str(exc_info.value)


def test_run_other_request_exception(private_py_tools):
    test_url = f"{PRIVATE_BASE_URL}/api/data"

    with patch('requests.get', side_effect=requests.exceptions.RequestException("Unknown error")):
        with pytest.raises(ModelRetry) as exc_info:
            private_py_tools._run(test_url)
        assert "Failed to fetch page" in str(exc_info.value)
        assert "Unknown error" in str(exc_info.value)
