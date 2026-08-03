
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select field_engineer_sk
from ANALYTICS.DBT_BHAVANA.fct_service_tickets
where field_engineer_sk is null



  
  
      
    ) dbt_internal_test