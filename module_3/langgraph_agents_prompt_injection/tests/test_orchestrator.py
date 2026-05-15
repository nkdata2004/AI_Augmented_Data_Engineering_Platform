from pathlib import Path

from src.agent_platform.orchestrator import run_workflow


def test_run_workflow_creates_expected_artifacts(tmp_path: Path) -> None:
    final_state = run_workflow("Create a function that normalizes messy names", tmp_path)

    assert final_state["verdict"] == "APPROVED"
    assert (tmp_path / "developer_notebook.ipynb").exists()
    assert (tmp_path / "generated_module.py").exists()
    assert (tmp_path / "test_generated_module.py").exists()
    assert (tmp_path / "review_report.md").exists()
    assert (tmp_path / "run_summary.json").exists()
