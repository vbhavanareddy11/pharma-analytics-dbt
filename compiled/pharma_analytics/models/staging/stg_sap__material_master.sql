

with source as (

    select * from RAW.SAP.material_master

),

renamed as (

    select
        -- Keys
        material_id,
        material_code,

        -- Descriptive attributes
        material_name,
        business_unit,
        therapy_area,
        product_family,
        product_line,
        disease_category,
        service_tier,

        -- Economics
        list_price_usd       as list_price,
        production_cost_usd  as production_cost,

        -- Warranty and install
        warranty_months,
        requires_hw_install,
        requires_sw_install,

        -- Lifecycle
        launch_date,
        is_active,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from renamed