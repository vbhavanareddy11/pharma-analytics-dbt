
    
    

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


