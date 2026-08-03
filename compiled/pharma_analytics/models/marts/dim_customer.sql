

/*
  dim_customer
  ------------
  Customer dimension (hospitals, hospital chains, clinics + distributors
  that also purchase directly). Enriched with zone hierarchy context.
  Grain: one row per account.
*/

with source as (

    select * from ANALYTICS.DBT_BHAVANA.int_accounts_with_zone

),

final as (

    select
        -- Surrogate key
        md5(account_id)                    as customer_sk,

        -- Natural key
        account_id                         as customer_nk,
        account_number,

        -- Descriptive
        account_name                       as customer_name,
        account_type                       as customer_type,
        tier,
        is_distributor,

        -- Hierarchy — parent chain if any
        parent_account_id,

        -- Geography (from zone bridge)
        country,
        region,
        zone_code,
        zone_name,
        sub_zone_name,
        city,
        billing_address,

        -- Ownership
        assigned_sales_rep_id,
        primary_contact_name,
        primary_contact_email,

        -- Commercial
        contract_start_date,
        payment_terms,
        geo_data_quality,

        -- Status
        is_active

    from source

)

select * from final