
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    service_ticket_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.fct_service_tickets
where service_ticket_nk is not null
group by service_ticket_nk
having count(*) > 1



  
  
      
    ) dbt_internal_test