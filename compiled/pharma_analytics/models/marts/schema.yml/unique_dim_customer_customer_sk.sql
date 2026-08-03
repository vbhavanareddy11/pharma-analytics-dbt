
    
    

select
    customer_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_customer
where customer_sk is not null
group by customer_sk
having count(*) > 1


