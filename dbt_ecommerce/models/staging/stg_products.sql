select
    product_id,
    product_name,
    category,
    unit_price,
    created_at,
    _ingested_at
from {{ source('raw', 'products') }}