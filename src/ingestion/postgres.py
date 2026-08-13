import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )

def extract_orders(conn):
    query = """
        SELECT *
        FROM orders
    """

    return pd.read_sql(
        query,
        conn
    )


def main():
    conn = get_connection()

    try:
        orders = extract_orders(conn)

        print(f"Records extracted: {len(orders)}")
        print(orders.head())

    finally:
        conn.close()

if __name__ == "__main__":
    main()