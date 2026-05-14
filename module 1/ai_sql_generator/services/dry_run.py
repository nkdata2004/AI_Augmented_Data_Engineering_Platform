from dataclasses import dataclass


@dataclass
class DryRunResult:
    passed: bool
    message: str
    plan: str


def dry_run(sql: str, dialect: str = "postgres") -> DryRunResult:
    """Mock dry run. In production this would call EXPLAIN on the target database."""
    if not sql.strip().lower().startswith(("select", "with")):
        return DryRunResult(False, "Dry run failed: unsupported statement type.", "")
    return DryRunResult(
        passed=True,
        message="Dry run passed using mock EXPLAIN.",
        plan="MOCK EXPLAIN PLAN: scan catalog-backed tables, evaluate CTE, sort revenue DESC, apply LIMIT 10.",
    )
