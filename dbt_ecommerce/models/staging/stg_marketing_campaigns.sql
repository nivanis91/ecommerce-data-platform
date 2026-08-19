select
    campaign_id,
    campaign_name,
    channel,
    city,
    start_date,
    end_date,
    budget,
    spend,
    _ingested_at
from {{ source('raw', 'marketing_campaigns') }}