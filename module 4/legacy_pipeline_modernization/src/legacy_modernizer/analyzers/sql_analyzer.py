from __future__ import annotations

import re
from pathlib import Path

from legacy_modernizer.models import Evidence, PipelineInventory, relpath

TABLE_RE = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)?)", re.I)
TARGET_RE = re.compile(r"\b(?:create\s+table|insert\s+into)\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)?)", re.I)
SELECT_RE = re.compile(r"select\s+(.*?)\s+from\s", re.I | re.S)
ALIAS_RE = re.compile(r"(.+?)\s+as\s+([a-zA-Z_][\w]*)$", re.I)


def analyze_sql_file(path: Path, base: Path, inventory: PipelineInventory) -> None:
    text = path.read_text(encoding="utf-8")
    short = relpath(path, base)
    sources = sorted(set(TABLE_RE.findall(text)))
    targets = sorted(set(TARGET_RE.findall(text)))

    for src in sources:
        inventory.add_node(src, "source", Evidence(short, "SQL FROM/JOIN reference", 0.86))
    for tgt in targets:
        inventory.add_node(tgt, "sink", Evidence(short, "SQL CREATE TABLE/INSERT target", 0.92))

    transform_name = f"transform::{path.stem}"
    inventory.add_node(transform_name, "transform", Evidence(short, "SQL transformation script", 0.9), file=short)
    for src in sources:
        inventory.add_edge(src, transform_name, "feeds", Evidence(short, "SQL source feeds transformation", 0.86), 0.86)
    for tgt in targets:
        inventory.add_edge(transform_name, tgt, "writes", Evidence(short, "SQL transformation writes target", 0.92), 0.92)

    columns = infer_select_columns(text)
    if columns:
        inventory.nodes[transform_name].metadata["selected_columns"] = columns
    if "select *" in text.lower():
        inventory.gaps.append(f"{short}: wildcard SELECT makes column-level lineage low confidence")


def infer_select_columns(sql: str) -> list[dict[str, str]]:
    match = SELECT_RE.search(sql)
    if not match:
        return []
    raw = match.group(1)
    columns: list[dict[str, str]] = []
    for part in split_select_list(raw):
        item = part.strip()
        if not item:
            continue
        alias_match = ALIAS_RE.match(item)
        if alias_match:
            expression, output = alias_match.groups()
        else:
            expression = item
            output = item.split(".")[-1]
        confidence = "high" if re.match(r"^[a-zA-Z_]\w*\.[a-zA-Z_]\w*$", expression.strip()) else "medium"
        if any(fn in expression.lower() for fn in ["sum(", "count(", "max(", "min(", "avg("]):
            confidence = "medium"
        columns.append({"output_column": output.strip(), "expression": expression.strip(), "confidence": confidence})
    return columns


def split_select_list(raw: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current = []
    for char in raw:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return parts
