import argparse
import json

from providers.mock_provider import MockProvider
from services.best_practice_validator import validate_best_practices
from services.catalog_loader import load_schema, load_udfs
from services.dry_run import dry_run
from services.prompt_builder import build_prompt
from services.reasoning import build_reasoning_trace
from services.semantic_validator import validate_semantics
from validators.syntax_validator import validate_syntax


def run(question: str) -> dict:
    schema = load_schema()
    udfs = load_udfs()
    prompt = build_prompt(question)
    provider = MockProvider()
    sql = provider.generate(prompt)

    syntax = validate_syntax(sql, schema.get("dialect", "postgres"))
    best_practice = validate_best_practices(sql)
    semantic = validate_semantics(sql, schema, udfs, schema.get("dialect", "postgres")) if syntax.passed else None
    dry_run_result = dry_run(sql, schema.get("dialect", "postgres")) if syntax.passed else None
    reasoning_trace = build_reasoning_trace(sql, question, schema, udfs) if syntax.passed else {}

    passed = (
        syntax.passed
        and best_practice.passed
        and semantic is not None
        and semantic.passed
        and dry_run_result is not None
        and dry_run_result.passed
    )

    return {
        "passed": passed,
        "generated_sql": sql,
        "syntax_validation": syntax.__dict__,
        "semantic_validation": semantic.__dict__ if semantic else None,
        "best_practice_validation": best_practice.__dict__,
        "dry_run": dry_run_result.__dict__ if dry_run_result else None,
        "reasoning_trace": reasoning_trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="UDF-aware SQL generator prototype")
    parser.add_argument(
        "--question",
        default="Show me the top 10 customers by revenue last quarter",
        help="Natural language question to convert to SQL.",
    )
    args = parser.parse_args()
    result = run(args.question)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
