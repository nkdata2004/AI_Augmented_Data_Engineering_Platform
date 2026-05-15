"""Notebook creation and extraction utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


REQUIREMENTS_CELL = """# Requirements\n# pip install pytest nbformat langgraph pydantic"""


IMPLEMENTATION_CODE = '''import re
from typing import Any


def normalize_customer_name(value: Any) -> str:
    """Normalize a customer name for matching and display.

    Args:
        value: Customer name supplied by an upstream system.

    Returns:
        A normalized name with collapsed whitespace and title casing.

    Raises:
        TypeError: If value is not a string.
    """
    if not isinstance(value, str):
        raise TypeError("Customer name must be a string.")

    collapsed = re.sub(r"\\s+", " ", value.strip())
    if not collapsed:
        return ""

    return collapsed.title()
'''


EXAMPLE_CODE = '''examples = [
    "  jane   DOE ",
    "ACME     corporation",
    "   ",
]

for raw_name in examples:
    print(f"{raw_name!r} -> {normalize_customer_name(raw_name)!r}")
'''


def build_customer_name_notebook(task: str, reviewer_feedback: str = "") -> nbformat.NotebookNode:
    """Build a deterministic notebook for the demo task."""
    feedback_note = (
        f"\n\nRevision notes addressed: {reviewer_feedback}"
        if reviewer_feedback
        else ""
    )
    return new_notebook(
        cells=[
            new_markdown_cell(f"# Problem Statement\n\n{task}{feedback_note}"),
            new_code_cell(REQUIREMENTS_CELL),
            new_markdown_cell("## Imports\n\nImports are kept minimal and standard-library only."),
            new_code_cell("import re\nfrom typing import Any"),
            new_markdown_cell("## Implementation"),
            new_code_cell(IMPLEMENTATION_CODE),
            new_markdown_cell("## Example Usage"),
            new_code_cell(EXAMPLE_CODE),
            new_markdown_cell(
                "## Results\n\nThe function returns normalized names and raises `TypeError` "
                "for non-string inputs."
            ),
        ],
        metadata={"language_info": {"name": "python"}},
    )


def notebook_to_json(notebook: nbformat.NotebookNode) -> str:
    """Serialize a notebook to formatted JSON."""
    return nbformat.writes(notebook)


def write_notebook(notebook_json: str, path: Path) -> None:
    """Write notebook JSON to disk after validating its structure."""
    notebook = nbformat.reads(notebook_json, as_version=4)
    nbformat.validate(notebook)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(nbformat.writes(notebook), encoding="utf-8")


def extract_code_cells(notebook_json: str) -> str:
    """Extract Python code cells from notebook JSON."""
    notebook = nbformat.reads(notebook_json, as_version=4)
    code_cells: list[str] = []
    for cell in notebook.cells:
        if cell.get("cell_type") == "code":
            source = cell.get("source", "")
            if source.strip() and not source.lstrip().startswith("# Requirements"):
                code_cells.append(source)
    return "\n\n".join(code_cells).strip() + "\n"


def write_module_from_code(code: str, path: Path) -> None:
    """Write extracted implementation code as an importable Python module."""
    marker = "def normalize_customer_name"
    if marker in code:
        function_start = code.index(marker)
        example_start = code.find("examples =", function_start)
        function_code = code[function_start:example_start].strip() if example_start != -1 else code[function_start:].strip()
        module_code = "import re\nfrom typing import Any\n\n\n" + function_code
    else:
        module_code = code
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(module_code.strip() + "\n", encoding="utf-8")


def load_json_file(path: Path) -> dict[str, Any]:
    """Load JSON from disk."""
    return json.loads(path.read_text(encoding="utf-8"))
