import pandas as pd
from config.connections import get_postgres_connection

def get_order_date_range(conn):
    query = """
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date
        FROM orders
    """

    return pd.read_sql(query, conn)

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
    conn = get_postgres_connection
    try:
        orders = extract_orders(conn)

        print(f"Records extracted: {len(orders)}")
        print(orders.head())

    finally:
        conn.close()

if __name__ == "__main__":
    main()