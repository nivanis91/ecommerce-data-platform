select
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    created_at,
    updated_at,
    _ingested_at
from {{ source('raw', 'customers') }}
