{% snapshot customers_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    created_at,
    updated_at

FROM {{ ref('stg_customers') }}

{% endsnapshot %}