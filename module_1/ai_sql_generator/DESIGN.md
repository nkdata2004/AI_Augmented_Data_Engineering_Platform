# DESIGN.md — Module 1: Intelligent SQL Generator

## Requirement Coverage

| Requirement | How this prototype addresses it |
|---|---|
| Accept natural-language query | `app.py` provides a CLI that accepts a user question. |
| Generate executable PostgreSQL SQL | The provider returns PostgreSQL-style SQL and syntax is validated with `sqlglot`. |
| UDF awareness | UDFs are loaded from `catalogs/udfs.yaml` and injected into the prompt context. |
| Prefer UDFs over inline logic | The prompt explicitly instructs the generator to prefer matching UDFs; the demo SQL uses `calculate_customer_revenue` instead of inline revenue aggregation. |
| UDF catalog ingestion | `catalog_loader.py` / prompt builder loads UDF definitions from YAML at runtime. |
| Accuracy | Layered validation: syntax validation, semantic validation, UDF validation, and best-practice validation. |
| Reusability | UDF catalog is externalized and can be updated without changing code. |
| Validation | Includes `sqlglot` syntax validation, schema/UDF checks, best-practice checks, and mock dry run / EXPLAIN. |
| Reasoning | Returns a structured reasoning trace with selected tables, UDFs, assumptions, and best-practice intent. |
| Data freshness | Prototype reloads YAML catalogs at runtime; production design would sync metadata from information schema or catalog services. |
| Avoid SELECT * | Best-practice validator rejects `SELECT *`. |
| Push filters early | Prompt rule enforces this; demo pushes date logic into UDF arguments. |
| Prefer CTEs | Prompt enforces CTE preference; demo SQL uses `WITH revenue_by_customer AS (...)`. |
| Flag Cartesian joins | Best-practice validator flags `CROSS JOIN` and joins without clear `ON` / `USING`. |
| Qualify aliases | Prompt requires aliases; demo SQL uses `c.customer_id`, `r.revenue`, etc. |
| Working prototype | `python app.py` runs an end-to-end CLI demo. |
| Prompt versioning | Prompt stored in `prompts/sql_generator.md`, not hardcoded. |
| Tests | Tests are included under `tests/`. |
| Mock dependencies allowed | LLM and dry run are mocked, as permitted by the assignment instructions. |


## Scope

This prototype implements Module 1 only. The goal is a working, maintainable, UDF-aware SQL generation pipeline, not a production SQL copilot.

## Architecture

```text
Natural-language query
  -> Prompt builder
  -> Schema + UDF catalog injection
  -> LLM provider interface (mocked for reproducibility)
  -> SQL syntax validation
  -> Semantic validation against schema/UDF catalog
  -> Best-practice validation
  -> Mock dry run / EXPLAIN
  -> Structured reasoning trace
```

## 1. Accuracy

Accuracy is handled through layered validation rather than trusting the LLM output directly.

- `sqlglot` validates SQL syntax.
- Semantic validation checks that referenced tables and qualified columns exist in the schema catalog.
- UDF validation checks that generated UDF calls exist in the UDF catalog.
- Best-practice validation rejects `SELECT *` and flags risky joins.

This is intentionally layered because LLMs can produce plausible but invalid SQL.

## 2. Reusability

UDFs are loaded from `catalogs/udfs.yaml`. Each UDF includes:

- name
- signature
- description
- example usage
- preferred intent keywords

The prompt builder injects the UDF catalog into the generation context. In production, this catalog would be populated from database metadata tables or an internal data catalog.

## 3. Validation

The prototype includes:

- syntax validation using `sqlglot`
- schema constraint checking
- UDF existence checking
- SQL best-practice checks
- mock dry run / EXPLAIN

The dry run is mocked because the assignment allows mocked external dependencies. In production, this would call `EXPLAIN` or a dry-run API on PostgreSQL, Snowflake, or BigQuery.

## 4. Reasoning

The system returns a structured reasoning trace, not raw hidden chain-of-thought. The trace includes:

- selected tables
- selected UDFs
- assumptions
- best-practice intent

This gives reviewers transparency without exposing unnecessary internal reasoning.

## 5. Data Freshness

For the prototype, catalogs are reloaded from YAML at runtime. This keeps the demo simple and reproducible.

A production version would use one of these strategies:

- scheduled metadata sync from database information schema
- CDC or catalog event updates for UDF/table changes
- versioned catalog snapshots with `last_synced_at`
- hash-based detection to avoid unnecessary re-indexing

## SQL Best Practices

The system enforces or flags:

- no `SELECT *`
- explicit projected columns
- CTEs for readability
- qualified aliases
- potential Cartesian joins
- UDF preference when UDF matches the intent

## Simplifying Assumptions

- The LLM provider is mocked for deterministic evaluation.
- The database dry run is mocked.
- The demo supports a small sample schema focused on customers and orders.
- Date interpretation for “last quarter” is hardcoded in the mock output for reproducibility.

These shortcuts are documented because the exercise prioritizes design, reasoning, and maintainable code over infrastructure setup.

## Live Extension Ideas

Likely extensions include:

- Replace `MockProvider` with Ollama/OpenAI/Anthropic.
- Add UDF ranking based on intent similarity.
- Add support for multiple schemas.
- Replace mock dry run with a real PostgreSQL `EXPLAIN` call.
- Add stricter join graph validation.
