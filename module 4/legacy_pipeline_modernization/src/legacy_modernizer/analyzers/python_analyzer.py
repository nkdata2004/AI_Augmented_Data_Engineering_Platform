from __future__ import annotations

import ast
from pathlib import Path

from legacy_modernizer.models import Evidence, PipelineInventory, relpath


class PythonVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: list[str] = []
        self.calls: list[str] = []
        self.string_literals: list[str] = []
        self.dependencies: list[tuple[str, str]] = []
        self.schedule: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        if name:
            self.calls.append(name)
        for kw in node.keywords:
            if kw.arg in {"schedule_interval", "schedule"} and isinstance(kw.value, ast.Constant):
                self.schedule = str(kw.value.value)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            self.string_literals.append(node.value)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        # Detect Airflow task dependency syntax: task_a >> task_b
        if isinstance(node.op, ast.RShift):
            left = expr_name(node.left)
            right = expr_name(node.right)
            if left and right:
                self.dependencies.append((left, right))
        self.generic_visit(node)


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def expr_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def analyze_python_file(path: Path, base: Path, inventory: PipelineInventory) -> None:
    short = relpath(path, base)
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        inventory.gaps.append(f"{short}: Python syntax error prevents full static analysis: {exc}")
        return
    visitor = PythonVisitor()
    visitor.visit(tree)

    if "dag" in path.parts or "DAG" in text or "schedule_interval" in text:
        node_type = "task"
        node_name = f"dag::{path.stem}"
        confidence = 0.88
    else:
        node_type = "transform"
        node_name = f"python::{path.stem}"
        confidence = 0.78
    inventory.add_node(node_name, node_type, Evidence(short, "Python artifact parsed with ast", confidence), functions=visitor.functions, calls=visitor.calls)

    if visitor.schedule:
        inventory.schedules[node_name] = visitor.schedule

    for fn in visitor.functions:
        fn_node = f"function::{fn}"
        inferred_type = "transform"
        inventory.add_node(fn_node, inferred_type, Evidence(short, "Python function definition", 0.72))
        inventory.add_edge(node_name, fn_node, "contains", Evidence(short, "Function defined in artifact", 0.72), 0.72)
        lower = fn.lower()
        if lower.startswith("extract"):
            inventory.add_node(fn_node, "source", Evidence(short, "Function name indicates extraction", 0.62))
        elif lower.startswith("load"):
            inventory.add_node(fn_node, "sink", Evidence(short, "Function name indicates loading", 0.62))

    for left, right in visitor.dependencies:
        inventory.add_node(f"task::{left}", "task", Evidence(short, "Airflow dependency task", 0.76))
        inventory.add_node(f"task::{right}", "task", Evidence(short, "Airflow dependency task", 0.76))
        inventory.add_edge(f"task::{left}", f"task::{right}", "runs_before", Evidence(short, "Airflow >> dependency", 0.82), 0.82)

    for literal in visitor.string_literals:
        if literal.endswith(".sql") or literal.endswith(".py"):
            inventory.add_edge(node_name, literal, "references_file", Evidence(short, f"String literal references {literal}", 0.68), 0.68)

    if any("format" in call or "execute" in call for call in visitor.calls) and "select" in text.lower():
        inventory.gaps.append(f"{short}: possible dynamic SQL requires human review")
