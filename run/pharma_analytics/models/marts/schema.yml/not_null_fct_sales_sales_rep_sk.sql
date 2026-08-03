
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sales_rep_sk
from ANALYTICS.DBT_BHAVANA.fct_sales
where sales_rep_sk is null



  
  
      
    ) dbt_internal_test