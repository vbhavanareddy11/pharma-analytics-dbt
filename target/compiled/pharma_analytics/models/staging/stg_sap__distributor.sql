

with source as (

    select * from RAW.SAP.distributor

),

renamed as (

    select
        -- Keys
        distributor_id,
        sap_vendor_code,
        salesforce_account_id,           -- FK bridge to SALESFORCE.ACCOUNT

        -- Descriptive
        distributor_name,
        country,
        warehouse_location,

        -- Capacity + financials
        warehouse_capacity_units,
        credit_limit_usd     as credit_limit,
        payment_terms_days,
        shipping_cost_per_order_usd  as shipping_cost_per_order,

        -- Regulatory
        regulatory_license_number,
        license_expiry_date,
        quality_certification,
        is_approved_vendor,

        -- Contract lifecycle
        contract_start_date,
        contract_end_date,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from renamed