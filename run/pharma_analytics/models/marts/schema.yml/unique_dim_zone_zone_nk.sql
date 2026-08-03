
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    zone_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_zone
where zone_nk is not null
group by zone_nk
having count(*) > 1



  
  
      
    ) dbt_internal_test