

/*
  int_accounts_with_zone
  ----------------------
  Enriches Salesforce accounts with full zone hierarchy metadata
  (sub_zone → zone → country → region).

  Grain: one row per account.
*/

with accounts as (

    select
        account_id,
        parent_account_id,
        account_number,
        account_name,
        account_type,
        tier,
        country     as account_country,
        zone        as zone_code,
        city,
        billing_address,
        is_distributor,
        primary_contact_name,
        primary_contact_email,
        assigned_sales_rep_id,
        contract_start_date,
        payment_terms,
        is_active
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__account

),

zones as (

    select
        zone_code,
        sub_zone_name,
        zone_name,
        country      as zone_country,
        region
    from ANALYTICS.DBT_BHAVANA.zone_hierarchy

),

joined as (

    select
        a.account_id,
        a.parent_account_id,
        a.account_number,
        a.account_name,
        a.account_type,
        a.tier,
        a.is_distributor,

        -- Zone hierarchy (from the seed)
        a.zone_code,
        z.sub_zone_name,
        z.zone_name,
        z.region,

        -- Country: prefer the account's own country, fall back to zone's
        coalesce(a.account_country, z.zone_country) as country,

        -- Data quality flag
        case
            when z.zone_code is null then 'zone_not_found'
            when a.account_country != z.zone_country then 'country_zone_mismatch'
            else 'ok'
        end as geo_data_quality,

        -- Rest of account attributes
        a.city,
        a.billing_address,
        a.primary_contact_name,
        a.primary_contact_email,
        a.assigned_sales_rep_id,
        a.contract_start_date,
        a.payment_terms,
        a.is_active

    from accounts a
    left join zones z
        on a.zone_code = z.zone_code

)

select * from joined