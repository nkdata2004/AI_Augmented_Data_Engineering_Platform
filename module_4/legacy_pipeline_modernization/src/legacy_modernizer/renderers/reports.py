from __future__ import annotations

from legacy_modernizer.models import PipelineInventory


def render_gap_report(inventory: PipelineInventory) -> str:
    lines = ["# Gap Report", ""]
    if not inventory.gaps:
        lines.append("No gaps detected by static analysis.")
        return "\n".join(lines) + "\n"
    lines.append("## Detected gaps")
    for gap in inventory.gaps:
        lines.append(f"- {gap}")
    lines.extend([
        "",
        "## Recommended human review",
        "- Validate low-confidence lineage edges before migration.",
        "- Confirm business definitions for aggregations and filters.",
        "- Confirm schedules, SLA, owner, and downstream consumers.",
        "- Do not delete suspected dead code until production logs/runtime metadata confirm it is unused.",
    ])
    return "\n".join(lines) + "\n"


def render_migration_plan(target_spec: str, confidence: dict) -> str:
    return f"""# Migration Plan

## Target specification

{target_spec}

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

Overall artifact confidence: **{confidence.get('artifact_confidence')}** — {confidence.get('interpretation')}

## Human review flags

- Any edge below 0.70 confidence.
- Any inferred column lineage from aggregate expressions.
- Any dynamic SQL or file references not fully resolved.
- Any business-critical filter such as status, date range, or customer eligibility.
"""
