
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select field_engineer_sk as from_field
    from ANALYTICS.DBT_BHAVANA.fct_service_tickets
    where field_engineer_sk is not null
),

parent as (
    select field_engineer_sk as to_field
    from ANALYTICS.DBT_BHAVANA.dim_field_engineer
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test