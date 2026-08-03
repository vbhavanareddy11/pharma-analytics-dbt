
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select device_serial_number
from RAW.SALESFORCE.opportunity
where device_serial_number is null



  
  
      
    ) dbt_internal_test