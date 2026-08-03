
  
    

create or replace transient table ANALYTICS.DBT_BHAVANA.dim_sales_rep
    
    
    
    as (

/*
  dim_sales_rep
  -------------
  Sales rep dimension. Filtered from the unified USER table by role.
  Grain: one row per sales rep.
*/

with source as (

    select *
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__user
    where user_role = 'Sales Rep'

),

final as (

    select
        -- Surrogate key
        md5(user_id)                    as sales_rep_sk,

        -- Natural keys
        user_id                         as sales_rep_nk,
        employee_id,

        -- Descriptive
        first_name,
        last_name,
        first_name || ' ' || last_name  as full_name,
        email,

        -- Assignment
        assigned_zone,
        country,
        manager_id,

        -- Employment
        hire_date,
        termination_date,
        is_active,

        -- Compensation
        base_salary,
        commission_tier,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from final
    )
;


  