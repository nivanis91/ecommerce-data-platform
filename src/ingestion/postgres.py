import pandas as pd
from config.connections import get_postgres_connection
from decimal import Decimal


def get_order_date_range(conn):
    query = """
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date
        FROM orders
    """

    return pd.read_sql(query, conn)

def extract_stores(conn):
    query = """
        SELECT *
        FROM stores
    """

    return pd.read_sql(
        query,
        conn
    )

def extract_customers(conn):
    query = """
        SELECT *
        FROM customers
    """

    return pd.read_sql(
        query,
        conn
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

def extract_order_items(conn):
    query = """
        SELECT *
        FROM order_items
    """

    df = pd.read_sql(
        query,
        conn
    )

    df["unit_price"] = df["unit_price"].apply(
                lambda x: Decimal(str(x)) if x is not None else None
            )

    return df

def extract_products(conn):
    query = """
        SELECT *
        FROM products
    """
    
    df = pd.read_sql(
        query,
        conn
    )

    df["unit_price"] = df["unit_price"].apply(
                lambda x: Decimal(str(x)) if x is not None else None
            )

    return df

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