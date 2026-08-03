
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sale_nk
from ANALYTICS.DBT_BHAVANA.fct_sales
where sale_nk is null



  
  
      
    ) dbt_internal_test