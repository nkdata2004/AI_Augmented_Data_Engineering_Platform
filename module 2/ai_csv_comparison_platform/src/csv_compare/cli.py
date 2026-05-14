from __future__ import annotations

import argparse
from pathlib import Path

from .comparator import compare_csvs
from .reporting import write_html, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare two CSV files using fuzzy, heuristic, and embedding-based column matching.")
    parser.add_argument("--source", required=True, help="Path to source CSV")
    parser.add_argument("--target", required=True, help="Path to target CSV")
    parser.add_argument("--key-column", default=None, help="Optional source or target key column name")
    parser.add_argument("--threshold", type=float, default=0.40, help="Minimum confidence for column mapping")
    parser.add_argument("--output-dir", default="reports", help="Directory where report.json and report.html are written")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    report = compare_csvs(args.source, args.target, key_column=args.key_column, mapping_threshold=args.threshold)
    write_json(report, output_dir / "report.json")
    write_html(report, output_dir / "report.html")
    print(f"Wrote {output_dir / 'report.json'}")
    print(f"Wrote {output_dir / 'report.html'}")
    print(f"Overall confidence: {report['overall_confidence']}")


if __name__ == "__main__":
    main()
