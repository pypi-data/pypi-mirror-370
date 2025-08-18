import pytest
from typing import Any
from pydantic_ai import Tool
from ToolsPydantic.abstract_py_tools import AbstractPyTools


def test_abstract_class_cannot_be_instantiated():
    """Test that AbstractPyTools cannot be instantiated directly"""
    with pytest.raises(TypeError) as excinfo:
        AbstractPyTools()
    assert "Can't instantiate abstract class" in str(excinfo.value)


def test_concrete_class_must_implement_abstract_methods():
    """Test that concrete subclasses must implement all abstract methods"""

    class IncompleteConcreteClass(AbstractPyTools):
        pass  # Doesn't implement required methods

    with pytest.raises(TypeError) as excinfo:
        IncompleteConcreteClass()
    assert "abstract method" in str(excinfo.value)


def test_complete_concrete_class_works():
    """Test that a properly implemented concrete class works"""

    class CompleteConcreteClass(AbstractPyTools):
        def get_tool(self) -> Tool:
            return Tool(self._run, name="test-tool", takes_ctx=False)

        def _run(self, *args: Any) -> str:
            return "test output"

    instance = CompleteConcreteClass()
    tool = instance.get_tool()

    assert isinstance(tool, Tool)
    assert tool.name == "test-tool"
    assert instance._run() == "test output"
