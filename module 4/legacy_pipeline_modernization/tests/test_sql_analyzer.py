from pathlib import Path

from legacy_modernizer.analyzers.sql_analyzer import analyze_sql_file, infer_select_columns
from legacy_modernizer.models import PipelineInventory


def test_infer_select_columns_handles_aggregates():
    sql = "SELECT c.id AS customer_id, SUM(o.amount) AS total_amount FROM c JOIN o ON c.id=o.id"
    cols = infer_select_columns(sql)
    assert {c["output_column"] for c in cols} == {"customer_id", "total_amount"}
    assert any(c["confidence"] == "medium" for c in cols)


def test_sql_analysis_adds_sources_transform_sink(tmp_path: Path):
    sql_path = tmp_path / "x.sql"
    sql_path.write_text("CREATE TABLE mart.t AS SELECT a.id FROM raw.a a JOIN raw.b b ON a.id=b.id", encoding="utf-8")
    inv = PipelineInventory()
    analyze_sql_file(sql_path, tmp_path, inv)
    assert "raw.a" in inv.nodes
    assert "raw.b" in inv.nodes
    assert "mart.t" in inv.nodes
    assert any(e.target == "mart.t" for e in inv.edges)
