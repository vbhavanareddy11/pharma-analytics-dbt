
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.fct_service_tickets
    group by status

)

select *
from all_values
where value_field not in (
    'Open','In Progress','Resolved','Closed'
)


