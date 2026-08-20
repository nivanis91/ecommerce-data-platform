SELECT
    o.order_date
FROM {{ ref('fct_orders') }} o
INNER JOIN {{ ref('dim_customers') }} c
on o.customer_key = c.customer_key
WHERE c.created_at > o.order_date 