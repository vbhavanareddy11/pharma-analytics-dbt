
  
    

create or replace transient table ANALYTICS.DBT_BHAVANA.fct_service_tickets
    
    
    
    as (

/*
  fct_service_tickets
  -------------------
  Service ticket fact — one row per ticket.

  Uses int_cases_with_parts_cost as source so parts economics
  (parts_cost_total, labor_cost, total_company_cost, customer_revenue,
   net_service_cost) are already computed.

  Grain: one row per ticket (case_id).
*/

with tickets as (

    select * from ANALYTICS.DBT_BHAVANA.int_cases_with_parts_cost

),

customer_dim as (
    select customer_sk, customer_nk from ANALYTICS.DBT_BHAVANA.dim_customer
),

engineer_dim as (
    select field_engineer_sk, field_engineer_nk from ANALYTICS.DBT_BHAVANA.dim_field_engineer
),

-- Look up product via device_serial → opportunity → material
device_to_product as (

    select
        s.device_serial_number,
        p.product_sk
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__opportunity s
    left join ANALYTICS.DBT_BHAVANA.dim_product p
        on s.material_id = p.product_nk

),

final as (

    select
        -- Surrogate key
        md5(t.case_id)                              as service_ticket_sk,

        -- Natural keys
        t.case_id                                   as service_ticket_nk,
        t.case_number,
        t.device_serial_number,

        -- Foreign keys
        c.customer_sk,
        e.field_engineer_sk,
        d.product_sk,
        t.opened_date                               as date_sk,  -- joins to dim_date.calendar_date

        -- Degenerate dims (attributes without their own dim)
        t.case_type,
        t.priority,
        t.status,
        t.resolution_code,
        t.ticket_channel,
        t.is_in_warranty,
        t.is_billable_to_customer,

        -- Measures — effort
        t.engineer_hours_logged,
        t.travel_hours_logged,
        (coalesce(t.engineer_hours_logged, 0) + coalesce(t.travel_hours_logged, 0)) as total_hours_logged,

        -- Measures — parts
        t.parts_line_count,
        t.total_parts_quantity,

        -- Measures — economics (pre-computed in intermediate)
        t.labor_cost,
        t.parts_cost_total,
        t.total_company_cost,
        t.customer_revenue,
        t.net_service_cost,

        -- Dates
        t.opened_date,
        t.resolved_date,
        t.closed_date,

        -- Resolution time (only if resolved)
        case
            when t.resolved_date is not null
                then datediff(hour, t.opened_date, t.resolved_date)
            else null
        end as resolution_hours,

        -- Provenance
        current_timestamp() as dbt_loaded_at

    from tickets t
    left join customer_dim c        on t.account_id            = c.customer_nk
    left join engineer_dim e        on t.field_engineer_id     = e.field_engineer_nk
    left join device_to_product d   on t.device_serial_number  = d.device_serial_number

)

select * from final
    )
;


  