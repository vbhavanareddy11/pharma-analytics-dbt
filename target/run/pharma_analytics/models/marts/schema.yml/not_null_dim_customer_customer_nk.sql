
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_nk
from ANALYTICS.DBT_BHAVANA.dim_customer
where customer_nk is null



  
  
      
    ) dbt_internal_test