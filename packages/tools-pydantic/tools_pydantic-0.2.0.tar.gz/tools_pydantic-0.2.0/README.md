# PyTools

A collection of Pydantic-powered tools for building AI agents.  
Includes utilities such as file readers, file listers, private network readers, crawlers, and more — all designed to integrate smoothly with agent frameworks.

---

## 🚀 Features

- **Typed Tools** — Strict input/output validation with Pydantic models.  
- **Reusable Components** — Common utilities like file reading, listing, and crawling.  
- **Agent-Friendly** — Easily pluggable into LLM agents or tool-based frameworks.  
- **Modern Packaging** — Built and published using [`uv`](https://github.com/astral-sh/uv).  

---

## 📦 Installation

```bash
pip install tools-pydantic
```

Or, if you’re using uv
```bash
uv pip install tools-pydantic
```

## 🛠️ Usage

```python
from ToolsPydantic import FileReaderPyTools, ListProjectFilesPyTools, ReadPrivateNetworkPyTools
from pydantic_ai import Agent

# Example usage
tool = FileReaderPyTools().get_tool()
Agent(
    name="Example Agent",
    # ...
    tools=[
        FileReaderPyTools().get_tool(),
        ListProjectFilesPyTools().get_tool(),
        ReadPrivateNetworkPyTools("https://example.private.tech").get_tool()
    ]
)
```

## 🧪 Running Tests

```bash
uv run pytest
```

This project uses pytest and coverage.

To check coverage:

```bash
uv run coverage run -m pytest
uv run coverage report -m
```
