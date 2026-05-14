from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Template

HTML_TEMPLATE = Template("""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>CSV Comparison Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #202124; }
    h1, h2 { margin-bottom: 8px; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 16px 0; }
    .low { color: #b00020; font-weight: bold; }
    table { border-collapse: collapse; width: 100%; margin-top: 8px; }
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 14px; }
    th { background: #f4f4f4; text-align: left; }
    code { background: #f5f5f5; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>CSV Comparison Report</h1>
  <div class="card">
    <h2>Summary</h2>
    <p><b>Overall confidence:</b> {{ report.overall_confidence }}</p>
    <p><b>Match rate:</b> {{ report.summary.match_rate }}</p>
    <p><b>New rows:</b> {{ report.summary.new_row_count }} | <b>Deleted rows:</b> {{ report.summary.deleted_row_count }} | <b>Modified rows:</b> {{ report.summary.modified_row_count }}</p>
    <p><b>Value mismatches:</b> {{ report.summary.value_mismatch_count }} | <b>Unmapped source columns:</b> {{ report.summary.unmapped_source_columns|length }} | <b>Unmapped target columns:</b> {{ report.summary.unmapped_target_columns|length }}</p>
  </div>

  <div class="card">
    <h2>Key Detection</h2>
    <p><code>{{ report.key_mapping.source_column }}</code> → <code>{{ report.key_mapping.target_column }}</code>, confidence {{ report.key_mapping.confidence }}, method {{ report.key_mapping.method }}</p>
  </div>

  <div class="card">
    <h2>Column Mapping</h2>
    <table>
      <tr><th>Source</th><th>Target</th><th>Confidence</th><th>Levenshtein</th><th>Embedding</th><th>Heuristic</th><th>Review</th></tr>
      {% for m in report.column_mappings %}
      <tr>
        <td>{{ m.source_column }}</td><td>{{ m.target_column }}</td><td>{{ m.confidence }}</td><td>{{ m.levenshtein }}</td><td>{{ m.embedding }}</td><td>{{ m.heuristic }}</td><td class="{{ 'low' if m.needs_review else '' }}">{{ m.needs_review }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <div class="card">
    <h2>Modified Rows</h2>
    <table>
      <tr><th>Key</th><th>Differences</th></tr>
      {% for r in report.row_diffs.modified_rows %}
      <tr><td>{{ r.key }}</td><td><pre>{{ r.differences | tojson(indent=2) }}</pre></td></tr>
      {% endfor %}
    </table>
  </div>

  <div class="card">
    <h2>New / Deleted Rows</h2>
    <p><b>New keys:</b> {{ report.row_diffs.new_rows }}</p>
    <p><b>Deleted keys:</b> {{ report.row_diffs.deleted_rows }}</p>
  </div>
</body>
</html>
""")


def write_json(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def write_html(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HTML_TEMPLATE.render(report=report), encoding="utf-8")
