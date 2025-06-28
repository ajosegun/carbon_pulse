{{
  config(
    materialized='view'
  )
}}

select
    id,
    zone,
    timestamp,
    carbon_intensity,
    fossil_fuel_percentage,
    renewable_percentage,
    nuclear_percentage,
    hydro_percentage,
    wind_percentage,
    solar_percentage,
    biomass_percentage,
    coal_percentage,
    gas_percentage,
    oil_percentage,
    unknown_percentage,
    total_production,
    total_consumption,
    created_at
from {{ source('raw', 'carbon_intensity') }}

-- Add data quality checks
where carbon_intensity is not null
  and carbon_intensity >= 0
  and timestamp is not null 