

/*
  dim_distributor
  ---------------
  Distributor dimension — SAP supply-chain view unified with the
  Salesforce commercial view.
  Grain: one row per distributor.
*/

with source as (

    select * from ANALYTICS.DBT_BHAVANA.int_distributors_unified

),

final as (

    select
        -- Surrogate key
        md5(distributor_id::varchar)  as distributor_sk,

        -- Natural keys
        distributor_id                as distributor_nk,
        sap_vendor_code,
        salesforce_account_id,

        -- Descriptive
        distributor_name,
        account_type,
        tier,

        -- Data quality
        name_reconciliation_status,

        -- Geography
        country,
        zone,
        city,
        billing_address,
        warehouse_location,
        warehouse_capacity_units,

        -- Contacts
        primary_contact_name,
        primary_contact_email,
        primary_contact_phone,
        assigned_sales_rep_id,

        -- Financial
        credit_limit,
        payment_terms_days,
        shipping_cost_per_order,

        -- Regulatory
        regulatory_license_number,
        license_expiry_date,
        quality_certification,
        is_approved_vendor,

        -- Contract
        contract_start_date,
        contract_end_date,

        -- Status
        is_active_salesforce          as is_active

    from source

)

select * from final