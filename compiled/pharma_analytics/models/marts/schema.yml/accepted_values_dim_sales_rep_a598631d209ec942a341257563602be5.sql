
    
    

with all_values as (

    select
        commission_tier as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_sales_rep
    group by commission_tier

)

select *
from all_values
where value_field not in (
    'Tier A','Tier B','Tier C'
)


