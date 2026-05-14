from pathlib import Path

from legacy_modernizer.cli import run_analyze


def test_cli_writes_outputs(tmp_path: Path):
    root = Path(__file__).resolve().parents[1] / "examples" / "legacy_pipeline"
    out = tmp_path / "out"
    run_analyze(root, out, "Migrate from Airflow + raw SQL to dbt + Prefect on Snowflake")
    assert (out / "inventory.json").exists()
    assert (out / "data_flow.mmd").exists()
    assert (out / "migrated" / "prefect" / "flow.py").exists()
