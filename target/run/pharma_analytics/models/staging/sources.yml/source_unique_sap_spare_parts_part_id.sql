
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    part_id as unique_field,
    count(*) as n_records

from RAW.SAP.spare_parts
where part_id is not null
group by part_id
having count(*) > 1



  
  
      
    ) dbt_internal_test