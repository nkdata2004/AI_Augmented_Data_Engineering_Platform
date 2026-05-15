from dataclasses import dataclass
import sqlglot


@dataclass
class ValidationResult:
    passed: bool
    message: str


def validate_syntax(sql: str, dialect: str = "postgres") -> ValidationResult:
    try:
        sqlglot.parse_one(sql, read=dialect)
        return ValidationResult(True, "SQL syntax is valid using sqlglot.")
    except Exception as exc:
        return ValidationResult(False, f"SQL syntax error: {exc}")