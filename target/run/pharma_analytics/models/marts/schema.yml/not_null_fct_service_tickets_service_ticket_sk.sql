
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select service_ticket_sk
from ANALYTICS.DBT_BHAVANA.fct_service_tickets
where service_ticket_sk is null



  
  
      
    ) dbt_internal_test