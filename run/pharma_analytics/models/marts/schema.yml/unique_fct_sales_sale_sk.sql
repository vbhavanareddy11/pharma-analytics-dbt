
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sale_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.fct_sales
where sale_sk is not null
group by sale_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test