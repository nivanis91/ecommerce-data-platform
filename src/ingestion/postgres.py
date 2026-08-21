import pandas as pd
from src.config.connections import get_postgres_connection
from decimal import Decimal
from datetime import datetime, timedelta


def get_order_date_range(conn):
    query = """
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date
        FROM orders
    """

    return pd.read_sql(query, conn)

def extract_stores(
        conn, 
        last_watermark=None
    ):

    if last_watermark is None:
            last_watermark = datetime.now() - timedelta(days=365 * 100)

    query = """
        SELECT *
        FROM stores
        WHERE opened_at >= %(last_watermark)s
    """

    return pd.read_sql(
        query,
        conn,
        params={
            "last_watermark": last_watermark
        }
    )

def extract_customers(
        conn, 
        last_watermark=None
    ):

    if last_watermark is None:
            last_watermark = datetime.now() - timedelta(days=365 * 100)
    
    query = """
        SELECT *
        FROM customers
        WHERE created_at >= %(last_watermark)s
    """

    return pd.read_sql(
        query,
        conn,
        params={
            "last_watermark": last_watermark
        }
    )


def extract_orders(
        conn, 
        last_watermark=None
    ):

    if last_watermark is None:
        last_watermark = datetime.now() - timedelta(days=365 * 100)

    query = """
        SELECT *
        FROM orders
        WHERE updated_at >= %(last_watermark)s
    """

    return pd.read_sql(
        query,
        conn,
        params={
            "last_watermark": last_watermark
        }
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

def extract_products(
        conn, 
        last_watermark=None
    ):

    if last_watermark is None:
            last_watermark = datetime.now() - timedelta(days=365 * 100)

    query = """
        SELECT *
        FROM products
        WHERE created_at >= %(last_watermark)s
    """
    
    df = pd.read_sql(
        query,
        conn,
        params={
            "last_watermark": last_watermark
        }
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