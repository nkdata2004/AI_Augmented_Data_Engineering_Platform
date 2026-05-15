# AI-Augmented Legacy Data Pipeline Modernization System

This repository is a proof-of-concept for **Module 4 — Legacy Data Pipeline Modernization System** from the AI-Augmented Data Engineering Platform take-home exercise.

It analyzes legacy pipeline artifacts such as SQL scripts, Python ETL files, YAML configs, and DAG definitions, then generates modernization artifacts:

- Current-state inventory of sources, transformations, sinks, dependencies, schedules, and inferred data volume hints
- Mermaid data-flow diagram
- Column-level lineage map where inferable
- Gap report for missing docs, ambiguous lineage, broken dependencies, and dead-code indicators
- Confidence scores at artifact and node level
- dbt + Prefect migration draft with inline comments and human-review flags

The implementation intentionally uses deterministic static analysis first and reserves LLM usage for ambiguous interpretation. This keeps the demo runnable without paid APIs while showing where prompts and validation would plug in for production.

## 5-minute quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python -m legacy_modernizer.cli analyze \
  --input examples/legacy_pipeline \
  --target "Migrate from Airflow + raw SQL to dbt + Prefect on Snowflake" \
  --output outputs/demo

```

Open the generated files in `outputs/demo/`:

```text
inventory.json
lineage.json
data_flow.mmd
gap_report.md
confidence_report.json
migration_plan.md
migrated/dbt/models/*.sql
migrated/prefect/flow.py
```


## VS Code debugging

This project uses a package-based layout. For VS Code debugging, configure `.vscode/launch.json` to run the CLI as a module instead of running `cli.py` directly.

Example:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Legacy Pipeline Modernizer",
      "type": "debugpy",
      "request": "launch",
      "module": "legacy_modernizer.cli",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "args": [
        "analyze",
        "--input",
        "examples/legacy_pipeline",
        "--target",
        "Migrate from Airflow + raw SQL to dbt + Prefect on Snowflake",
        "--output",
        "outputs/demo"
      ]
    }
  ]
}
```

# Run tests

```bash
python -m pytest
```


## Repository layout

```text
legacy_pipeline_modernization/
├── docs/
│   ├── architecture.md
│   └── process_flow.mmd
├── examples/legacy_pipeline/
│   ├── dags/customer_orders_dag.py
│   ├── etl/load_customers.py
│   ├── sql/transform_orders.sql
│   └── configs/pipeline.yaml
├── prompts/
│   ├── current_state_interpretation_v1.md
│   ├── migration_planner_v1.md
│   └── lineage_gap_review_v1.md
├── src/legacy_modernizer/
│   ├── analyzers/
│   ├── renderers/
│   ├── migration/
│   ├── models.py
│   └── cli.py
└── tests/
```

## Design choices

| Layer | Choice for this POC | Why |
|---|---|---|
| LLM Orchestration | Lightweight prompt runner abstraction; production option: LangChain or LlamaIndex | Avoids API dependency in demo; prompts are versioned and output is validated before use |
| Code Parsing | `ast` for Python, `sqlglot` for SQL with fallback regex, `PyYAML` for YAML | Deterministic, inspectable, testable; LLM is not the first parser |
| Lineage | Custom typed graph using dataclasses; production option: OpenLineage/Marquez or NetworkX | Simple enough for demo, easy to serialize and explain |
| Graph Rendering | Mermaid | GitHub renders Mermaid natively in Markdown and it is easy to review |
| Vector Store | Not required for demo; production option: Chroma for local POC, pgvector/Weaviate for scale | Useful for retrieving related code/docs into LLM context, not necessary for deterministic sample |
| Pipeline Runtime Target | dbt + Prefect on Snowflake | dbt owns transformations and documentation; Prefect owns orchestration |

## How the POC works

1. Walk the input folder and classify files by extension/path.
2. Parse SQL for tables, selected columns, aliases, inserts, joins, and transformations.
3. Parse Python ETL and DAG files using Python `ast` to infer imports, function calls, dependencies, and schedules.
4. Parse YAML configs for declared sources, sinks, schedules, owner, and volume hints.
5. Merge findings into a normalized inventory graph.
6. Infer lineage when source-to-target relationships are clear.
7. Generate artifacts and confidence scores.
8. Generate migration draft code for dbt models and a Prefect flow.

## Confidence scoring strategy

Confidence is computed from evidence, not from vibes:

- Strong evidence: explicit SQL `INSERT INTO`, `CREATE TABLE AS`, dbt-like `ref/source`, explicit config source/sink declarations
- Medium evidence: table names in SQL `FROM/JOIN`, Python function names such as `extract`, `transform`, `load`, Airflow operator references
- Weak evidence: naming conventions, comments, inferred dependencies from file names
- Penalties: wildcard selects, dynamic SQL, unresolved imports, missing schedules, undocumented transformations, lineage gaps

The artifact-level confidence is the average of relevant node and edge scores minus penalties for known gaps. In production, LLM-generated claims would require JSON-schema validation and must cite source spans before being accepted.

## Human-in-the-loop checkpoints

Human review is required before:

- Accepting low-confidence lineage edges
- Migrating dynamic SQL or wildcard transformations
- Confirming business definitions such as revenue/customer/order logic
- Deleting suspected dead code
- Deploying generated dbt/Prefect code
- Changing schedules, SLAs, or ownership metadata

## Simplifying assumptions

- The demo focuses on batch SQL/Python/YAML/Airflow-style artifacts.
- Runtime database metadata and actual data volumes are mocked or inferred from config comments.
- Column-level lineage is best-effort and explicitly marks unknowns.
- Generated migration code is a starting point, not production-ready without human review.
