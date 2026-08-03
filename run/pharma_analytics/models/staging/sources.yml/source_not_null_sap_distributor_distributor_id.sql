
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select distributor_id
from RAW.SAP.distributor
where distributor_id is null



  
  
      
    ) dbt_internal_test