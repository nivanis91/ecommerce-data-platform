select
    location,
    timestamp,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    wind_speed_10m,
    _ingested_at
from {{ source('raw', 'weather') }}