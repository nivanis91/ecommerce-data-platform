import pandas as pd
from google.cloud import bigquery

from src.pipeline import merge_dataframe_to_bigquery


TEST_TABLE_NAME = "ecommerce-data-platform-505412.test.orders"


def test_merge_is_idempotent():
    client = bigquery.Client()

    df = pd.DataFrame({
        "order_id": [101, 102],
        "customer_id": [1, 2],
        "status": ["completed", "pending"]
    })

    # Start with a clean table
    client.delete_table(TEST_TABLE_NAME, not_found_ok=True)

    schema = [
        bigquery.SchemaField("order_id", "INT64"),
        bigquery.SchemaField("customer_id", "INT64"),
        bigquery.SchemaField("status", "STRING"),
    ]

    table = bigquery.Table(TEST_TABLE_NAME, schema=schema)
    client.create_table(table)

    try:
        # First ingestion
        merge_dataframe_to_bigquery(
            df,
            TEST_TABLE_NAME,
            ["order_id"]
        )

        # Same data again
        merge_dataframe_to_bigquery(
            df,
            TEST_TABLE_NAME,
            ["order_id"]
        )

        query = f"""
            SELECT
                order_id,
                COUNT(*) AS row_count
            FROM `{TEST_TABLE_NAME}`
            GROUP BY order_id
            HAVING COUNT(*) > 1
        """

        duplicates = list(client.query(query).result())

        assert duplicates == []

    finally:
        client.delete_table(TEST_TABLE_NAME, not_found_ok=True)

