select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    _ingested_at
from {{ source('raw', 'order_items') }}