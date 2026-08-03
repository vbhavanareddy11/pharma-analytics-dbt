
    
    

select
    customer_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_customer
where customer_nk is not null
group by customer_nk
having count(*) > 1


