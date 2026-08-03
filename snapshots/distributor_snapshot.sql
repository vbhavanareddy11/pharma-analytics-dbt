{% snapshot distributor_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='distributor_id',
        strategy='check',
        check_cols=['tier', 'assigned_sales_rep_id', 'is_approved_vendor', 'credit_limit', 'payment_terms_days']
    )
}}

/*
  distributor_snapshot
  --------------------
  SCD Type 2 snapshot of distributor state.

  Tracks changes to:
    - tier (customer growth reclassification)
    - assigned_sales_rep_id (territory reassignments)
    - is_approved_vendor (regulatory status changes)
    - credit_limit (financial re-evaluations)
    - payment_terms_days (commercial contract updates)

  Strategy: 'check' — dbt detects changes by comparing tracked columns
  (as opposed to 'timestamp' strategy which relies on updated_at).

  First run: captures every row as its initial version.
  Subsequent runs: closes old row + inserts new row when any check_col changes.
*/

select
    distributor_id,
    sap_vendor_code,
    salesforce_account_id,
    distributor_name,
    account_type,
    tier,
    country,
    city,
    warehouse_location,
    assigned_sales_rep_id,
    credit_limit,
    payment_terms_days,
    is_approved_vendor,
    regulatory_license_number,
    license_expiry_date,
    contract_start_date,
    contract_end_date

from {{ ref('int_distributors_unified') }}

{% endsnapshot %}