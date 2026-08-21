from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.pipeline import (
    run_postgres_ingestion,
    run_weather_ingestion,
    run_marketing_csv_ingestion,
)


with DAG(
    dag_id="ecommerce_ingestion",
    start_date=datetime(2026, 8, 14),
    schedule=None,
    catchup=False,
) as dag:

    postgres_ingestion = PythonOperator(
        task_id="postgres_ingestion",
        python_callable=run_postgres_ingestion,
    )

    weather_ingestion = PythonOperator(
        task_id="weather_ingestion",
        python_callable=run_weather_ingestion,
    )
'''
    marketing_ingestion = PythonOperator(
        task_id="marketing_csv_ingestion",
        python_callable=run_marketing_csv_ingestion,
    )
    '''
