from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .mapping import detect_key_column, infer_column_mapping


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def compare_csvs(
    source_csv: str | Path,
    target_csv: str | Path,
    key_column: str | None = None,
    mapping_threshold: float = 0.40,
) -> dict[str, Any]:
    source_df = pd.read_csv(source_csv)
    target_df = pd.read_csv(target_csv)

    mappings = infer_column_mapping(list(source_df.columns), list(target_df.columns), threshold=mapping_threshold)
    key_mapping = detect_key_column(source_df, target_df, mappings, key_column)

    src_key, tgt_key = key_mapping["source_column"], key_mapping["target_column"]
    value_mappings = [m for m in mappings if m["source_column"] != src_key and m["target_column"] != tgt_key]

    source_indexed = source_df.set_index(src_key, drop=False)
    target_indexed = target_df.set_index(tgt_key, drop=False)
    source_keys = set(source_indexed.index.astype(str))
    target_keys = set(target_indexed.index.astype(str))

    new_rows = sorted(target_keys - source_keys)
    deleted_rows = sorted(source_keys - target_keys)
    common_keys = sorted(source_keys & target_keys)

    modified_rows: list[dict[str, Any]] = []
    mismatch_count = 0
    for key in common_keys:
        src_row = source_indexed.loc[source_indexed.index.astype(str) == key].iloc[0]
        tgt_row = target_indexed.loc[target_indexed.index.astype(str) == key].iloc[0]
        differences = []
        for m in value_mappings:
            src_col, tgt_col = m["source_column"], m["target_column"]
            src_val, tgt_val = _clean_value(src_row[src_col]), _clean_value(tgt_row[tgt_col])
            if src_val != tgt_val:
                mismatch_count += 1
                differences.append({
                    "source_column": src_col,
                    "target_column": tgt_col,
                    "source_value": src_val,
                    "target_value": tgt_val,
                    "mapping_confidence": m["confidence"],
                })
        if differences:
            modified_rows.append({"key": key, "differences": differences})

    mapped_source = {m["source_column"] for m in mappings}
    mapped_target = {m["target_column"] for m in mappings}
    unmapped_source = [c for c in source_df.columns if c not in mapped_source]
    unmapped_target = [c for c in target_df.columns if c not in mapped_target]

    mapping_confidence = sum(m["confidence"] for m in mappings) / max(len(mappings), 1)
    review_penalty = sum(1 for m in mappings if m.get("needs_review")) / max(len(mappings), 1) * 0.1
    overall_confidence = max(0.0, min(1.0, 0.75 * mapping_confidence + 0.25 * key_mapping["confidence"] - review_penalty))

    total_compared_rows = len(common_keys)
    unchanged_rows = total_compared_rows - len(modified_rows)
    match_rate = unchanged_rows / max(total_compared_rows, 1)

    return {
        "inputs": {"source_csv": str(source_csv), "target_csv": str(target_csv)},
        "overall_confidence": round(overall_confidence, 4),
        "confidence_breakdown": {
            "average_column_mapping_confidence": round(mapping_confidence, 4),
            "key_detection_confidence": key_mapping["confidence"],
            "low_confidence_mapping_penalty": round(review_penalty, 4),
        },
        "key_mapping": key_mapping,
        "column_mappings": mappings,
        "summary": {
            "source_row_count": int(len(source_df)),
            "target_row_count": int(len(target_df)),
            "compared_row_count": int(total_compared_rows),
            "new_row_count": len(new_rows),
            "deleted_row_count": len(deleted_rows),
            "modified_row_count": len(modified_rows),
            "value_mismatch_count": mismatch_count,
            "match_rate": round(match_rate, 4),
            "unmapped_source_columns": unmapped_source,
            "unmapped_target_columns": unmapped_target,
        },
        "row_diffs": {
            "new_rows": new_rows,
            "deleted_rows": deleted_rows,
            "modified_rows": modified_rows,
        },
        "human_review_flags": [m for m in mappings if m.get("needs_review")],
        "assumptions": [
            "CSV files fit in memory for the take-home demo; production path would stream or use a distributed engine.",
            "Semantic similarity uses BGE through sentence-transformers; the first run may download the model locally.",
            "For production-scale datasets, embeddings should be cached per normalized column name.",
            "Auto key detection favors uniqueness, overlap, and ID-like names; critical workflows should pass --key-column explicitly.",
        ],
    }
