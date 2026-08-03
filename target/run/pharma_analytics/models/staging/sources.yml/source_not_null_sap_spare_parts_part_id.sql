
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select part_id
from RAW.SAP.spare_parts
where part_id is null



  
  
      
    ) dbt_internal_test