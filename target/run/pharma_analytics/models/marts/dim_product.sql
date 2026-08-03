
  
    

create or replace transient table ANALYTICS.DBT_BHAVANA.dim_product
    
    
    
    as (

/*
  dim_product
  -----------
  Product dimension — the 4-level hierarchy plus economics, warranty,
  install requirements, and disease category for launch targeting joins.
  Grain: one row per product (material_id).
*/

with source as (

    select * from ANALYTICS.DBT_BHAVANA.stg_sap__material_master

),

final as (

    select
        -- Surrogate key
        md5(material_id::varchar)   as product_sk,

        -- Natural key (from SAP)
        material_id                 as product_nk,
        material_code               as product_code,

        -- Descriptive
        material_name               as product_name,

        -- Hierarchy (4 levels)
        business_unit,
        therapy_area,
        product_family,
        product_line,

        -- Analytical bridge
        disease_category,

        -- Economics
        list_price,
        production_cost,

        -- Warranty & install
        warranty_months,
        requires_hw_install,
        requires_sw_install,
        service_tier,

        -- Lifecycle
        launch_date,
        is_active,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from final
    )
;


  