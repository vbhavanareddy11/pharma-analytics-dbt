{{ config(materialized='view') }}

with source as (

    select * from {{ source('sap', 'spare_parts') }}

),

renamed as (

    select
        -- Keys
        part_id,
        part_code,

        -- Descriptive
        part_name,
        part_category,
        compatible_product_line,

        -- Economics
        unit_cost_usd    as unit_cost,
        unit_price_usd   as unit_price,

        -- Lifecycle
        is_active,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from renamed