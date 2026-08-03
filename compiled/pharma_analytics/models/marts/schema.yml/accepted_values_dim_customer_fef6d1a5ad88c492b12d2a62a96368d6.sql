
    
    

with all_values as (

    select
        customer_type as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_customer
    group by customer_type

)

select *
from all_values
where value_field not in (
    'Hospital','Hospital Chain','Clinic','Independent Distributor'
)


