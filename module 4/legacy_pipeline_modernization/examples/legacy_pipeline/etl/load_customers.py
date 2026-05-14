import pandas as pd
from sqlalchemy import create_engine


def extract_customers(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"id": "customer_id", "name": "customer_name"})
    df["customer_name"] = df["customer_name"].str.strip()
    return df


def load_customers(df: pd.DataFrame, connection_string: str) -> None:
    engine = create_engine(connection_string)
    df.to_sql("customers", engine, schema="raw", if_exists="append", index=False)
