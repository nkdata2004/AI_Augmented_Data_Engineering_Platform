# Migration Plan

## Target specification

Migrate from Airflow + raw SQL to dbt + Prefect on Snowflake

## Recommended target state

- Move SQL transformations into dbt models.
- Add dbt tests for not-null keys, uniqueness, accepted values, and relationship checks.
- Use Prefect to orchestrate extraction/loading and dbt execution.
- Store source freshness and ownership metadata in dbt YAML.
- Publish lineage and run metadata to OpenLineage/Marquez in production.

## Phased plan

1. **Inventory and validation**: review generated inventory, lineage, and gaps.
2. **Model migration**: convert raw SQL scripts into dbt models with source declarations.
3. **Orchestration migration**: replace Airflow DAG with Prefect flow calling extraction jobs and dbt commands.
4. **Testing**: add dbt tests, unit tests for Python transforms, and reconciliation checks against legacy outputs.
5. **Parallel run**: run legacy and modern pipelines side-by-side for several cycles.
6. **Cutover**: switch downstream consumers only after reconciliation passes.

## Confidence

Overall artifact confidence: **0.572** — Low: requires substantial human validation

## Human review flags

- Any edge below 0.70 confidence.
- Any inferred column lineage from aggregate expressions.
- Any dynamic SQL or file references not fully resolved.
- Any business-critical filter such as status, date range, or customer eligibility.
