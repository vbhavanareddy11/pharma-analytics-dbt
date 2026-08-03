
    
    

select
    distributor_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_distributor
where distributor_sk is not null
group by distributor_sk
having count(*) > 1


