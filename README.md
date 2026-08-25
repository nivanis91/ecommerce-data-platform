# E-commerce Data Platform

A production-style data engineering pipeline that ingests e-commerce and external data from multiple sources into BigQuery.

## Key Engineering Features

- **Incremental ingestion** using source-specific watermarks
- **Idempotent loading** using BigQuery `MERGE` operations
- **Retry handling** for transient PostgreSQL, BigQuery, and API failures
- **Data validation and cleaning** for incoming datasets
- **Unit and integration tests**
- **Airflow orchestration** for pipeline execution
- **Structured logging** for pipeline observability

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
