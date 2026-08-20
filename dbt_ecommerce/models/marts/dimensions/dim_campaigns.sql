{{
    config(
        materialized='table'
    )
}}

SELECT
    FARM_FINGERPRINT(CAST(campaign_id AS STRING)) AS campaign_key,
    campaign_id,
    campaign_name,
    channel,
    city,
    start_date,
    end_date,
    budget,
    spend

FROM {{ ref('stg_marketing_campaigns') }}