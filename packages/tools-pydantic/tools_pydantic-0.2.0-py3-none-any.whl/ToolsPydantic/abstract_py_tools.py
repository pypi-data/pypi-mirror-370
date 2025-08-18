from abc import ABC, abstractmethod
from pydantic_ai import Tool
from typing import Any, Optional


class AbstractPyTools(ABC):
    @abstractmethod
    def get_tool(self) -> Tool:
        pass

    @abstractmethod
    def _run(self, *args: Any) -> str:
        pass