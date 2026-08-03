
    
    

with child as (
    select sales_rep_sk as from_field
    from ANALYTICS.DBT_BHAVANA.fct_sales
    where sales_rep_sk is not null
),

parent as (
    select sales_rep_sk as to_field
    from ANALYTICS.DBT_BHAVANA.dim_sales_rep
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


