# Lineage Gap Review Prompt v1

Review the proposed lineage map and gap report.

Focus on:
- Missing source-to-sink edges
- Ambiguous column expressions
- UDFs/macros/procedures that need manual review
- Dynamic SQL or runtime table names
- Dead-code candidates
- Broken dependency references

Return JSON with `accepted`, `rejected`, and `needs_human_review` lists.
