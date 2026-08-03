
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    field_engineer_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_field_engineer
where field_engineer_sk is not null
group by field_engineer_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test