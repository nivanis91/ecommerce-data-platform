{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(store_id AS STRING)) AS store_key,
    s.store_id,
    s.store_name,

    l.location_key,

    s.opened_at

FROM {{ ref('stg_stores') }} AS s

LEFT JOIN {{ ref('dim_location') }} AS l
    ON s.city = l.city