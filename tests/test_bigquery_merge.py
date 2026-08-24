import pandas as pd
from google.cloud import bigquery
import pytest
from src.pipeline import merge_dataframe_to_bigquery


TEST_TABLE_NAME = "ecommerce-data-platform-505412.test.orders"

pytestmark = pytest.mark.integration

def create_test_table(client):
    # Start with a clean table
    client.delete_table(TEST_TABLE_NAME, not_found_ok=True)

    schema = [
        bigquery.SchemaField("order_id", "INT64"),
        bigquery.SchemaField("customer_id", "INT64"),
        bigquery.SchemaField("status", "STRING"),
    ]

    table = bigquery.Table(TEST_TABLE_NAME, schema=schema)
    client.create_table(table)

def test_merge_is_idempotent():
    client = bigquery.Client()

    df = pd.DataFrame({
        "order_id": [101, 102],
        "customer_id": [1, 2],
        "status": ["completed", "pending"]
    })

    create_test_table(client)

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


def test_merge_with_update_and_insert():
    client = bigquery.Client()

    df = pd.DataFrame({
        "order_id": [101, 102],
        "customer_id": [1, 2],
        "status": ["completed", "pending"]
    })

    df_second = pd.DataFrame({
        "order_id": [102, 103],
        "customer_id": [2, 3],
        "status": ["completed", "on_delivery"]
    })

    create_test_table(client)

    try:
        # First ingestion
        merge_dataframe_to_bigquery(
            df,
            TEST_TABLE_NAME,
            ["order_id"]
        )

        # MERGE new data (UPDATE of an existing record + INSERT of a new record)
        merge_dataframe_to_bigquery(
            df_second,
            TEST_TABLE_NAME,
            ["order_id"]
        )

        query = f"""
            SELECT order_id, customer_id, status
            FROM `{TEST_TABLE_NAME}`
            ORDER BY order_id
        """

        orders_list = list(client.query(query).result())

        assert len(orders_list) == 3

        assert [tuple(row) for row in orders_list] == [
            (101, 1, 'completed'),
            (102, 2, 'completed'),
            (103, 3, 'on_delivery'),
        ]

    finally:
        client.delete_table(TEST_TABLE_NAME, not_found_ok=True)

