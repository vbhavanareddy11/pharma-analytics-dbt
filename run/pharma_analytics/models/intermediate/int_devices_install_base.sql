
  create or replace   view ANALYTICS.DBT_BHAVANA.int_devices_install_base
  
  
  
  
  as (
    

/*
  int_devices_install_base
  ------------------------
  Every device ever sold, enriched with active-status and warranty flags.
  Grain: one row per device (device_serial_number).

  Domain rule (from real-world pharma commercial analytics):
    A device is "currently active" if it has received at least one service
    event in the last 18 months. Devices without recent service are
    considered dark — potentially retired, replaced, or churned.
*/

with sales as (

    select
        opportunity_id,
        account_id,
        sales_rep_id,
        material_id,
        device_serial_number,
        sale_date,
        warranty_start_date,
        warranty_end_date,
        hardware_install_date,
        software_install_date,
        total_amount as sale_amount
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__opportunity

),

products as (

    select
        material_id,
        product_line,
        product_family,
        therapy_area,
        business_unit,
        disease_category,
        warranty_months,
        requires_hw_install,
        requires_sw_install
    from ANALYTICS.DBT_BHAVANA.stg_sap__material_master

),

last_service_per_device as (

    -- Most recent service event per device (used for 18-month active rule)
    select
        device_serial_number,
        max(opened_date) as last_service_opened_at,
        count(*) as total_service_tickets_lifetime
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__case
    group by device_serial_number

),

joined as (

    select
        s.device_serial_number,
        s.opportunity_id,
        s.account_id,
        s.sales_rep_id,
        s.material_id,

        -- Product context
        p.product_line,
        p.product_family,
        p.therapy_area,
        p.business_unit,
        p.disease_category,

        -- Sale + warranty
        s.sale_date,
        s.warranty_start_date,
        s.warranty_end_date,
        s.sale_amount,

        -- Install tracking
        s.hardware_install_date,
        s.software_install_date,
        p.requires_hw_install,
        p.requires_sw_install,

        -- Service history
        ls.last_service_opened_at,
        coalesce(ls.total_service_tickets_lifetime, 0) as total_service_tickets_lifetime

    from sales s
    left join products p
        on s.material_id = p.material_id
    left join last_service_per_device ls
        on s.device_serial_number = ls.device_serial_number

),

flags as (

    select
        *,

        -- Active-instrument rule: has this device received service in the last 18 months?
        case
            when last_service_opened_at is null then false
            when last_service_opened_at >= dateadd(month, -18, current_date) then true
            else false
        end as is_currently_active,

        -- Days since last service (null if never serviced)
        case
            when last_service_opened_at is null then null
            else datediff(day, last_service_opened_at, current_date)
        end as days_since_last_service,

        -- Warranty status today
        case
            when warranty_end_date >= current_date then true
            else false
        end as is_in_warranty_today,

        -- Days remaining on warranty (negative if expired)
        datediff(day, current_date, warranty_end_date) as warranty_days_remaining,

        -- Install completion status
        case
            when requires_hw_install = false and requires_sw_install = false then 'not_required'
            when requires_hw_install = true and hardware_install_date is null then 'hw_pending'
            when requires_sw_install = true and software_install_date is null then 'sw_pending'
            when requires_hw_install = true
                and requires_sw_install = true
                and hardware_install_date is not null
                and software_install_date is not null then 'complete'
            when requires_hw_install = true and hardware_install_date is not null
                and requires_sw_install = false then 'complete'
            when requires_sw_install = true and software_install_date is not null
                and requires_hw_install = false then 'complete'
            else 'unknown'
        end as install_completion_status

    from joined

)

select * from flags
  );

