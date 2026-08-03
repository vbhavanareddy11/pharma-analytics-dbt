
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select therapy_area
from ANALYTICS.DBT_BHAVANA.dim_product
where therapy_area is null



  
  
      
    ) dbt_internal_test