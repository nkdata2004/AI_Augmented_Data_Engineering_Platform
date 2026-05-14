from pathlib import Path

from legacy_modernizer.analyzers.project_analyzer import analyze_project
from legacy_modernizer.confidence import score_inventory
from legacy_modernizer.lineage import build_lineage


def test_project_demo_analysis_runs():
    root = Path(__file__).resolve().parents[1] / "examples" / "legacy_pipeline"
    inv = analyze_project(root)
    assert "raw.customers" in inv.nodes
    assert "raw.orders" in inv.nodes
    assert "mart.customer_order_summary" in inv.nodes
    lineage = build_lineage(inv)
    assert lineage["edges"]
    confidence = score_inventory(inv)
    assert 0 <= confidence["artifact_confidence"] <= 1
