
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    zone_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_zone
where zone_sk is not null
group by zone_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test