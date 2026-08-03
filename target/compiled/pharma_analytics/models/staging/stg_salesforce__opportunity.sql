

with source as (

    select * from RAW.SALESFORCE.opportunity

),

renamed as (

    select
        -- Keys
        id                        as opportunity_id,
        opportunity_number,
        account_id,
        owner_id                  as sales_rep_id,
        material_id,
        device_serial_number,

        -- Descriptive
        name                      as opportunity_name,
        stage,

        -- Economics
        quantity,
        unit_sale_price_usd       as unit_sale_price,
        total_amount_usd          as total_amount,
        discount_pct,
        payment_terms,

        -- Dates
        close_date                as sale_date,
        hardware_install_date,
        software_install_date,
        warranty_start_date,
        warranty_end_date,

        -- Lifecycle
        is_deleted,

        -- Metadata
        created_date              as created_at,
        last_modified_date        as updated_at

    from source
    where is_deleted = false

)

select * from renamed