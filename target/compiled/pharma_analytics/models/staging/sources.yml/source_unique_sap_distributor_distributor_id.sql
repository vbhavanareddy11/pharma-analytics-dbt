
    
    

select
    distributor_id as unique_field,
    count(*) as n_records

from RAW.SAP.distributor
where distributor_id is not null
group by distributor_id
having count(*) > 1


