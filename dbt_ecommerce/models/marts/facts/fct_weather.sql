{{
    config(
        materialized='table'
    )
}}

SELECT
    location,
    timestamp,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m

FROM {{ ref('stg_weather') }}