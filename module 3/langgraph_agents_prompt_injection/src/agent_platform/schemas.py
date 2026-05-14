"""Shared state and provider interfaces for the agent workflow."""

from __future__ import annotations

from typing import Protocol, TypedDict


class LLMClient(Protocol):
    """Small provider interface to keep agents decoupled from LLM vendors."""

    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""


class AgentState(TypedDict, total=False):
    """LangGraph state passed between agents."""

    task: str
    revision_count: int
    reviewer_feedback: str
    notebook_json: str
    extracted_code: str
    test_file: str
    review_report: str
    verdict: str
    output_dir: str
    prompt_injection_findings: list[str]
