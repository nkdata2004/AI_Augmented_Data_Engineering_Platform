from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from legacy_modernizer.models import Evidence, PipelineInventory, relpath


def analyze_yaml_file(path: Path, base: Path, inventory: PipelineInventory) -> None:
    short = relpath(path, base)
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    name = data.get("pipeline_name") or path.stem
    config_node = f"config::{name}"
    inventory.add_node(config_node, "config", Evidence(short, "YAML config", 0.85), **data)

    for src in data.get("sources", []) or []:
        inventory.add_node(str(src), "source", Evidence(short, "Declared YAML source", 0.9))
        inventory.add_edge(str(src), config_node, "declared_in", Evidence(short, "Source declared in config", 0.9), 0.9)
    for sink in data.get("sinks", []) or []:
        inventory.add_node(str(sink), "sink", Evidence(short, "Declared YAML sink", 0.9))
        inventory.add_edge(config_node, str(sink), "declares_sink", Evidence(short, "Sink declared in config", 0.9), 0.9)
    if data.get("schedule"):
        inventory.schedules[config_node] = str(data["schedule"])
    if data.get("volume_hints"):
        inventory.volume_hints.update({str(k): str(v) for k, v in data["volume_hints"].items()})
    if not data.get("owner"):
        inventory.gaps.append(f"{short}: owner is missing")
