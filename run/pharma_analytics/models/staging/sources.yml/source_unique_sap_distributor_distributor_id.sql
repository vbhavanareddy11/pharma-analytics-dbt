
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    distributor_id as unique_field,
    count(*) as n_records

from RAW.SAP.distributor
where distributor_id is not null
group by distributor_id
having count(*) > 1



  
  
      
    ) dbt_internal_test