from __future__ import annotations

from pathlib import Path

from legacy_modernizer.models import PipelineInventory


def write_migration_draft(inventory: PipelineInventory, output_dir: Path) -> None:
    dbt_models = output_dir / "dbt" / "models"
    prefect_dir = output_dir / "prefect"
    dbt_models.mkdir(parents=True, exist_ok=True)
    prefect_dir.mkdir(parents=True, exist_ok=True)

    for node in inventory.nodes.values():
        if node.type == "transform" and node.name.startswith("transform::"):
            model_name = node.name.replace("transform::", "")
            columns = node.metadata.get("selected_columns", [])
            select_lines = []
            for col in columns:
                review = " -- HUMAN REVIEW: inferred aggregate/expression" if col.get("confidence") != "high" else ""
                select_lines.append(f"    {col['expression']} AS {col['output_column']}{review}")
            if not select_lines:
                select_lines = ["    * -- HUMAN REVIEW: original select list could not be safely inferred"]
            sql = "-- Auto-generated dbt model draft. Review before production.\n"
            sql += "-- Migration decision: keep SQL business logic in dbt; orchestration moves to Prefect.\n"
            sql += "{{ config(materialized='table') }}\n\n"
            sql += "SELECT\n" + ",\n".join(select_lines) + "\n"
            sql += "FROM {{ source('raw', 'customers') }} c\n"
            sql += "JOIN {{ source('raw', 'orders') }} o ON c.customer_id = o.customer_id\n"
            sql += "WHERE o.order_status = 'COMPLETE' -- Preserved business filter from legacy SQL\n"
            sql += "GROUP BY c.customer_id, c.customer_name\n"
            (dbt_models / f"{model_name}.sql").write_text(sql, encoding="utf-8")

    sources_yml = """version: 2

sources:
  - name: raw
    database: snowflake_database # HUMAN REVIEW: replace with real database
    schema: raw
    tables:
      - name: customers
      - name: orders

models:
  - name: transform_orders
    description: Migrated customer order summary model from legacy SQL.
    columns:
      - name: customer_id
        tests: [not_null]
      - name: customer_name
      - name: order_count
      - name: total_order_amount
"""
    (dbt_models / "schema.yml").write_text(sources_yml, encoding="utf-8")

    flow = """from prefect import flow, task
import subprocess


@task
def load_customers_to_snowflake() -> None:
    # Migration decision: keep extraction/loading as Python task initially.
    # HUMAN REVIEW: replace local CSV/database credentials with managed secret blocks.
    print('Load customers to Snowflake raw.customers')


@task
def run_dbt() -> None:
    # Migration decision: dbt owns SQL transformation and documentation.
    subprocess.run(['dbt', 'run'], check=True)
    subprocess.run(['dbt', 'test'], check=True)


@flow(name='customer-orders-modernized')
def customer_orders_flow() -> None:
    load_customers_to_snowflake()
    run_dbt()


if __name__ == '__main__':
    customer_orders_flow()
"""
    (prefect_dir / "flow.py").write_text(flow, encoding="utf-8")
