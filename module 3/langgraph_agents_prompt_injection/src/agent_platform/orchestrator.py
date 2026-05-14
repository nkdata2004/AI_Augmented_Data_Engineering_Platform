"""LangGraph orchestration for Module 3.

Run:
    python -m src.agent_platform.orchestrator --task "Create a function that normalizes messy customer names"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

try:  # pragma: no cover - exercised when langgraph is installed
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover - fallback keeps the repo runnable offline
    END = "__end__"
    START = "__start__"
    StateGraph = None  # type: ignore[assignment]

from src.agent_platform.agents import (
    DeveloperAgent,
    MockLLMClient,
    ReviewerAgent,
    TesterAgent,
)
from src.agent_platform.schemas import AgentState

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts" / "v1"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
MAX_REVISIONS = 2


class FallbackGraph:
    """Minimal fallback with the same invoke shape as a compiled LangGraph."""

    def __init__(
        self,
        developer: Callable[[AgentState], AgentState],
        tester: Callable[[AgentState], AgentState],
        reviewer: Callable[[AgentState], AgentState],
    ) -> None:
        self.developer = developer
        self.tester = tester
        self.reviewer = reviewer

    def invoke(self, state: AgentState) -> AgentState:
        """Execute the workflow with a bounded reviewer loop."""
        while True:
            state = self.developer(state)
            state = self.tester(state)
            state = self.reviewer(state)
            if route_after_review(state) == END:
                return state
            state["revision_count"] = state.get("revision_count", 0) + 1


def route_after_review(state: AgentState) -> str:
    """Route to END or back to developer based on reviewer verdict."""
    if state.get("verdict") == "APPROVED":
        return END
    if state.get("revision_count", 0) >= MAX_REVISIONS:
        return END
    return "developer"


def increment_revision(state: AgentState) -> AgentState:
    """Increment revision count before returning to developer."""
    return {**state, "revision_count": state.get("revision_count", 0) + 1}


def build_graph() -> object:
    """Build and compile the LangGraph workflow."""
    llm = MockLLMClient()
    developer = DeveloperAgent(llm, PROMPT_DIR / "developer_agent.md")
    tester = TesterAgent(llm, PROMPT_DIR / "tester_agent.md")
    reviewer = ReviewerAgent(llm, PROMPT_DIR / "reviewer_agent.md")

    if StateGraph is None:
        return FallbackGraph(developer.run, tester.run, reviewer.run)

    graph = StateGraph(AgentState)
    graph.add_node("developer", developer.run)
    graph.add_node("tester", tester.run)
    graph.add_node("reviewer", reviewer.run)
    graph.add_node("increment_revision", increment_revision)

    graph.add_edge(START, "developer")
    graph.add_edge("developer", "tester")
    graph.add_edge("tester", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {END: END, "developer": "increment_revision"},
    )
    graph.add_edge("increment_revision", "developer")
    return graph.compile()


def run_workflow(task: str, output_dir: Path = DEFAULT_OUTPUT_DIR) -> AgentState:
    """Run the end-to-end multi-agent workflow."""
    graph = build_graph()
    initial_state: AgentState = {
        "task": task,
        "revision_count": 0,
        "output_dir": str(output_dir),
    }
    final_state = graph.invoke(initial_state)  # type: ignore[attr-defined]

    summary = {
        "task": task,
        "verdict": final_state.get("verdict"),
        "revision_count": final_state.get("revision_count", 0),
        "artifacts": [
            "developer_notebook.ipynb",
            "generated_module.py",
            "test_generated_module.py",
            "review_report.md",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return final_state


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run Module 3 LangGraph agents.")
    parser.add_argument(
        "--task",
        default="Create a function that normalizes messy customer names",
        help="Feature description for the Developer Agent.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    final_state = run_workflow(args.task, Path(args.output_dir))
    print(final_state["review_report"])


if __name__ == "__main__":
    main()
