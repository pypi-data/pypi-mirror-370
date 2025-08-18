import requests

from pydantic_ai import Tool, ModelRetry
from opentelemetry import trace

from ToolsPydantic.abstract_py_tools import AbstractPyTools


class ReadPrivateNetworkPyTools(AbstractPyTools):
    def __init__(self, private_base_url: str):
        self.private_base_url = private_base_url
        pass

    def get_tool(self, ):
        summary = f"Read a page from the private network that wil start with {self.private_base_url} and return its contents."
        description = (
            f"<summary>{summary}</summary>"
            '<returns>\n'
            '<type>str</type>\n'
            '<description>The content of the page.\n'
            '    If the page cannot be found, raises a ModelRetry with a "Page not found" '
            'message.\n'
            '    If there is a network or other failure, raises a ModelRetry with details '
            'about the failure.</description>\n'
            '</returns>'
        )
        return Tool(self._run, name="Read-Private-Network-PyTools", takes_ctx=False, max_retries=2, description=description)

    def _run(self, url: str) -> str:
        """Read a page from the private network and return its contents.

        Args:
            url (str): The full URL of a private web page to read.

        Returns:
            str: The content of the page.
                If the page cannot be found, raises a ModelRetry with a "Page not found" message.
                If authentication fails, raises a ModelRetry with an "Unauthorized" message.
                If there is a network or other failure, raises a ModelRetry with details about the failure.
        """
        trace.get_current_span().set_attribute("input", url)

        if not url.startswith(self.private_base_url):
            raise ModelRetry(message=f"Page is not supported by this tool")

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                raise ModelRetry(message=f"Page not found at {url}")
            elif response.status_code == 401:
                raise ModelRetry(message=f"Unauthorized. Check credentials for {url}")
            elif response.status_code != 200:
                raise ModelRetry(message=f"Failed to fetch page {url}. Status code: {response.status_code}")

            content = response.text
            trace.get_current_span().set_attribute("output", content)
            return content

        except requests.exceptions.RequestException as e:
            raise ModelRetry(message=f"Failed to fetch page {url}. Exception: {str(e)}")