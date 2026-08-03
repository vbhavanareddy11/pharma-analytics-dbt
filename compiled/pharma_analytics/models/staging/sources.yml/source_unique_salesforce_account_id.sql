
    
    

select
    id as unique_field,
    count(*) as n_records

from RAW.SALESFORCE.account
where id is not null
group by id
having count(*) > 1


