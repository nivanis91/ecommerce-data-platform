import os
from config.connections import get_postgres_connection, get_s3_client
from ingestion.postgres import get_order_date_range
from ingestion.weather_api import get_weather
from ingestion.csv_import import list_files, load_csv
from config.cities import CITIES


import pandas as pd


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
    print(result)

    return result 


def run_marketing_csv_ingestion():
    s3 = get_s3_client()

    files = list_files(s3)

    print("Files:")
    for file in files:
        print(file)
        df = load_csv(
            s3,
            file
            )
        print(df)    

if __name__ == "__main__":
    #run_weather_ingestion()
    run_marketing_csv_ingestion()