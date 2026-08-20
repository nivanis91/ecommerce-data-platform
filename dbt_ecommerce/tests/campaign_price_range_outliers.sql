{{ config(
    severity = 'warn',
    warn_if = '>0',
    error_if = '>50'
) }}

WITH stats AS (
    SELECT
        AVG(unit_price) AS avg_price,
        STDDEV(unit_price) AS stddev_price
    FROM {{ ref('dim_products') }}
    WHERE unit_price > 0
)

SELECT
    p.product_id,
    p.unit_price,
    s.avg_price,
    s.stddev_price,
    ROUND((p.unit_price - s.avg_price) / NULLIF(s.stddev_price, 0), 2) AS z_score,
    CASE
        WHEN (p.unit_price - s.avg_price) / NULLIF(s.stddev_price, 0) > 10 THEN 'EXTREME'
        WHEN (p.unit_price - s.avg_price) / NULLIF(s.stddev_price, 0) > 5  THEN 'SEVERE'
        WHEN (p.unit_price - s.avg_price) / NULLIF(s.stddev_price, 0) > 3  THEN 'MODERATE'
    END AS severity
FROM {{ ref('dim_products') }} p
CROSS JOIN stats s
WHERE (p.unit_price - s.avg_price) / NULLIF(s.stddev_price, 0) > 3   -- only high side
ORDER BY z_score DESC