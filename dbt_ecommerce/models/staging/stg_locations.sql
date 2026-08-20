SELECT
    city,
    country,
    population,
    avg_income,
    latitude,
    longitude

FROM {{ source('raw', 'locations') }}