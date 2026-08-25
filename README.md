## Architecture

```mermaid
flowchart TB
    AIRFLOW[Airflow<br/>Orchestration]

    PG[(PostgreSQL)]
    S3[(S3 / CSV)]
    API[(Weather API)]

    PIPE["<div style='text-align: left'><b>Python Ingestion Pipeline</b> ---------------------------------<br/>• Incremental Loading<br/>• Watermarks<br/>• Idempotent MERGE<br/>• Retry Handling</div>"]

    BQ[(BigQuery<br/>Raw)]
    DBT[dbt]
    ANALYTICS[(Analytics)]
    TESTS["Testing<br/>• Unit Tests<br/>• Integration Tests"]

    AIRFLOW -. "Orchestrates" .-> PIPE

    PG --> PIPE
    S3 --> PIPE
    API --> PIPE

    PIPE --> BQ
    BQ --> DBT
    DBT --> ANALYTICS

    TESTS -. "Validates" .-> PIPE
