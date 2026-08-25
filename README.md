## Architecture

```mermaid
flowchart LR
    PG[(PostgreSQL)]
    S3[(S3 / CSV)]
    API[Weather API]

    PIPE["<div style='text-align: left'><b>Python Ingestion Pipeline</b> ---------------------------------<br/>• Incremental Loading<br/>• Watermarks<br/>• Idempotent MERGE<br/>• Retry Handling</div>"]

    BQ[(BigQuery<br/>Raw)]
    DBT[dbt]
    ANALYTICS[(Analytics)]
    AIRFLOW[Airflow]
   TESTS["Testing<br/>• Unit Tests<br/>• Integration Tests"]

    PG --> PIPE
    S3 --> PIPE
    API --> PIPE

    PIPE --> BQ
    BQ --> DBT
    DBT --> ANALYTICS

    AIRFLOW -. "Orchestrates" .-> PIPE
