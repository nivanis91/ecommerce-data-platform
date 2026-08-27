import pandas as pd
from src.config.connections import get_postgres_connection
from decimal import Decimal
from datetime import datetime, timedelta


def get_order_date_range(
          conn, 
          last_order_id
    ):
    query = """
        SELECT
            MIN(order_date) AS start_date,
            MAX(order_date) AS end_date,
            MAX(order_id) as max_id_for_range
        FROM orders
        WHERE order_id >= %(last_order_id)s
    """

    return pd.read_sql(
         query, 
         conn,
         params={
            "last_order_id": last_order_id
        }
        )

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
        WHERE updated_at >= %(last_watermark)s
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

def extract_orders_backfill(
    conn,
    start_date_inclusive,
    end_date_exclusive
):
    query = """
        SELECT *
        FROM orders
        WHERE updated_at >= %(start_date_inclusive)s AND
              updated_at <= %(end_date_exclusive)s
    """

    return pd.read_sql(
        query,
        conn,
        params={
            "start_date_inclusive": start_date_inclusive,
            "end_date_exclusive": end_date_exclusive,
        },
    )

def extract_order_items(
        conn, 
        last_watermark=None
    ):

    if last_watermark is None:
        last_watermark = 0
            
    query = """
        SELECT *
        FROM order_items
        WHERE order_item_id >= %(last_watermark)s
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
