
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sale_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.fct_sales
where sale_nk is not null
group by sale_nk
having count(*) > 1



  
  
      
    ) dbt_internal_test