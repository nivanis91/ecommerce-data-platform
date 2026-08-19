select
    order_id,
    customer_id,
    store_id,
    order_date,
    status,
    updated_at,
    _ingested_at
from {{ source('raw', 'orders') }}