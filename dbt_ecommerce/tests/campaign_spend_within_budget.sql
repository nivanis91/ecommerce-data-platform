SELECT *
FROM {{ ref('dim_campaigns') }}
WHERE spend > budget