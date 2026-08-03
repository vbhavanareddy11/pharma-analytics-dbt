
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    device_serial_number as unique_field,
    count(*) as n_records

from RAW.SALESFORCE.opportunity
where device_serial_number is not null
group by device_serial_number
having count(*) > 1



  
  
      
    ) dbt_internal_test