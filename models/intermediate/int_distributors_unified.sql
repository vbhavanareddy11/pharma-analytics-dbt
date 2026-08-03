{{
    config(
        materialized='view'
    )
}}

/*
  int_distributors_unified
  ------------------------
  Combines SAP.DISTRIBUTOR (supply-chain view) with SALESFORCE.ACCOUNT
  (commercial view) into a single distributor record.

  Handles real-world integration quirk: SAP and Salesforce sometimes
  have slightly different names for the same entity (casing, abbreviations).
  We flag the mismatch and prefer the Salesforce name (customer-facing).

  Grain: one row per distributor (distributor_id from SAP).
*/

with sap_distributor as (

    select
        distributor_id,
        sap_vendor_code,
        salesforce_account_id,
        distributor_name         as sap_distributor_name,
        country                  as sap_country,
        warehouse_location,
        warehouse_capacity_units,
        credit_limit,
        payment_terms_days,
        shipping_cost_per_order,
        regulatory_license_number,
        license_expiry_date,
        quality_certification,
        is_approved_vendor,
        contract_start_date,
        contract_end_date
    from {{ ref('stg_sap__distributor') }}

),

salesforce_account as (

    select
        account_id,
        account_name             as salesforce_distributor_name,
        account_type,
        tier,
        country                  as salesforce_country,
        zone,
        city,
        billing_address,
        primary_contact_name,
        primary_contact_email,
        primary_contact_phone,
        assigned_sales_rep_id,
        payment_terms            as salesforce_payment_terms,
        is_active                as is_active_salesforce
    from {{ ref('stg_salesforce__account') }}
    where is_distributor = true

),

joined as (

    select
        -- Keys
        sap.distributor_id,
        sap.sap_vendor_code,
        sap.salesforce_account_id,

        -- Names (both, plus mismatch flag)
        sap.sap_distributor_name,
        sf.salesforce_distributor_name,

        -- Prefer Salesforce name as canonical (customer-facing wins)
        coalesce(sf.salesforce_distributor_name, sap.sap_distributor_name) as distributor_name,

        -- Data quality flag: do the two source systems agree?
        case
            when sf.salesforce_distributor_name is null then 'missing_in_salesforce'
            when upper(sap.sap_distributor_name) = upper(sf.salesforce_distributor_name) then 'match'
            else 'mismatch'
        end as name_reconciliation_status,

        -- Location (prefer Salesforce for city detail; SAP for warehouse ops)
        coalesce(sf.salesforce_country, sap.sap_country) as country,
        sf.zone,
        sf.city,
        sf.billing_address,
        sap.warehouse_location,
        sap.warehouse_capacity_units,

        -- Commercial (Salesforce)
        sf.account_type,
        sf.tier,
        sf.primary_contact_name,
        sf.primary_contact_email,
        sf.primary_contact_phone,
        sf.assigned_sales_rep_id,

        -- Financial (SAP)
        sap.credit_limit,
        sap.payment_terms_days,
        sap.shipping_cost_per_order,

        -- Regulatory (SAP)
        sap.regulatory_license_number,
        sap.license_expiry_date,
        sap.quality_certification,
        sap.is_approved_vendor,

        -- Contract (SAP)
        sap.contract_start_date,
        sap.contract_end_date,

        -- Status
        sf.is_active_salesforce

    from sap_distributor sap
    left join salesforce_account sf
        on sap.salesforce_account_id = sf.account_id

)

select * from joined