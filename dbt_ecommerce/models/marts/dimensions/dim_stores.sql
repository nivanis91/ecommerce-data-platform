{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(store_id AS STRING)) AS store_key,
    store_id,
    store_name,
    city,
    country,
    opened_at

FROM {{ ref('stg_stores') }}