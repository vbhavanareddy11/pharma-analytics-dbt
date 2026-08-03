
    
    

select
    part_id as unique_field,
    count(*) as n_records

from RAW.SAP.spare_parts
where part_id is not null
group by part_id
having count(*) > 1


