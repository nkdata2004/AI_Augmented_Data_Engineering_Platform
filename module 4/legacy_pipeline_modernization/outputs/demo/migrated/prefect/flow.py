from prefect import flow, task
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
