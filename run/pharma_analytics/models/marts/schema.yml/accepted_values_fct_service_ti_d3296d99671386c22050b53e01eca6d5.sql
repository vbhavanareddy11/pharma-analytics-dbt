
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        case_type as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.fct_service_tickets
    group by case_type

)

select *
from all_values
where value_field not in (
    'Hardware Failure','Software Issue','Calibration','Preventive Maintenance','User Training'
)



  
  
      
    ) dbt_internal_test