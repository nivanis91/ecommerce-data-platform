SELECT *
FROM {{ ref('dim_campaigns') }}
WHERE end_date - start_date > INTERVAL 90 DAY