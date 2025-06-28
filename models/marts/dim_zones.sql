{{
  config(
    materialized='table'
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
from {{ ref('stg_zones') }} 