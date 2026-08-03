
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select distributor_sk
from ANALYTICS.DBT_BHAVANA.dim_distributor
where distributor_sk is null



  
  
      
    ) dbt_internal_test