from __future__ import annotations

import re

from legacy_modernizer.models import PipelineInventory


def render_data_flow(inventory: PipelineInventory) -> str:
    lines = ["flowchart LR"]
    for name, node in inventory.nodes.items():
        node_id = safe_id(name)
        label = f"{name}\n({node.type}, conf={node.confidence:.2f})"
        shape = mermaid_shape(node.type, node_id, label)
        lines.append(f"    {shape}")
    for edge in inventory.edges:
        lines.append(f"    {safe_id(edge.source)} -->|{edge.relation} {edge.confidence:.2f}| {safe_id(edge.target)}")
    return "\n".join(lines) + "\n"


def safe_id(name: str) -> str:
    return "N_" + re.sub(r"[^a-zA-Z0-9_]", "_", name)


def mermaid_shape(node_type: str, node_id: str, label: str) -> str:
    escaped = label.replace('"', "'")
    if node_type == "source":
        return f'{node_id}[("{escaped}")]'
    if node_type == "sink":
        return f'{node_id}[["{escaped}"]]'
    if node_type == "transform":
        return f'{node_id}["{escaped}"]'
    if node_type == "task":
        return f'{node_id}{{"{escaped}"}}'
    return f'{node_id}["{escaped}"]'
