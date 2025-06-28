{{
  config(
    materialized='table'
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
    created_at,
    -- Add calculated fields
    case 
        when carbon_intensity < {{ var('low_carbon_threshold') }} then 'low'
        when carbon_intensity < {{ var('high_carbon_threshold') }} then 'medium'
        else 'high'
    end as carbon_intensity_category,
    -- Calculate total renewable percentage
    coalesce(renewable_percentage, 0) + 
    coalesce(hydro_percentage, 0) + 
    coalesce(wind_percentage, 0) + 
    coalesce(solar_percentage, 0) + 
    coalesce(biomass_percentage, 0) as total_renewable_percentage
from {{ ref('stg_carbon_intensity') }} 