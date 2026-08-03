
    
    

with all_values as (

    select
        service_tier as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_product
    group by service_tier

)

select *
from all_values
where value_field not in (
    'Standard','Premium'
)


