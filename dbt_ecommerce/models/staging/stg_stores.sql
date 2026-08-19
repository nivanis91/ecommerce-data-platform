select
    store_id,
    store_name,
    city,
    country,
    opened_at,
    _ingested_at
from {{ source('raw', 'stores') }}