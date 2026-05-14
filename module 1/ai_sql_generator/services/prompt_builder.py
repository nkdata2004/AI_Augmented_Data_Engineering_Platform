from pathlib import Path

from services.catalog_loader import load_schema, load_udfs


BASE_DIR = Path(__file__).resolve().parents[1]


def build_prompt(question: str) -> str:
    prompt_template = (BASE_DIR / "prompts/sql_generator.md").read_text(encoding="utf-8")
    schema = load_schema()
    udfs = load_udfs()
    return f"""
{prompt_template}

Schema catalog:
{schema}

UDF catalog:
{udfs}

User question:
{question}
""".strip()
