from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="customer_orders_daily",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 2 * * *",
    catchup=False,
) as dag:
    load_customers = BashOperator(
        task_id="load_customers",
        bash_command="python etl/load_customers.py"
    )

    transform_orders = BashOperator(
        task_id="transform_orders",
        bash_command="psql -f sql/transform_orders.sql"
    )

    load_customers >> transform_orders
