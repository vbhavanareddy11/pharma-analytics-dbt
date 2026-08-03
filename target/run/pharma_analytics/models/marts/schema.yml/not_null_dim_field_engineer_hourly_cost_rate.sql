
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select hourly_cost_rate
from ANALYTICS.DBT_BHAVANA.dim_field_engineer
where hourly_cost_rate is null



  
  
      
    ) dbt_internal_test