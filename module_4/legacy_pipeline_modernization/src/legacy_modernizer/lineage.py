from __future__ import annotations

from legacy_modernizer.models import PipelineInventory


def build_lineage(inventory: PipelineInventory) -> dict:
    column_lineage = []
    for node in inventory.nodes.values():
        if node.type != "transform":
            continue
        for col in node.metadata.get("selected_columns", []) or []:
            confidence = 0.82 if col["confidence"] == "high" else 0.64
            human_review = confidence < 0.7
            column_lineage.append({
                "transform": node.name,
                "output_column": col["output_column"],
                "source_expression": col["expression"],
                "confidence": confidence,
                "human_review_required": human_review,
            })
    return {
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "relation": edge.relation,
                "confidence": edge.confidence,
                "human_review_required": edge.confidence < 0.7,
            }
            for edge in inventory.edges
        ],
        "column_lineage": column_lineage,
        "known_gaps": [gap for gap in inventory.gaps if "lineage" in gap.lower() or "dynamic" in gap.lower()],
    }
