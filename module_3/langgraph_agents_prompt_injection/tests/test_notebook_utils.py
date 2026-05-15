from src.agent_platform.notebook_utils import (
    build_customer_name_notebook,
    extract_code_cells,
    notebook_to_json,
)


def test_build_notebook_has_required_sections() -> None:
    notebook_json = notebook_to_json(build_customer_name_notebook("Normalize names"))

    assert "# Problem Statement" in notebook_json
    assert "# Requirements" in notebook_json
    assert "normalize_customer_name" in notebook_json


def test_extract_code_cells_skips_requirements_cell() -> None:
    notebook_json = notebook_to_json(build_customer_name_notebook("Normalize names"))
    code = extract_code_cells(notebook_json)

    assert "pip install" not in code
    assert "def normalize_customer_name" in code
