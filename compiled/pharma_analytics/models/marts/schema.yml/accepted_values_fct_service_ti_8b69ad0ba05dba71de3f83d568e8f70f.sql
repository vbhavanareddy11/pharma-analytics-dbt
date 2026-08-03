
    
    

with all_values as (

    select
        priority as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.fct_service_tickets
    group by priority

)

select *
from all_values
where value_field not in (
    'Critical','High','Medium','Low'
)


