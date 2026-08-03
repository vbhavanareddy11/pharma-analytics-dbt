
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select zone_sk
from ANALYTICS.DBT_BHAVANA.dim_zone
where zone_sk is null



  
  
      
    ) dbt_internal_test