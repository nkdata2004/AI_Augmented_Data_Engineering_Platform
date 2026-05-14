# Architecture — Module 3 LangGraph Agent Workflow

## Goal

Implement a maintainable multi-agent workflow for software development tasks. The system turns a feature description into a notebook, tests the generated code, and reviews the result before a hypothetical commit.

## Components

```text
User Task
  |
  v
Developer Agent
  - Receives task and optional reviewer feedback
  - Produces structured notebook JSON
  - Writes notebook and importable module
  |
  v
Tester Agent
  - Receives extracted code cells only
  - Produces pytest file
  |
  v
Reviewer Agent
  - Receives code cells and tests only
  - Produces structured PASS/WARN/FAIL review
  - Emits APPROVED or CHANGES_REQUESTED
  |
  v
Conditional LangGraph Router
  - APPROVED -> END
  - CHANGES_REQUESTED -> Developer revision loop
```

## Context Isolation

The workflow intentionally avoids passing full conversation history between agents. This is important for security, cost, and output quality.

| Agent | Receives | Does Not Receive |
|---|---|---|
| Developer | Feature task, reviewer feedback | Tester hidden reasoning, full conversation |
| Tester | Extracted code cells | Original full chat, reviewer prompt |
| Reviewer | Code cells, test file | Full notebook markdown, full conversation |

## Reviewer Loop

Reviewer feedback is stored in `reviewer_feedback`. If the verdict is `CHANGES_REQUESTED`, the graph returns to the Developer Agent. A maximum revision count prevents infinite loops.

## Output Validation

The implementation validates notebooks using `nbformat.validate`. The reviewer performs simple static checks for expected functions, type hints, dangerous patterns, and test category coverage.

## Production Extensions

Recommended production extensions:

- Add provider adapters for Azure OpenAI, OpenAI, Anthropic, or Ollama.
- Validate LLM outputs with Pydantic models and JSON schema.
- Run generated code in a sandbox.
- Add Bandit or Semgrep for static security scanning.
- Add a human approval node before commit.
- Store agent traces and evaluation results for observability.
