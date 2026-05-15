from __future__ import annotations

import argparse
import json
from pathlib import Path

from legacy_modernizer.analyzers.project_analyzer import analyze_project
from legacy_modernizer.confidence import score_inventory
from legacy_modernizer.lineage import build_lineage
from legacy_modernizer.migration.dbt_prefect import write_migration_draft
from legacy_modernizer.renderers.mermaid import render_data_flow
from legacy_modernizer.renderers.reports import render_gap_report, render_migration_plan


def run_analyze(input_dir: Path, output_dir: Path, target: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = analyze_project(input_dir)
    lineage = build_lineage(inventory)
    confidence = score_inventory(inventory)

    (output_dir / "inventory.json").write_text(json.dumps(inventory.to_dict(), indent=2), encoding="utf-8")
    (output_dir / "lineage.json").write_text(json.dumps(lineage, indent=2), encoding="utf-8")
    (output_dir / "confidence_report.json").write_text(json.dumps(confidence, indent=2), encoding="utf-8")
    (output_dir / "data_flow.mmd").write_text(render_data_flow(inventory), encoding="utf-8")
    (output_dir / "gap_report.md").write_text(render_gap_report(inventory), encoding="utf-8")
    (output_dir / "migration_plan.md").write_text(render_migration_plan(target, confidence), encoding="utf-8")
    write_migration_draft(inventory, output_dir / "migrated")
    print(f"Analysis complete. Artifacts written to: {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze and modernize legacy data pipeline artifacts")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a legacy pipeline folder")
    analyze.add_argument("--input", required=True, type=Path, help="Input folder containing legacy artifacts")
    analyze.add_argument("--output", required=True, type=Path, help="Output folder for generated artifacts")
    analyze.add_argument("--target", required=True, help="Target platform specification")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "analyze":
        run_analyze(args.input, args.output, args.target)


if __name__ == "__main__":
    main()
