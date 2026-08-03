
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select business_unit
from ANALYTICS.DBT_BHAVANA.dim_product
where business_unit is null



  
  
      
    ) dbt_internal_test