
  create or replace   view ANALYTICS.DBT_BHAVANA.stg_salesforce__case
  
  
  
  
  as (
    

with source as (

    select * from RAW.SALESFORCE.case

),

renamed as (

    select
        -- Keys
        id                       as case_id,
        case_number,
        account_id,
        device_serial_number,
        owner_id                 as field_engineer_id,

        -- Descriptive
        subject,
        case_type,
        priority,
        status,
        resolution_code,
        ticket_channel,

        -- Warranty + billing
        is_in_warranty,
        is_billable_to_customer,

        -- Effort
        engineer_hours_logged,
        travel_hours_logged,

        -- Timeline
        opened_date,
        resolved_date,
        closed_date,

        -- Lifecycle
        is_deleted,

        -- Metadata
        created_date             as created_at,
        last_modified_date       as updated_at

    from source
    where is_deleted = false

)

select * from renamed
  );

