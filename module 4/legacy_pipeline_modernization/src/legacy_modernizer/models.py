from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Literal

NodeType = Literal["source", "transform", "sink", "task", "config", "unknown"]


@dataclass
class Evidence:
    path: str
    detail: str
    confidence: float
    line: int | None = None


@dataclass
class Node:
    name: str
    type: NodeType
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5


@dataclass
class Edge:
    source: str
    target: str
    relation: str
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class PipelineInventory:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    schedules: dict[str, str] = field(default_factory=dict)
    volume_hints: dict[str, str] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)

    def add_node(self, name: str, type: NodeType, evidence: Evidence | None = None, **metadata: Any) -> Node:
        node = self.nodes.get(name)
        if node is None:
            node = Node(name=name, type=type, metadata=metadata)
            self.nodes[name] = node
        else:
            if node.type == "unknown" and type != "unknown":
                node.type = type
            node.metadata.update(metadata)
        if evidence:
            node.evidence.append(evidence)
            node.confidence = max(node.confidence, evidence.confidence)
        return node

    def add_edge(self, source: str, target: str, relation: str, evidence: Evidence | None = None, confidence: float = 0.5) -> None:
        if source == target:
            return
        for edge in self.edges:
            if edge.source == source and edge.target == target and edge.relation == relation:
                if evidence:
                    edge.evidence.append(evidence)
                edge.confidence = max(edge.confidence, confidence)
                return
        self.edges.append(Edge(source=source, target=target, relation=relation, evidence=[evidence] if evidence else [], confidence=confidence))

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {name: asdict(node) for name, node in sorted(self.nodes.items())},
            "edges": [asdict(edge) for edge in self.edges],
            "schedules": self.schedules,
            "volume_hints": self.volume_hints,
            "gaps": self.gaps,
        }


def relpath(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)
