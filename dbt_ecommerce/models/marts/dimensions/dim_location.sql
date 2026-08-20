{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(city) AS location_key,
    city,
    country,
    population,
    avg_income,
    latitude,
    longitude

FROM {{ ref('stg_locations') }}