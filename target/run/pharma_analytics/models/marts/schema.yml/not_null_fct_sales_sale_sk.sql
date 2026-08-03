
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sale_sk
from ANALYTICS.DBT_BHAVANA.fct_sales
where sale_sk is null



  
  
      
    ) dbt_internal_test