
    
    

select
    device_serial_number as unique_field,
    count(*) as n_records

from RAW.SALESFORCE.opportunity
where device_serial_number is not null
group by device_serial_number
having count(*) > 1


