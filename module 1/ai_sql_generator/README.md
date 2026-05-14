# Module 1 — Intelligent SQL Generator

This is a focused, runnable prototype for the take-home exercise. It generates PostgreSQL SQL from a natural-language prompt while using a schema catalog and a UDF catalog.

The implementation uses a deterministic mock LLM provider so the demo is reproducible and does not require API keys. The provider interface can be replaced by OpenAI, Anthropic, Ollama, or another provider.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py --question "Show me the top 10 customers by revenue last quarter"
```


## Run tests

### Linux/macOS

```bash
PYTHONPATH=. pytest
```

### Windows (PowerShell)

```powershell
$env:PYTHONPATH="."
python -m pytest
```


## What the demo shows

- Natural-language question input
- UDF catalog ingestion from YAML
- Schema catalog ingestion from YAML
- UDF-aware SQL generation
- Syntax validation with `sqlglot`
- Basic semantic validation against schema and UDF catalogs
- SQL best-practice checks
- Mock dry run / EXPLAIN strategy
- Structured reasoning trace without exposing private chain-of-thought

## Design choice

External dependencies such as real databases and LLM APIs are mocked intentionally, as the exercise notes allow mocked dependencies and emphasize design over infrastructure setup.


## Production Considerations

A production deployment would typically extend this prototype with:

- Prompt injection and unsafe SQL detection
- Query allowlists / restricted SQL operations
- Role-based access control (RBAC)
- Query cost estimation and execution limits
- Observability and audit logging
- Human approval for high-risk queries
- Stronger schema and output validation