{{
    config(
        materialized='table'
    )
}}

SELECT
    oi.order_item_id,
    oi.order_id,

    c.customer_key,
    p.product_key,
    s.store_key,
    d.date_key,

    o.order_date,
    o.status,

    oi.quantity,
    oi.unit_price,

    oi.quantity * oi.unit_price AS sales_amount

FROM {{ ref('stg_order_items') }} AS oi

INNER JOIN {{ ref('stg_orders') }} AS o
    ON oi.order_id = o.order_id

INNER JOIN {{ ref('dim_customers') }} AS c
    ON o.customer_id = c.customer_id

INNER JOIN {{ ref('dim_products') }} AS p
    ON oi.product_id = p.product_id

INNER JOIN {{ ref('dim_stores') }} AS s
    ON o.store_id = s.store_id

INNER JOIN {{ ref('dim_date') }} AS d
    ON DATE(o.order_date) = d.date_day