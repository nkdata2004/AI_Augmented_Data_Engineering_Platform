from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp


@dataclass
class SemanticResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


SQL_BUILTIN_FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "DATE",
    "COALESCE", "NULLIF", "ROUND", "CAST", "EXTRACT"
}


def extract_function_calls(sql: str, dialect: str = "postgres") -> set[str]:
    tree = sqlglot.parse_one(sql, read=dialect)
    functions = set()

    for node in tree.find_all(exp.Func):
        name = node.sql_name()
        if name == "ANONYMOUS":
            name = node.name
        if name:
            functions.add(name.upper())

    return functions


def extract_cte_names(tree: exp.Expression) -> set[str]:
    cte_names = set()

    for cte in tree.find_all(exp.CTE):
        if cte.alias:
            cte_names.add(cte.alias)

    return cte_names


def validate_semantics(
    sql: str,
    schema: dict,
    udfs: dict,
    dialect: str = "postgres",
) -> SemanticResult:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        tree = sqlglot.parse_one(sql, read=dialect)
    except Exception as exc:
        return SemanticResult(
            passed=False,
            errors=[f"Failed to parse SQL: {exc}"],
        )

    schema_tables = schema.get("tables", {})
    known_tables = set(schema_tables.keys())
    cte_names = extract_cte_names(tree)

    known_udfs = {
        item["name"].upper()
        for item in udfs.get("udfs", [])
    }

    # Build alias -> table map
    alias_to_table: dict[str, str] = {}

    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias_or_name

        if not table_name:
            continue

        # CTEs are valid virtual relations
        if table_name in cte_names:
            if alias:
                alias_to_table[alias] = table_name
            continue

        if table_name not in known_tables:
            errors.append(f"Unknown table: {table_name}")
            continue

        if alias:
            alias_to_table[alias] = table_name

    # Validate qualified columns like c.customer_id
    for column in tree.find_all(exp.Column):
        table_alias = column.table
        column_name = column.name

        if not table_alias:
            continue

        table_name = alias_to_table.get(table_alias)

        if not table_name:
            continue

        # Skip CTE column validation for prototype
        if table_name in cte_names:
            continue

        valid_columns = schema_tables.get(table_name, {}).get("columns", [])

        if column_name not in valid_columns:
            errors.append(f"Unknown column: {table_name}.{column_name}")

    # Validate functions
    function_calls = extract_function_calls(sql, dialect=dialect)

    unknown_functions = (
        function_calls
        - known_udfs
        - SQL_BUILTIN_FUNCTIONS
    )

    for fn in unknown_functions:
        warnings.append(
            f"Function '{fn}' is not listed in the UDF catalog or known SQL built-ins."
        )

    return SemanticResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
    )