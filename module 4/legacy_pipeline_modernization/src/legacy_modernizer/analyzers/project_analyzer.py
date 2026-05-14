from __future__ import annotations

from pathlib import Path

from legacy_modernizer.analyzers.python_analyzer import analyze_python_file
from legacy_modernizer.analyzers.sql_analyzer import analyze_sql_file
from legacy_modernizer.analyzers.yaml_analyzer import analyze_yaml_file
from legacy_modernizer.models import PipelineInventory


def analyze_project(input_dir: Path) -> PipelineInventory:
    inventory = PipelineInventory()
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    files = [p for p in input_dir.rglob("*") if p.is_file()]
    if not files:
        inventory.gaps.append("Input directory contains no files")
        return inventory

    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".sql":
            analyze_sql_file(path, input_dir, inventory)
        elif suffix == ".py":
            analyze_python_file(path, input_dir, inventory)
        elif suffix in {".yaml", ".yml"}:
            analyze_yaml_file(path, input_dir, inventory)
        else:
            inventory.gaps.append(f"Unsupported artifact type skipped: {path.name}")

    detect_broken_file_references(inventory, input_dir)
    detect_missing_documentation(inventory)
    return inventory


def detect_broken_file_references(inventory: PipelineInventory, input_dir: Path) -> None:
    known_files = {str(p.relative_to(input_dir)).replace("\\", "/") for p in input_dir.rglob("*") if p.is_file()}
    for edge in inventory.edges:
        if edge.relation == "references_file":
            target = edge.target.replace("\\", "/")
            if target not in known_files and not any(k.endswith(target) for k in known_files):
                inventory.gaps.append(f"Broken or unresolved file reference: {edge.source} -> {edge.target}")


def detect_missing_documentation(inventory: PipelineInventory) -> None:
    for node in inventory.nodes.values():
        if node.type in {"transform", "sink"} and not node.metadata.get("description"):
            if not any("Business purpose" in ev.detail for ev in node.evidence):
                inventory.gaps.append(f"{node.name}: missing explicit documentation/description")
