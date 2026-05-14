# AI-Augmented Data Engineering Platform

## Focus module

This repository implements **Module 2 — Intelligent CSV Comparison Tool** from the take-home exercise.

It compares two CSV files and produces structured JSON and HTML diff reports. The system handles schema mismatch using:

- Levenshtein edit-distance similarity
- BGE embedding similarity using sentence-transformers
- Heuristic normalization for abbreviations, snake_case, camelCase, and common column-name variants

The implementation prioritizes depth and production-oriented design for Module 2, consistent with the exercise guidance to prioritize depth over breadth.

---

# 5-minute quickstart

## Create virtual environment

```bash
python -m venv .venv
```

## Activate environment

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.venv\Scripts\activate
```

## Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run the CSV comparison tool

```bash
csv-compare \
  --source examples/source_customers.csv \
  --target examples/target_customers.csv \
  --output-dir reports
```

---

# Expected outputs

The tool writes:

- `reports/report.json`
- `reports/report.html`

The HTML report is optimized for human review, while the JSON report preserves full comparison fidelity for downstream automation and auditing.

The JSON report includes:

- `column_mappings`: mapping table with confidence score from 0 to 1
- `key_mapping`: detected or user-specified key column
- `row_diffs.new_rows`
- `row_diffs.deleted_rows`
- `row_diffs.modified_rows`
- `summary.unmapped_source_columns`
- `summary.unmapped_target_columns`
- `overall_confidence`
- `confidence_breakdown`
- `human_review_flags`

---

## Embedding model

The column similarity module uses `BAAI/bge-small-en-v1.5` through `sentence-transformers`.

BGE is used to compute semantic similarity between normalized/enriched column names, while Levenshtein and heuristic rules provide additional explainable signals.

The first run may download the model from Hugging Face.

# Example CLI with user-specified key

```bash
csv-compare \
  --source examples/source_customers.csv \
  --target examples/target_customers.csv \
  --key-column cust_id \
  --output-dir reports
```

---

# VS Code debugging

This project uses a package-based `src/` layout with relative imports.

For VS Code debugging, configure `launch.json` to run:

```json
"module": "src.csv_compare.cli"
```

instead of running `cli.py` directly.

Example:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug CSV Comparator",
      "type": "python",
      "request": "launch",
      "module": "src.csv_compare.cli",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "args": [
        "--source",
        "examples/source_customers.csv",
        "--target",
        "examples/target_customers.csv",
        "--output-dir",
        "reports"
      ]
    }
  ]
}
```

---

# Run tests

```bash
python -m pytest
```

---

# Architecture and design notes

See:

- `docs/architecture.md`
- `docs/tradeoffs_and_limitations.md`
- `prompts/column_mapping_review_v1.md`

The pipeline is intentionally modular so that schema matching, row alignment, confidence scoring, and report generation can evolve independently.

---

# LLM and prompt management

No prompt is hardcoded in the implementation. The optional LLM review prompt is stored as a versioned prompt file under `prompts/`.

For the take-home demo, the system uses deterministic local scoring so it is testable and does not fail because of missing API keys.

In production, ambiguous mappings can be sent to an LLM using the versioned prompt and validated against a strict JSON output schema.

---

# Repository checklist coverage

- Working runnable demo for one module: yes, Module 2
- README with setup instructions and 5-minute quickstart: yes
- Structured JSON and HTML output: yes
- Column similarity mapping with edit distance, semantic scoring, and heuristics: yes
- Mapping confidence and overall confidence scoring: yes
- Low-confidence human-review flags: yes
- Tests: yes
- Versioned prompt files: yes
- Design docs and architecture notes: yes

---

# Main tradeoff

The implementation intentionally favors deterministic and explainable scoring over external LLM dependency for the core comparison flow.

This improves reproducibility, local testability, and debugging reliability for the take-home environment, while still leaving a clear extension path for production LLM-assisted review workflows.