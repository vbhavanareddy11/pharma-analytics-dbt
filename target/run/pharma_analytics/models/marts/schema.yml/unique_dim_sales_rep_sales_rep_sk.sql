
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sales_rep_sk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_sales_rep
where sales_rep_sk is not null
group by sales_rep_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test