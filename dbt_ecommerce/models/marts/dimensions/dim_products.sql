{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(product_id AS STRING)) AS product_key,
    product_id,
    product_name,
    category,
    unit_price,
    created_at

FROM {{ ref('stg_products') }}