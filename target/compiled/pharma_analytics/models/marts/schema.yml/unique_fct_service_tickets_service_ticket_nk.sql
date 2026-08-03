
    
    

select
    service_ticket_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.fct_service_tickets
where service_ticket_nk is not null
group by service_ticket_nk
having count(*) > 1


