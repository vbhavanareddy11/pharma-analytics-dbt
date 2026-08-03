
    
    

select
    material_id as unique_field,
    count(*) as n_records

from RAW.SAP.material_master
where material_id is not null
group by material_id
having count(*) > 1


