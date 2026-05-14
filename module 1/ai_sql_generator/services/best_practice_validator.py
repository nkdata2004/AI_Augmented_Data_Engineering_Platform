import re
from dataclasses import dataclass, field


@dataclass
class BestPracticeResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_best_practices(sql: str) -> BestPracticeResult:
    errors: list[str] = []
    warnings: list[str] = []
    upper_sql = sql.upper()

    if re.search(r"SELECT\s+\*", upper_sql):
        errors.append("Avoid SELECT *; project explicit columns.")

    if "CROSS JOIN" in upper_sql:
        errors.append("Potential Cartesian join detected via CROSS JOIN.")

    if " JOIN " in upper_sql and " ON " not in upper_sql and " USING " not in upper_sql:
        warnings.append("JOIN detected without obvious ON/USING condition.")

    if "WITH " not in upper_sql and "SELECT" in upper_sql:
        warnings.append("Consider using CTEs for complex queries.")

    return BestPracticeResult(passed=not errors, errors=errors, warnings=warnings)
