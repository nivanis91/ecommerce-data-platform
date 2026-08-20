{{
    config(
        materialized='table'
    )
}}

SELECT
    l.location_key,

    w.timestamp,
    w.temperature_2m,
    w.relative_humidity_2m,
    w.precipitation,
    w.wind_speed_10m

FROM {{ ref('stg_weather') }} AS w

INNER JOIN {{ ref('dim_location') }} AS l
    ON w.location = l.city