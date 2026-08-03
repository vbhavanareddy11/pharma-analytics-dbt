
  create or replace   view ANALYTICS.DBT_BHAVANA.stg_salesforce__case_part_usage
  
  
  
  
  as (
    

with source as (

    select * from RAW.SALESFORCE.case_part_usage

),

renamed as (

    select
        -- Keys
        id                                    as case_part_usage_id,
        case_id,
        part_id,

        -- Quantity + economics
        quantity,
        unit_cost_at_time_of_use_usd          as unit_cost_at_use,
        unit_price_charged_to_customer_usd    as unit_price_charged,

        -- Lifecycle
        is_deleted,

        -- Metadata
        created_date                          as created_at,
        last_modified_date                    as updated_at

    from source
    where is_deleted = false

)

select * from renamed
  );

