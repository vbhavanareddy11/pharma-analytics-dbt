
    
    

select
    id as unique_field,
    count(*) as n_records

from RAW.SALESFORCE.case_part_usage
where id is not null
group by id
having count(*) > 1


