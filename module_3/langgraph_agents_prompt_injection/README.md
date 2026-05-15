# Module 3 — Prompt Engineering & Agent Personas

This repository implements **Module 3** of the AI-Augmented Data Engineering Platform take-home exercise.

It demonstrates a **LangGraph-based multi-agent workflow** where three AI personas collaborate on a software development task:

1. **Developer Agent** generates a structured Jupyter Notebook.
2. **Tester Agent** extracts code from the notebook and generates pytest tests.
3. **Reviewer Agent** reviews the code and tests, then produces a gate verdict: `APPROVED` or `CHANGES_REQUESTED`.

The implementation is intentionally runnable without a paid LLM key by using a deterministic local mock model. The orchestration layer is written so a real LLM provider can be added later with minimal changes.

## 5-Minute Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m src.agent_platform.orchestrator --task "Create a function that normalizes messy customer names"
```

Generated artifacts are written to `outputs/`.


## Run tests

### Windows PowerShell

```powershell
python -m pytest
```

## VS Code Debugging

This project uses a package-based `src/` layout. For VS Code debugging, configure `.vscode/launch.json` to run the orchestrator as a module instead of running `orchestrator.py` directly.

Example:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Module 3 Orchestrator",
      "type": "debugpy",
      "request": "launch",
      "module": "src.agent_platform.orchestrator",
      "args": [
        "--task",
        "Build email validator"
      ],
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal"
    }
  ]
}



## Why LangGraph?


LangGraph is a good fit because this module is not just a linear script. It needs explicit state, controlled context passing, conditional routing when the reviewer requests changes, and future extensibility for retries or human approval.

```text
START -> Developer -> Tester -> Reviewer -> APPROVED -> END
                              ^             |
                              | CHANGES     |
                              +-------------+
```


## LangGraph Runtime Note

LangGraph is the primary orchestration framework used in this project. A lightweight `FallbackGraph` implementation is also included so the repository remains runnable in restricted or offline environments where LangGraph may not be available.

The fallback is intended only for demo resilience and local execution convenience; the intended orchestration architecture is based on LangGraph.


## Deliverables Mapping

| Requirement | Location |
|---|---|
| Prompt templates for all three agents | `prompts/v1/*.md` |
| Working orchestration script | `src/agent_platform/orchestrator.py` |
| LangGraph workflow | `build_graph()` in `orchestrator.py` |
| Example task demo | `examples/example_task.md` |
| Prompt design write-up | `docs/prompt_design_choices.md` |
| Architecture/design doc | `docs/architecture.md` |
| Tests for implemented module | `tests/` |

## Context Management Design

Each agent receives only what it needs:

- Developer receives the feature task and reviewer feedback if this is a revision.
- Tester receives extracted code cells, not the entire notebook conversation.
- Reviewer receives extracted code and the generated test file, not the full prompt history.

## LLM Provider Assumption

The demo uses a deterministic `MockLLMClient` so reviewers can run the project without credentials. In production, replace it with an adapter for OpenAI, Anthropic, Azure OpenAI, Ollama, or another backend.

## Limitations

- The local mock model is deterministic and does not perform true natural-language reasoning.
- Real LLM output should be validated more aggressively with schema validation and sandboxed code execution.
- Security review is limited to static checks and OWASP-inspired heuristics.


## Production Considerations

A production deployment would typically extend this prototype with:

- Retry/fallback handling for LLM failures
- Structured observability and trace logging
- Stronger schema validation
- Human-in-the-loop approval gates
- Tool permission boundaries
- Rate limiting and circuit breakers
- Advanced prompt-injection filtering and retrieval sanitization


## Prompt Injection Handling

This project treats feature descriptions as untrusted input. The Developer Agent wraps task text in an untrusted-data block, the validation layer detects common injection phrases, and the Reviewer Agent reports prompt-injection findings before final approval. See `docs/prompt_injection.md` for details.
