
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        tier as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_customer
    group by tier

)

select *
from all_values
where value_field not in (
    'Tier 1','Tier 2','Tier 3'
)



  
  
      
    ) dbt_internal_test