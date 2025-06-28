{{
  config(
    materialized='view'
  )
}}

select
    zone,
    name,
    country,
    latitude,
    longitude,
    timezone,
    created_at,
    updated_at
from {{ source('raw', 'zones') }}

-- Add data quality checks
where zone is not null
  and name is not null 