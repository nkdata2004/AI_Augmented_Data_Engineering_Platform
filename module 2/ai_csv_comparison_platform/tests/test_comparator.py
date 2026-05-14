from pathlib import Path

from csv_compare.comparator import compare_csvs

ROOT = Path(__file__).resolve().parents[1]


def test_compare_demo_files():
    report = compare_csvs(ROOT / "examples/source_customers.csv", ROOT / "examples/target_customers.csv")
    assert report["key_mapping"]["source_column"] == "cust_id"
    assert report["summary"]["new_row_count"] == 1
    assert report["summary"]["deleted_row_count"] == 1
    assert report["summary"]["modified_row_count"] >= 1
    assert report["summary"]["unmapped_source_columns"] == []
    assert "loyalty_tier" in report["summary"]["unmapped_target_columns"]
