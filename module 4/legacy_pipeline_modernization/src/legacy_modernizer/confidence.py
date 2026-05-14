from __future__ import annotations

from statistics import mean

from legacy_modernizer.models import PipelineInventory


def score_inventory(inventory: PipelineInventory) -> dict:
    node_scores = {name: round(node.confidence, 3) for name, node in inventory.nodes.items()}
    edge_scores = [edge.confidence for edge in inventory.edges]
    gap_penalty = min(0.25, 0.03 * len(inventory.gaps))
    base = mean(list(node_scores.values()) + edge_scores) if node_scores or edge_scores else 0.0
    artifact_score = max(0.0, base - gap_penalty)
    return {
        "artifact_confidence": round(artifact_score, 3),
        "node_confidence": node_scores,
        "edge_confidence": [
            {"source": e.source, "target": e.target, "relation": e.relation, "confidence": round(e.confidence, 3)}
            for e in inventory.edges
        ],
        "penalties": {
            "gap_count": len(inventory.gaps),
            "gap_penalty": round(gap_penalty, 3),
        },
        "interpretation": confidence_label(artifact_score),
    }


def confidence_label(score: float) -> str:
    if score >= 0.85:
        return "High: mostly deterministic evidence"
    if score >= 0.7:
        return "Medium: usable draft with targeted human review"
    return "Low: requires substantial human validation"
