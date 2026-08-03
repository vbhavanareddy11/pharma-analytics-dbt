
  create or replace   view ANALYTICS.DBT_BHAVANA.stg_salesforce__user
  
  
  
  
  as (
    

with source as (

    select * from RAW.SALESFORCE.user

),

renamed as (

    select
        -- Keys
        id                    as user_id,
        employee_id,
        manager_id,

        -- Descriptive
        first_name,
        last_name,
        email,
        user_role,
        profile,

        -- Assignment
        assigned_zone,
        country,

        -- Employment
        hire_date,
        termination_date,
        is_active,

        -- Compensation
        base_salary_usd         as base_salary,
        hourly_cost_rate_usd    as hourly_cost_rate,
        commission_tier,

        -- Lifecycle
        is_deleted,

        -- Metadata
        created_date            as created_at,
        last_modified_date      as updated_at

    from source
    where is_deleted = false

)

select * from renamed
  );

