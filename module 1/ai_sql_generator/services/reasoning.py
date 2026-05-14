import re
import sqlglot
from sqlglot import exp


SQL_BUILTIN_FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "DATE",
    "COALESCE", "NULLIF", "ROUND", "CAST", "EXTRACT"
}


def build_reasoning_trace(sql: str, question: str, schema: dict, udfs: dict) -> dict:
    used_tables = sorted(set(re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)))

    known_udfs = {
        item["name"].upper()
        for item in udfs.get("udfs", [])
    }

    tree = sqlglot.parse_one(sql)

    function_calls = set()

    for node in tree.find_all(exp.Func):
        name = node.sql_name()

        if name == "ANONYMOUS":
            name = node.name

        if name:
            function_calls.add(name.upper())

    
    used_udfs = sorted(
    fn for fn in function_calls
    if fn in known_udfs
       and fn not in SQL_BUILTIN_FUNCTIONS
) 

    assumptions = []

    if "last quarter" in question.lower():
        assumptions.append("For the demo, 'last quarter' is mapped to Q1 2026 dates.")

    if used_udfs:
        assumptions.append("A matching UDF was preferred over inline revenue aggregation.")

    return {
        "question": question,
        "tables_used": used_tables,
        "udfs_used": used_udfs,
        "best_practice_intent": [
            "explicit column projection",
            "CTE for readability",
            "qualified aliases",
            "filter or date logic pushed into UDF arguments",
        ],
        "assumptions": assumptions,
    }