
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_family
from ANALYTICS.DBT_BHAVANA.dim_product
where product_family is null



  
  
      
    ) dbt_internal_test