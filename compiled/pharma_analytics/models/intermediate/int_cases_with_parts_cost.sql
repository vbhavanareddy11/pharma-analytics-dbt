

/*
  int_cases_with_parts_cost
  -------------------------
  Every service ticket enriched with:
    - Parts cost rolled up from case_part_usage
    - Engineer + travel cost using the assigned engineer's hourly rate
    - Total company cost per ticket
    - Revenue billed to customer (parts + labor charges) if out-of-warranty

  Grain: one row per case (case_id).
*/

with cases as (

    select
        case_id,
        case_number,
        account_id,
        device_serial_number,
        field_engineer_id,
        case_type,
        priority,
        status,
        resolution_code,
        ticket_channel,
        is_in_warranty,
        is_billable_to_customer,
        engineer_hours_logged,
        travel_hours_logged,
        opened_date,
        resolved_date,
        closed_date
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__case

),

engineers as (

    select
        user_id            as field_engineer_id,
        hourly_cost_rate
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__user
    where user_role = 'Field Engineer'

),

parts_rolled_up as (

    -- Aggregate parts consumed per case
    select
        case_id,
        count(*)                                       as parts_line_count,
        sum(quantity)                                  as total_parts_quantity,
        sum(quantity * unit_cost_at_use)               as parts_cost_total,
        sum(quantity * unit_price_charged)             as parts_revenue_total
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__case_part_usage
    group by case_id

),

joined as (

    select
        c.*,

        -- Engineer cost rate
        e.hourly_cost_rate,

        -- Parts economics (nullable if no parts consumed)
        coalesce(p.parts_line_count, 0)      as parts_line_count,
        coalesce(p.total_parts_quantity, 0)  as total_parts_quantity,
        coalesce(p.parts_cost_total, 0)      as parts_cost_total,
        coalesce(p.parts_revenue_total, 0)   as parts_revenue_total

    from cases c
    left join engineers e
        on c.field_engineer_id = e.field_engineer_id
    left join parts_rolled_up p
        on c.case_id = p.case_id

),

with_totals as (

    select
        *,

        -- Labor cost = (engineer + travel hours) × engineer's hourly rate
        (coalesce(engineer_hours_logged, 0) + coalesce(travel_hours_logged, 0))
            * coalesce(hourly_cost_rate, 0)      as labor_cost,

        -- Total cost the COMPANY absorbs on this ticket
        (
            (coalesce(engineer_hours_logged, 0) + coalesce(travel_hours_logged, 0))
                * coalesce(hourly_cost_rate, 0)
        )
        + coalesce(parts_cost_total, 0)          as total_company_cost,

        -- Revenue billed to customer (0 if in-warranty)
        case
            when is_billable_to_customer = true then coalesce(parts_revenue_total, 0)
            else 0
        end                                      as customer_revenue

    from joined

),

final as (

    select
        *,
        -- Net cost to the company: cost incurred minus revenue billed to customer
        total_company_cost - customer_revenue    as net_service_cost
    from with_totals

)

select * from final