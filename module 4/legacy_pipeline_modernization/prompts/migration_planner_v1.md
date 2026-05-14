# Migration Planner Prompt v1

You are migrating a legacy data pipeline to a target platform.

Inputs:
- Current-state inventory
- Lineage map
- Gap report
- Target platform specification

Produce:
- Migration stages
- dbt model mapping
- orchestration mapping
- required tests
- human-review flags
- risks and mitigations

Rules:
- Preserve business logic.
- Do not hide uncertainty.
- Add inline comments explaining non-obvious migration choices.
- Flag any transformation that was inferred rather than proven.
