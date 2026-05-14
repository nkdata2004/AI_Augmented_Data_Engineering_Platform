from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from .similarity import combined_similarity, normalize_column

ID_HINTS = {"id", "identifier", "key", "customer identifier", "customer id", "customerid", "cust id"}


def infer_column_mapping(source_columns: list[str], target_columns: list[str], threshold: float = 0.55) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for src in source_columns:
        for tgt in target_columns:
            score = combined_similarity(src, tgt)
            candidates.append({"source_column": src, "target_column": tgt, **asdict(score)})
    candidates.sort(key=lambda r: r["confidence"], reverse=True)

    used_src, used_tgt, mapping = set(), set(), []
    for row in candidates:
        if row["confidence"] < threshold:
            continue
        if row["source_column"] in used_src or row["target_column"] in used_tgt:
            continue
        row["needs_review"] = row["confidence"] < 0.75
        mapping.append(row)
        used_src.add(row["source_column"])
        used_tgt.add(row["target_column"])
    return sorted(mapping, key=lambda r: r["source_column"])


def detect_key_column(source_df: pd.DataFrame, target_df: pd.DataFrame, mapping: list[dict[str, Any]], user_key: str | None = None) -> dict[str, Any]:
    if user_key:
        for m in mapping:
            if user_key in {m["source_column"], m["target_column"]}:
                return {"source_column": m["source_column"], "target_column": m["target_column"], "confidence": 1.0, "method": "user_specified"}
        if user_key in source_df.columns and user_key in target_df.columns:
            return {"source_column": user_key, "target_column": user_key, "confidence": 1.0, "method": "user_specified_exact"}
        raise ValueError(f"User-specified key '{user_key}' was not found in the mapped or exact columns.")

    best: dict[str, Any] | None = None
    for m in mapping:
        src, tgt = m["source_column"], m["target_column"]
        s_unique = source_df[src].notna().mean() * (source_df[src].nunique(dropna=True) / max(len(source_df), 1))
        t_unique = target_df[tgt].notna().mean() * (target_df[tgt].nunique(dropna=True) / max(len(target_df), 1))
        key_hint = 0.2 if any(h in normalize_column(src) or h in normalize_column(tgt) for h in ID_HINTS) else 0.0
        overlap = len(set(source_df[src].dropna().astype(str)) & set(target_df[tgt].dropna().astype(str))) / max(
            len(set(source_df[src].dropna().astype(str)) | set(target_df[tgt].dropna().astype(str))), 1
        )
        confidence = min(1.0, 0.35 * s_unique + 0.35 * t_unique + 0.20 * overlap + key_hint)
        candidate = {"source_column": src, "target_column": tgt, "confidence": round(confidence, 4), "method": "auto_detected"}
        if best is None or candidate["confidence"] > best["confidence"]:
            best = candidate
    if not best or best["confidence"] < 0.45:
        raise ValueError("Could not confidently detect a row key. Re-run with --key-column.")
    return best
