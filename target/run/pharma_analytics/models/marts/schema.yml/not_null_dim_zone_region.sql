
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select region
from ANALYTICS.DBT_BHAVANA.dim_zone
where region is null



  
  
      
    ) dbt_internal_test