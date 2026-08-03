
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    distributor_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_distributor
where distributor_nk is not null
group by distributor_nk
having count(*) > 1



  
  
      
    ) dbt_internal_test