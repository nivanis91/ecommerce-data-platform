{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(customer_id AS STRING)) AS customer_key,
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    created_at

FROM {{ ref('stg_customers') }}