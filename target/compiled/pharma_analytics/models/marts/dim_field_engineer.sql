

/*
  dim_field_engineer
  ------------------
  Field engineer dimension. Filtered from the unified USER table by role.
  Grain: one row per field engineer.
*/

with source as (

    select *
    from ANALYTICS.DBT_BHAVANA.stg_salesforce__user
    where user_role = 'Field Engineer'

),

final as (

    select
        -- Surrogate key
        md5(user_id)                    as field_engineer_sk,

        -- Natural keys
        user_id                         as field_engineer_nk,
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
        hourly_cost_rate,

        -- Metadata
        created_at,
        updated_at

    from source

)

select * from final