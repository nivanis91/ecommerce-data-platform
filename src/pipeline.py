import os
from src.config.connections import get_postgres_connection, get_s3_client
from src.ingestion.postgres import get_order_date_range, extract_orders, extract_customers, extract_stores, extract_order_items, extract_products
from src.ingestion.weather_api import get_weather
from src.ingestion.csv_import import list_files, load_csv
from src.config.cities import CITIES
from google.cloud import storage, bigquery
from decimal import Decimal

import pandas as pd

def load_dataframe_to_bigquery(df, table_id):
    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config,
    )
    
    job.result()

    print(f"Loaded {len(df)} rows into {table_id}")

from google.cloud import bigquery


def merge_dataframe_to_bigquery(df, table_id, merge_keys):
    client = bigquery.Client()

    temp_table_id = f"{table_id}_temp"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    job = client.load_table_from_dataframe(
        df,
        temp_table_id,
        job_config=job_config,
    )

    job.result()

    # 2. Get column name and prepare for query
    columns = df.columns.tolist()

    update_columns = [
        column for column in columns
        if column not in merge_keys
    ]

    merge_condition = " AND ".join(
        f"target.{key} = source.{key}"
        for key in merge_keys
    )
    
    update_set = ", ".join(
        f"target.{column} = source.{column}"
        for column in update_columns
    )

    insert_columns = ", ".join(columns)
    insert_values = ", ".join(
        f"source.{column}"
        for column in columns
    )

    # 3. MERGE temporary table into target
    merge_query = f"""
        MERGE `{table_id}` AS target
        USING `{temp_table_id}` AS source
        ON {merge_condition}

        WHEN MATCHED THEN
            UPDATE SET {update_set}

        WHEN NOT MATCHED THEN
            INSERT ({insert_columns})
            VALUES ({insert_values})
    """

    client.query(merge_query).result()

    # 4. Remove temporary table
    client.delete_table(temp_table_id, not_found_ok=True)

def run_weather_ingestion():

    conn = get_postgres_connection()

    try:
        dates = get_order_date_range(conn).iloc[0]
    finally:
        conn.close()

    start_date = dates["start_date"].strftime("%Y-%m-%d")
    end_date = dates["end_date"].strftime("%Y-%m-%d")

    dfs = []

    for city in CITIES:
        df = get_weather(
            city=city,
            start_date=start_date,
            end_date=end_date,
        )

        dfs.append(df)

    result = pd.concat(dfs, ignore_index=True)

    datetime_columns = result.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns

    for column in datetime_columns:
        result[column] = pd.to_datetime(
            result[column],
            utc=True
    )
            
    merge_dataframe_to_bigquery(result, "raw.weather", ['location', 'timestamp'])

    return result 

def clean_marketing_data_frame_before_db_upload(all_files_data_frame):
    df = all_files_data_frame.drop_duplicates(subset="campaign_id", keep="first")
    
    df["city"] = df["city"].replace({
        "Belgrad": "Belgrade"
    })

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce").dt.date

    df = df.dropna(subset=["spend"])

    df = df[df["spend"] >= 0]

    df = df[df["end_date"] >= df["start_date"]]

    df = df.dropna()

    # Strings
    df["campaign_name"] = df["campaign_name"].astype("string")
    df["channel"] = df["channel"].astype("string")
    df["city"] = df["city"].astype("string")

    # Numeric columns
    df["campaign_id"] = pd.to_numeric(df["campaign_id"], errors="coerce").astype("int64")
    df["budget"] = df["budget"].apply(lambda x: Decimal(str(x)))
    df["spend"] = df["spend"].apply(lambda x: Decimal(str(x)))

    return df

def run_marketing_csv_ingestion():
    s3 = get_s3_client()

    files = list_files(s3)

    files_array = []
    all_files_data_frame = pd.DataFrame()

    print("Files:")
    for file in files:
        print(file)
        loaded_csv = load_csv(
            s3,
            file
            )
        files_array.append(loaded_csv)

    all_files_data_frame = pd.concat(files_array)
    all_files_data_frame['budget'] = all_files_data_frame['budget'].astype(float)

    df = clean_marketing_data_frame_before_db_upload(all_files_data_frame)
   
    merge_dataframe_to_bigquery(df, 'raw.marketing_campaigns', ['campaign_id'])

def run_get_data_from_gcp():
    client = storage.Client()

    for bucket in client.list_buckets():
        print(bucket.name)

    bq = bigquery.Client()
    query = "SELECT * FROM `ecommerce.customers` LIMIT 10"

    results = bq.query(query).result()
    for row in results:
        print(row)


def ingest_table(extract_function, bq_table):
    conn = get_postgres_connection()

    try:
        df = extract_function(conn)
        
        load_dataframe_to_bigquery(df, bq_table)
    finally:
        conn.close()

def get_watermark(table_name):
    client = bigquery.Client()

    query = """
        SELECT watermark_value
        FROM `raw.pipeline_metadata`
        WHERE table_name = @table_name
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "table_name",
                "STRING",
                table_name
            )
        ]
    )

    result = client.query(
        query,
        job_config=job_config
    ).result()

    row = next(iter(result), None)

    if row is None:
        return None

    return row.watermark_value

def update_watermark(table_name, watermark_value):
    client = bigquery.Client()

    query = """
        MERGE `ecommerce-data-platform-505412.raw.pipeline_metadata` AS target

        USING (
            SELECT
                @table_name AS table_name,
                @watermark_value AS watermark_value,
                CURRENT_TIMESTAMP() AS completed_at
        ) AS source

        -- matching is done by table name, as we are using only record of the latest successfull run 
        ON target.table_name = source.table_name

        WHEN MATCHED THEN
            UPDATE SET
                target.watermark_value = source.watermark_value,
                target.completed_at = source.completed_at

        WHEN NOT MATCHED THEN
            INSERT (
                table_name,
                watermark_value,
                completed_at
            )
            VALUES (
                source.table_name,
                source.watermark_value,
                source.completed_at
            )
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "table_name",
                "STRING",
                table_name
            ),
            bigquery.ScalarQueryParameter(
                "watermark_value",
                "STRING",
                watermark_value
            ),
        ]
    )

    client.query(
        query,
        job_config=job_config
    ).result()

def ingest_table_idempotent(
        extract_function, 
        bq_table, 
        merge_keys,
        watermark_colum_name=None
    ):
    conn = get_postgres_connection()

    try:
        watermark = get_watermark(bq_table)
        print('Watermark value: ')
        print(watermark)
        df = extract_function(conn, watermark)

        datetime_columns = df.select_dtypes(
            include=["datetime", "datetimetz"]
        ).columns

        for column in datetime_columns:
            df[column] = pd.to_datetime(
                df[column],
                utc=True
        )

        merge_dataframe_to_bigquery(df, bq_table, merge_keys)

        print(f"\n{'=' * 60}")
        print(f"Table: {bq_table}")
        print(f"Watermark: {watermark}")
        print(f"Rows extracted: {len(df)}")
        print(f"\n{'=' * 60}")

        if len(df) > 0:
            new_watermark = df[watermark_colum_name].max()

            if watermark is None:
                update_watermark(
                    bq_table,
                    str(new_watermark)
                )
            else:
                watermark = type(new_watermark)(watermark)

                if new_watermark > watermark:
                    update_watermark(
                        bq_table,
                        str(new_watermark)
                    )

    finally:
        conn.close()

def run_postgres_ingestion():
    ingest_table_idempotent(extract_orders, "raw.orders", ['order_id'], "updated_at")
    ingest_table_idempotent(extract_customers, "raw.customers", ['customer_id'], "created_at")
    ingest_table_idempotent(extract_stores, "raw.stores", ['store_id'], "opened_at")
    #ingest_table_idempotent(extract_products, "raw.products", ['product_id'], "created_at")
    #ingest_table_idempotent(extract_order_items, "raw.order_items", ['order_item_id'], "order_item_id")
    
if __name__ == "__main__":
    #run_weather_ingestion()
    #run_marketing_csv_ingestion()
    run_postgres_ingestion()
    #run_get_data_from_gcp()

