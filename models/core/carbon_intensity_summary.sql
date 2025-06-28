{{
  config(
    materialized='table'
  )
}}

with zone_summary as (
    select
        zone,
        count(*) as data_points,
        avg(carbon_intensity) as avg_carbon_intensity,
        min(carbon_intensity) as min_carbon_intensity,
        max(carbon_intensity) as max_carbon_intensity,
        avg(total_renewable_percentage) as avg_renewable_percentage,
        avg(fossil_fuel_percentage) as avg_fossil_percentage,
        count(case when carbon_intensity_category = 'low' then 1 end) as low_carbon_count,
        count(case when carbon_intensity_category = 'medium' then 1 end) as medium_carbon_count,
        count(case when carbon_intensity_category = 'high' then 1 end) as high_carbon_count,
        min(timestamp) as first_reading,
        max(timestamp) as last_reading
    from {{ ref('fact_carbon_intensity') }}
    group by zone
)

select
    zs.*,
    z.name as zone_name,
    z.country,
    z.latitude,
    z.longitude,
    z.timezone,
    -- Calculate percentages
    round((low_carbon_count * 100.0 / data_points), 2) as low_carbon_percentage,
    round((medium_carbon_count * 100.0 / data_points), 2) as medium_carbon_percentage,
    round((high_carbon_count * 100.0 / data_points), 2) as high_carbon_percentage
from zone_summary zs
left join {{ ref('dim_zones') }} z on zs.zone = z.zone 