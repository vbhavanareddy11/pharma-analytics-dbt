
    
    

select
    device_serial_number as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.fct_sales
where device_serial_number is not null
group by device_serial_number
having count(*) > 1


