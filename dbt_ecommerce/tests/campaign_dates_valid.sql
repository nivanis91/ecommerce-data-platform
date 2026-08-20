SELECT *
FROM {{ ref('dim_campaigns') }}
WHERE start_date > end_date