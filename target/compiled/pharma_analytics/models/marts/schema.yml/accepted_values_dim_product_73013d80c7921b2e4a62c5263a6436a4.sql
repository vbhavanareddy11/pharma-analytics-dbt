
    
    

with all_values as (

    select
        disease_category as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_product
    group by disease_category

)

select *
from all_values
where value_field not in (
    'Diabetes','Respiratory','Cardiac','Renal','Oncology'
)


