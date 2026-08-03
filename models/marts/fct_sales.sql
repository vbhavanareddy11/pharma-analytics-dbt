{{
    config(
        materialized='incremental',
        unique_key='sale_sk',
        on_schema_change='append_new_columns'
    )
}}

/*
  fct_sales
  ---------
  Sales fact — one row per device sold.
  Materialization: incremental — new sales append based on updated_at watermark.

  Grain: one row per sale (opportunity_id / device_serial_number).

  Design notes:
    - Incremental keyed on 'sale_sk' with a watermark on 'source_updated_at'
    - On first run: full historical load (100K rows)
    - On subsequent runs: only pulls opportunities with source_updated_at > max(source_updated_at) in target
    - unique_key ensures dedup if the same row shows up in both old and new batches
*/

with source_sales as (

    select
        opportunity_id,
        opportunity_number,
        account_id,
        sales_rep_id,
        material_id,
        device_serial_number,
        quantity,
        unit_sale_price,
        total_amount,
        discount_pct,
        stage,
        sale_date,
        warranty_start_date,
        warranty_end_date,
        hardware_install_date,
        software_install_date,
        payment_terms,
        created_at,
        updated_at
    from {{ ref('stg_salesforce__opportunity') }}

    {% if is_incremental() %}
        -- Only pull rows updated after the latest we've already loaded
        where updated_at > (select coalesce(max(source_updated_at), '1900-01-01'::timestamp) from {{ this }})
    {% endif %}

),

dims as (

    select
        product_sk,
        product_nk
    from {{ ref('dim_product') }}

),

customer_dim as (

    select
        customer_sk,
        customer_nk
    from {{ ref('dim_customer') }}

),

sales_rep_dim as (

    select
        sales_rep_sk,
        sales_rep_nk
    from {{ ref('dim_sales_rep') }}

),

final as (

    select
        -- Surrogate key for this fact row
        md5(s.opportunity_id)                              as sale_sk,

        -- Natural keys
        s.opportunity_id                                   as sale_nk,
        s.opportunity_number,
        s.device_serial_number,

        -- Foreign keys to dims
        p.product_sk,
        c.customer_sk,
        r.sales_rep_sk,
        s.sale_date                                        as date_sk,  -- dim_date PK is calendar_date

        -- Degenerate dimensions
        s.stage,
        s.payment_terms,

        -- Measures
        s.quantity,
        s.unit_sale_price,
        s.total_amount                                     as revenue,
        s.discount_pct,
        s.total_amount - (s.total_amount * s.discount_pct) as net_revenue,

        -- Dates for downstream logic
        s.sale_date,
        s.warranty_start_date,
        s.warranty_end_date,
        s.hardware_install_date,
        s.software_install_date,

        -- Provenance
        s.created_at         as source_created_at,
        s.updated_at         as source_updated_at,
        current_timestamp()  as dbt_loaded_at

    from source_sales s
    left join dims p         on s.material_id  = p.product_nk
    left join customer_dim c on s.account_id   = c.customer_nk
    left join sales_rep_dim r on s.sales_rep_id = r.sales_rep_nk

)

select * from final