{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(campaign_id AS STRING)) AS campaign_key,
    c.campaign_id,
    c.campaign_name,
    c.channel,

    l.location_key,

    c.start_date,
    c.end_date,
    c.budget,
    c.spend

FROM {{ ref('stg_marketing_campaigns') }} AS c

INNER JOIN {{ ref('dim_location') }} AS l
    ON c.city = l.city